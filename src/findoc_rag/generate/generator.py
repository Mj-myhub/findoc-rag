"""Answer generation.  [PHASE 2 - Week 6]

Sends the question plus retrieved chunks to an LLM and returns a grounded,
cited answer - or an explicit abstention when the context is insufficient.
"""

from __future__ import annotations

from groq import Groq

from findoc_rag.config import GROQ_API_KEY, SETTINGS

SYSTEM_PROMPT = """You are a financial-document assistant.
Answer the user's question using ONLY the provided context passages.
Rules:
- Cite the passage(s) you used, by their chunk id.
- If the context does not contain the answer, reply exactly:
  "I cannot find this in the filings."
- Do not use outside knowledge. Do not guess."""


def generate_answer(question: str, chunks: list, client: Groq | None = None) -> dict:
    """Generate a cited answer from retrieved chunks."""
    if client is None:
        client = Groq(api_key=GROQ_API_KEY)

    context = "\n\n".join(
        f"[{c['chunk_id']}] (from {c['doc_name']})\n{c['text']}" for c in chunks
    )
    user_prompt = f"Context passages:\n\n{context}\n\nQuestion: {question}"

    gen = SETTINGS["generation"]
    resp = client.chat.completions.create(
        model=gen["model"],
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=gen["temperature"],
        max_tokens=gen["max_tokens"],
    )
    answer = resp.choices[0].message.content.strip()

    abstained = "cannot find this in the filings" in answer.lower()
    citations = [c["chunk_id"] for c in chunks if c["chunk_id"] in answer]

    return {"answer": answer, "citations": citations, "abstained": abstained}
