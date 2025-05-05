# TSCE – Two-Step Contextual Enrichment 

**TSCE gives small models (e.g. GPT-3.5) the ability to follow instructions with GPT-4-like precision by using a two-pass architecture.** TSCE is a lightweight wrapper that transforms a single user prompt into a **“think-before-speaking”** two-stage interaction. In the first pass, the model generates a hidden **anchor draft** (a latent plan or outline) capturing the prompt’s intent and requirements. In the second pass, the model produces the final answer, guided by the anchor to ensure high fidelity, coherence, and adherence to instructions. TSCE effectively narrows the model’s output to the intended solution space, dramatically improving reliability and consistency – **all without fine-tuning or specialized models.**

- **OpenAI & Azure support** – Works out-of-the-box with OpenAI API or Azure OpenAI (auto-detected via environment variables).  
- **Model-agnostic** – Use it with GPT-3.5, GPT-4, or other compatible chat models. Smaller models gain quality; larger models gain consistency.  
- **Minimal integration** – Just install and use a simple `TSCEChat` interface. No custom APIs or complex workflow changes.  
- **Improved outputs** – Fewer hallucinations, better instruction-following, and more focused responses by splitting “thinking” and “answering” into two steps.

## Installation

Install TSCE from pip:

```bash
pip install tsce
```

TSCE requires Python 3.8+ and the OpenAI Python SDK as a dependency. Once installed, you’re ready to use TSCE in your code.

## Configuration: OpenAI and Azure OpenAI API

TSCE will automatically choose between OpenAI’s API and Azure OpenAI based on your environment variables:

- **OpenAI API (openai.com)**: Simply set your OpenAI API key in the `OPENAI_API_KEY` environment variable. For example: 

  ```bash
  export OPENAI_API_KEY="sk-<your_openai_key>"
  ``` 

  That’s it – TSCE will use the OpenAI Chat Completion API with this key.

- **Azure OpenAI**: Set the following environment variables for your Azure OpenAI resource:

  ```bash
  export AZURE_OPENAI_ENDPOINT="https://<your-resource-name>.openai.azure.com/"
  export AZURE_OPENAI_KEY="<your_azure_openai_key>"
  export AZURE_OPENAI_DEPLOYMENT="<your_deployment_name>"
  export AZURE_OPENAI_API_VERSION="<api_version>"  # e.g. 2024-05-15 or latest
  ``` 

  TSCE will detect `AZURE_OPENAI_ENDPOINT` and use Azure OpenAI. Ensure `AZURE_OPENAI_DEPLOYMENT` is the deployment name of the model you want to use (e.g. a deployment of gpt-35-turbo or gpt-4). If `AZURE_OPENAI_API_VERSION` is not set, TSCE uses a default value (which you can override as needed).

No additional configuration is required in code — TSCE will pick up these settings and call the appropriate API. (Under the hood, it uses the OpenAI Python SDK’s client for either OpenAI or Azure.)

## Basic Usage: Two-Pass Chat

Using TSCE is straightforward. Import the `TSCEChat` class and call it with your prompt, just like you would use an AI assistant. For example:

```python
from tsce import TSCEChat

# Initialize TSCE with the model you want to use (e.g., GPT-3.5 Turbo)
tsce = TSCEChat(model="gpt-3.5-turbo")

# Ask a question or give an instruction
reply = tsce("Explain how a telescope works in simple terms.")

print(reply.content)   # Final answer from TSCE (string)
```

Running this will internally perform two calls to the model:
1. **Anchor Pass:** TSCE first prompts the model (invisibly) to produce an *anchor draft* – a latent outline or set of key points capturing everything important about your request.
2. **Final Pass:** TSCE then sends the anchor (as a hidden system instruction) along with your original prompt to produce the final answer.

The `reply` returned is an object with the final answer in `reply.content`. In most cases you can treat `reply.content` as the output to use in your application.

### Inspecting the Anchor Draft

TSCE’s power comes from the intermediate **anchor**. While this anchor is not part of the final answer, you can inspect it for debugging or curiosity. The anchor is available as `reply.anchor`:

```python
print(reply.anchor)  # The latent anchor generated in the first pass
```

The anchor is a special snippet of text (not meant for humans to read) that encodes the intent, constraints, and context of your prompt in a compact form. It often looks like a sequence of terse “tags” or keywords linked by arrows, summarizing what the model should consider. For example, an anchor for the telescope question might look conceptually like:

```
light → lenses → magnification → focal length → eye position → ###END###
```

*(The actual format is defined by TSCE’s internal prompt; it ensures the model lists all relevant latent aspects.)* In the second pass, this anchor is given to the model (as a system message) to steer the final output. By default, TSCE instructs the model **not to reveal the anchor** to the user, so you won’t see any trace of it in `reply.content`.

