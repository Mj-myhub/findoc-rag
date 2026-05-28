"""Answer generation.  [PHASE 2 — Week 6]

Sends the question plus retrieved chunks to an LLM and returns a grounded,
cited answer — or an explicit abstention when the context is insufficient.
Not yet implemented — see ROADMAP.md, Week 6.
"""

from __future__ import annotations

# The system prompt is the heart of this module. Refine it during Week 6.
SYSTEM_PROMPT = """You are a financial-document assistant.
Answer the user's question using ONLY the provided context passages.
Rules:
- Cite the passage(s) you used, by their chunk id.
- If the context does not contain the answer, reply exactly:
  "I cannot find this in the filings."
- Do not use outside knowledge. Do not guess."""


def generate_answer(question: str, chunks: list) -> dict:
    """Generate a cited answer from retrieved chunks.

    TODO (Week 6):
      - Format the retrieved chunks (with their ids) into the prompt.
      - Call the Groq API (model from config/settings.yaml, GROQ_API_KEY from .env).
      - Return a dict: {"answer": str, "citations": list, "abstained": bool}.
    """
    raise NotImplementedError("Phase 2, Week 6 — implement generation. See ROADMAP.md")
