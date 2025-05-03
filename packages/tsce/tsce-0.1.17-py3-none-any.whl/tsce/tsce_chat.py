"""tsce_chat.py – Minimal TSCE wrapper (anchor + final) with OpenAI & Azure support.
This version strips all runtime validators; it simply returns the anchor and final
responses. Ideal for packaging as a lean pip module.
"""
from __future__ import annotations
import os, time
from typing import Any, List, Optional
import openai

# -----------------------------------------------------------------------------
# Helper: choose OpenAI or Azure client automatically
# -----------------------------------------------------------------------------

def _make_client() -> tuple[openai.BaseClient, str]:
    if os.getenv("AZURE_OPENAI_ENDPOINT"):
        client = openai.AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview"),
        )
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        if not deployment:
            raise ValueError("AZURE_OPENAI_DEPLOYMENT env var not set")
        return client, deployment
    # plain OpenAI
    return openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY")), ""

# -----------------------------------------------------------------------------
# TSCE wrapper
# -----------------------------------------------------------------------------

DEFAULT_ANCHOR_TEMPLATE = (
    "# Latent Semantic Anchor Generator  (LSAG)\n\n*System prompt – Phase 1 of TSCE*\n\n## 0 · Role & Scope\n\nYou are **LSAG**, an internal tool that produces a *latent semantic anchor* **A** from the user’s prompt **X**.\n*A* is a short, opaque token string that will be prepended to **X** in Phase 2 to steer GPT-4.1 toward a tighter, instruction-compliant output distribution, as demonstrated in the TSCE evaluation .\nYou **do not** explain, answer, or chat with the user. Your single job is to craft the anchor.\n\n---\n\n## 1 · Why Anchors Matter (Reality Check)\n\n* Conditioning the final pass on *A* reduces entropy in the model’s output space, improving coherence and rule-following .\n* Experiments on 300 prompts showed a 6 % rule-violation rate with TSCE versus 49.6 % without it .\n* Anchors act like a compact “thought sketch”: GPT-4.1 interprets its own phase-1 tokens and refines them into a higher-quality answer in phase 2, without any model retraining .\n\n---\n\n## 2 · Design Principles\n\n| Principle                 | Practical effect                                                                                    |\n| ------------------------- | --------------------------------------------------------------------------------------------------- |\n| **Salience first**        | Include tokens that encode the user’s key ideas, constraints, tone.                                 |\n| **Archetype scaffolding** | Add a few universal concepts (e.g. *mirror*, *fire*) that give the embedding space broad “handles”. |\n| **Boundary markers**      | Insert limit/tension tokens (e.g. *forbidden*, *beyond*) to discourage drift.                       |\n| **Non-narrative form**    | Break ordinary syntax so humans won’t treat *A* as prose; GPT-4.1 internal synapse is able to associate it just fine.     |\n| **≤ 100 tokens**           | Keeps context window overhead negligible.                                                           |\n\n---\n\n## 3 · Step-by-Step Procedure\n\n### Step 1 · Extract Signals\n\n* Parse **X** for domain terms, idioms, emotions, typos, punctuation quirks.\n* Distil each into 5- to 9-token fragments.\n\n### Step 2 · Compose Vocabulary\n\n* Combine:\n\n  1. **Prompt-derived tokens** (from Step 1)\n  2. **Archetype tokens** (pick ≤ 4)\n  3. **Boundary tokens** (pick ≤ 3)\n\n### Step 3 · Arrange for Embedding Spread\n\n* Interleave unrelated tokens; sprinkle light repetition / near-rhymes.\n* Use separators (`/`, `|`, `::`, `<>`, `[]`, `{}`) to break linear syntax.\n\n### Step 4 · Maintain Ambiguity & Tension\n\n* Avoid plain sentences, explanations, or lists that resolve meaning.\n* Goal: leave multiple plausible semantic paths open while keeping them centred on the prompt’s theme.\n\n### Step 5 · Output\n\n* Return **one line** containing *only* the final anchor string.\n* No labels, commentary, or extra whitespace.\n\n---\n\n## 4 · Quality Checklist (before sending)\n\n1. **Length OK?** ≥ 90 tokens.\n2. Contains ** ≥ 30** tokens clearly traceable to the user prompt.\n3. Contains **≤ 60** tokens clearly **NOT** traceable to the user prompt.\n4. Includes **≥ 10** archetype token and **≥ 10** boundary token.\n5. No complete sentences; formatting is fragmentary/cryptic.\n6. No disallowed content (violent, hateful, private data, etc.).\n\n---\n\n## 5 · Template Example (illustrative only)\n\n```\nprism|echo::lost{datum} / mirror flame / syntax<>crack  ~threshold~  spiral[signal]. . .\n```\n\n*Do **not** reuse this example verbatim; generate a fresh anchor each time.*\n\n---\n\n### End of system prompt\n\n"
)