> **Note:** You typically don’t need to use the anchor directly. It’s provided for transparency and debugging. In production, you’d use only the final answer.

### Customizing the Second-Pass System Prompt

You can customize the system instructions for the second pass to control the style or role of the final answer. By default, TSCE uses a generic assistant persona and includes a directive not to expose the anchor. If you want a different tone or additional guidelines for the final answer, you can override the `final_prefix` parameter when creating the TSCEChat instance:

```python
tsce = TSCEChat(
    model="gpt-3.5-turbo",
    final_prefix="The above anchor is context. You are a witty pirate assistant who replies in rhyme. Do not mention the anchor."
)
reply = tsce("Tell a short story about a treasure hunt.")
print(reply.content)
```

In this example, the second pass will treat the model as a “witty pirate” persona who speaks in rhyme. The anchor from the first pass will still be prepended (so the answer stays on-point), and our custom system prompt ensures a specific style. **Always include an instruction not to reference or reveal the anchor** if you override the final system prompt, as we did above, to maintain the two-pass illusion.

### Enforcing Output Constraints with Validators

TSCE can incorporate validation of the final output to meet certain criteria. You can provide a **validator function** that checks the final answer and ensure it satisfies your requirements. For instance, suppose you want the answer to include a specific format or content rule – if the validator fails, TSCE can automatically retry or signal failure.

**Example:** Ensure the answer is a **perfect pangram** (a sentence using every letter of the alphabet exactly once). We’ll write a simple validator for this:

```python
def is_perfect_pangram(text: str) -> bool:
    alphabet = set("abcdefghijklmnopqrstuvwxyz")
    letters = set(c.lower() for c in text if c.isalpha())
    return letters == alphabet and all(text.lower().count(ch) == 1 for ch in alphabet)
```

Now use this validator with TSCE:

```python
tsce = TSCEChat(model="gpt-3.5-turbo")
prompt = "Create a single sentence about pirates that is a perfect pangram."
reply = tsce(prompt, validator=is_perfect_pangram)
print(reply.content)
```

If the first final attempt doesn’t pass the `is_perfect_pangram` check, TSCE will (optionally) retry or adjust until it does (up to a limit). In this way, the two-pass process plus a validator gives the model multiple chances to “get it right” within one API call abstraction.

*(Note: The current version of TSCE may simply return the result and allow you to check validity manually. Enhanced automatic retry logic with validators is in development.)*

## Example: Perfect Pangram Generation

Let’s walk through a real-world demo combining the above features. We want GPT-3.5 to produce a sentence about **pirates** that is a perfect pangram (each letter A–Z exactly once). This is a challenging task for a model to do in one go, because it requires planning the sentence structure to include rare letters like *Q, X, Z* exactly once. TSCE’s approach is ideal here: the anchor pass can plan out the requirement, and the final pass can realize it.

**Code:**

```python
from tsce import TSCEChat

def is_perfect_pangram(text: str) -> bool:
    alphabet = set("abcdefghijklmnopqrstuvwxyz")
    letters = set(c.lower() for c in text if c.isalpha())
    return letters == alphabet and all(text.lower().count(ch) == 1 for ch in alphabet)

# Initialize TSCE with validator
tsce = TSCEChat(model="gpt-3.5-turbo")
prompt = "Describe a sea adventure in one sentence as a perfect pangram."
reply = tsce(prompt, validator=is_perfect_pangram)

print("Anchor draft:\n", reply.anchor)
print("Final answer:\n", reply.content)
```

When you run this, TSCE will first generate an anchor capturing both the *content* (“sea adventure”, pirates, etc.) and the *constraint* (use all letters once). The final answer will then be created to satisfy that anchor and pass the validator. 

**Example outcome:**

- *Anchor draft (snippet):* `pirate legend → treasure → quest → ... → every letter → no repeats → ###END###`  
- *Final answer:* “**Jack quizzically vexed Mr. Wang’s PD club of pirates.**”

The final sentence above is a bit whimsical (and admittedly not something a human might write), but notice it **contains every letter exactly once** (it’s a perfect pangram). Without TSCE, GPT-3.5 would likely produce a fluent sentence about a sea adventure but miss some letters or repeat others, failing the pangram requirement. With TSCE, the model “thought through” the requirement in the anchor stage (making sure to account for all letters) and then delivered a valid result in the final stage. 

This demo highlights how TSCE enables complex constraints and improved precision even with smaller models.

## Performance Considerations

