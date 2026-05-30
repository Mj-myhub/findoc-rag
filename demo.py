"""Gradio demo for FinDocRAG.  [PHASE 4 - Week 10]"""
from __future__ import annotations

import gradio as gr

from findoc_rag.generate.generator import generate_answer
from findoc_rag.retrieval.retriever import Retriever

print("Loading retriever...")
retriever = Retriever()
print("Ready.")


def ask(question: str) -> tuple[str, str]:
    if not question.strip():
        return "Please type a question.", ""
    chunks = retriever.retrieve(question)
    result = generate_answer(question, chunks)
    sources = "\n".join(f"• {c}" for c in result["citations"]) or "None"
    return result["answer"], sources


demo = gr.Interface(
    fn=ask,
    inputs=gr.Textbox(
        label="Question",
        placeholder="Ask about any of the 15 filings (AMD, Boeing, 3M, PepsiCo...).",
    ),
    outputs=[
        gr.Textbox(label="Answer", lines=8),
        gr.Textbox(label="Sources cited", lines=3),
    ],
    title="FinDocRAG — Financial Document Q&A",
    description=(
        "Answers are grounded in 15 SEC 10-K filings. "
        "The system cites its sources and says 'I cannot find this' rather than guessing."
    ),
    examples=[
        ["What are AMD's main business risks?"],
        ["Has CVS Health paid dividends to shareholders?"],
        ["Is Boeing's business subject to cyclicality?"],
        ["What is the capital of France?"],
    ],
)

if __name__ == "__main__":
    demo.launch()