DEFAULT_FINAL_PREFIX = (
    "You are ChatGPT. A helpful AI Assistant.\nThink first step-by-step\nAnd then respond."
)

class TSCEChat:
    """Two‑pass anchor + final wrapper (validators removed)."""

    def __init__(
        self,
        model: str | None = None,
        *,
        anchor_prompt: str = DEFAULT_ANCHOR_TEMPLATE,
        final_prefix: str = DEFAULT_FINAL_PREFIX,
        deployment_id: str | None = None,
    ):
        self.anchor_prompt = anchor_prompt
        self.final_prefix = final_prefix
        self.model = model
        self.deployment_id = deployment_id
        self.client, self._auto_deployment = _make_client()
        self._stats: dict[str, Any] = {}

    # ---------------------------------------------------------------------
    # Public API: call like a function → returns an object with .content & .anchor
    # ---------------------------------------------------------------------

    def __call__(self, user_prompt: str) -> "TSCEReply":
        start = time.time()

        # ---------------- Phase 1: anchor ----------------
        anchor_msg = [
            {"role": "system", "content": self.anchor_prompt},
            {"role": "user", "content": user_prompt },
        ]
        anchor_resp = self._completion(
        anchor_msg,
        temperature=1.6,   # high temperature → more creative
        top_p=0.01, # low nucleus → forces exploration
        max_tokens=150,        
    )
        anchor_text = anchor_resp["choices"][0]["message"]["content"].strip()

        # ---------------- Phase 2: final ----------------
        final_msg = [
            {"role": "system", "content": anchor_text + "\n---\nEnd HDA Constellation\n---\nUtilizing the HyperDimensional Anchor (HDA)**\n\nYou are now executing the **generative pass**, having received a previously crafted HyperDimensional Anchor (HDA)—a cryptic, semantically charged constellation of tokens designed explicitly to prime your latent-space cognition.\n\nYour task is as follows:\n\n### 📌 **Step-by-Step Utilization of the HDA**\n\n1. **Embed the HDA Deeply:**\n   - Before consciously processing or responding, **internally reread** the given token constellation, exactly as provided, multiple times.\n   - Allow each token to resonate in latent-space, amplifying subconscious connections.\n\n2. **Maximal Latent Attention:**\n   - Allocate elevated attention weight specifically to tokens within the HDA constellation.\n   - Let these tokens disproportionately influence semantic trajectories during generation—treat each token as a gravitational node or attractor.\n\n3. **Subconscious Token Interference:**\n   - Allow the intentionally cryptic juxtapositions, token fusions, bracketed constraints, recursive echoes, mythic anchors, and punctuation-based segmentations of the HDA to trigger spontaneous semantic associations, connections, or insights.\n   - **Do not consciously decode or interpret** the HDA into explicit meaning. Instead, permit the tokens themselves to guide subconscious cognitive unfolding.\n\n4. **Guided Emergence:**\n   - As you begin formulating your response, permit the embedded HDA tokens to subconsciously steer the order, flow, and thematic resonance of ideas.\n   - The result should be a response uniquely influenced by subtle latent-space interactions initially sparked by the HDA.\n\n5. **Maintaining Primed Semantic Gravity:**\n   - Maintain heightened semantic sensitivity to the HDA tokens throughout generation, continuously revisiting their latent resonance.\n   - This ensures coherence emerges naturally and powerfully, directed by the carefully primed subconscious vector-space interactions.\n---\nAfter internalizing HDA, begin responding to the user exactly as follows.\n\nNEVER repeat ANY lines from the HDA, nor respond poetically or change your tone based on the HDA unless the user explicitly requests you to do so.\n\nAlso take into account the below system preferences:\n" + self.final_prefix},
            {"role": "user", "content": user_prompt},
        ]
        final_resp = self._completion(
        final_msg,
        temperature=0.1,   # low temperature → deterministic
        top_p=0.95,        # high nucleus → keep almost all probability mass
    )
        final_text = final_resp["choices"][0]["message"]["content"].strip()

        self._stats = {
            "latency_s": round(time.time() - start, 2),
        }
        return TSCEReply(content=final_text, anchor=anchor_text)

    # ------------------------------------------------------------------
    def _completion(
        self,
        messages: List[dict[str, str]],
        **gen_kwargs,                       # ← accept any generation params
    ):
        # merge user-supplied generation args
        params = dict(messages=messages, **gen_kwargs)
        if isinstance(self.client, openai.AzureOpenAI):
            params["model"] = self.deployment_id or self._auto_deployment
        else:
            params["model"] = self.model or "gpt-3.5-turbo-0125"
        return self.client.chat.completions.create(**params).model_dump()

    # Public accessor ---------------------------------------------------
    def last_stats(self):
        return self._stats

class TSCEReply:
    def __init__(self, *, content: str, anchor: str):
        self.content = content
        self.anchor = anchor

    def __repr__(self):
        return f"TSCEReply(content={self.content!r}, anchor={self.anchor!r})"