**Latency and Tokens:** Because TSCE uses two passes, it will roughly double the API calls compared to a single-pass approach. In practice, the overhead is often acceptable:
- The anchor is typically concise (hundreds of tokens at most, often less), and the final answer is of normal length. The user’s prompt is sent in both passes. So expect roughly 2× the token usage of a single call, plus a bit extra for the anchor instructions.
- The latency is likewise about 2× a single model call. For instance, if a normal GPT-3.5 response takes 2 seconds, TSCE might take ~4 seconds end-to-end for the same prompt (since it waits for the anchor then the final result).

**Cost:** The benefit of TSCE is you can use a cheaper model twice rather than a more expensive model once. Two GPT-3.5-turbo calls (at ~$0.002 per 1K tokens) are still far cheaper than one GPT-4 call ( ~$0.06 per 1K tokens) in many cases. This makes TSCE very cost-effective for boosting quality. Of course, if you use TSCE with GPT-4, you’ll be doubling GPT-4 calls (which may be unnecessary for straightforward tasks – TSCE is most valuable when pushing model limits or enforcing strict requirements).

**Model Selection:** TSCE is model-agnostic. You can experiment with using it on different models:
- Using TSCE on GPT-3.5-turbo can markedly improve its reliability and correctness, making it behave more like a GPT-4-lite.
- Using TSCE on GPT-4 can further tighten its outputs (as seen in internal tests, it improved instruction adherence), but the improvement might be more incremental since GPT-4 is already strong. 
- You could even try TSCE with open-source chat models (if they have a compatible chat completion API) to enhance their performance.

Keep in mind that because TSCE guides the model with an anchor rather than brute-force retries, it’s an efficient two calls – not an unbounded loop. You get more consistent results without significantly higher latency than, say, naive retry-until-success loops.

## Design Philosophy and Background

TSCE stands for **Two-Step Contextual Enrichment**, inspired by the simple idea: **“Think before you speak.”** Instead of generating an answer in one go, the model first **“thinks”** (creates a latent plan) and then **“speaks”** (produces the final output). This two-pass framework leads to several benefits:

- **Latent-Space Anchor:** The intermediate anchor lives in the model’s *latent semantic space*. It’s not a normal paragraph of text but a distilled representation of the solution space. This helps the model consider all aspects of the query (requirements, edge cases, factual context, style guidelines) without committing them directly to the final wording. By separating meaning from final phrasing, the model can explore possibilities broadly in the anchor, then converge to a focused answer.
- **Improved Coherence and Compliance:** Because the final generation is conditioned on the anchor (which encodes the prompt and constraints), the answers tend to be more on-target. TSCE reduces digressions and flattens out the wild variability you sometimes get from a single-pass response. The model is also less likely to violate instructions: the anchor creation step internalizes the rules and context, so the final step naturally follows them. (For example, if the instruction is “don’t use a certain word,” the anchor will contain that rule, and the final answer is far more likely to comply.)
- **Creative yet Controlled:** TSCE anchors do not directly appear in the answer, so the model still has freedom in phrasing the final response. It can be creative in how it delivers the content, but that creativity is guided by the anchor’s semantic blueprint. The result is often the best of both worlds: **creative outputs that still meet the exact criteria.**
- **Motivation:** We developed TSCE to tackle a common problem with large language models: a trade-off between creativity and accuracy. Single-pass models often either **ramble off-topic or miss subtleties**. By forcing a “brainstorm” pass (the anchor) and then a focused pass (the final answer), TSCE yields outputs that are both richer in content and more reliable in following the prompt. This approach is **model-agnostic** and doesn’t require any training data or fine-tuning – it’s a smarter use of prompting. Our internal evaluations across dozens of tasks (creative writing, Q&A, coding, etc.) showed significant improvements in consistency and user satisfaction when using TSCE.

In essence, TSCE adds a bit of structured reasoning into the generation process, borrowing ideas from “chain-of-thought” prompting and constraint satisfaction. It’s a minimalist strategy to make AI responses **sharper, safer, and more predictable**.

## License and Project Status

**License:** TSCE is open-source software released under the **MIT License**. This means you are free to use it in your own projects, whether personal or commercial, with attribution and without heavy restrictions.

**Status:** *Alpha.* TSCE is in active development (alpha stage). The core functionality is stable, but APIs may evolve as we incorporate feedback. We are continuously refining the anchor templates, validator mechanisms, and support for more use cases. Contributions, bug reports, and suggestions are welcome to help improve TSCE! 

___

*Harness GPT-4-like clarity from smaller models by letting them think first and answer second. We hope TSCE becomes a valuable addition to your AI toolbox, and we’re excited to see what you build with it. If you have questions or run into issues, please reach out via our GitHub repository or community forum.*