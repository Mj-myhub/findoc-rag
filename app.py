"""FinDocRAG - Hugging Face Spaces entry point."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import gradio as gr  # noqa: E402

from findoc_rag.generate.generator import generate_answer  # noqa: E402
from findoc_rag.retrieval.retriever import Retriever  # noqa: E402

print("Loading retriever...")
retriever = Retriever()
print("Ready.")


def ask(question: str):
    if not question.strip():
        return "Please type a question.", ""
    chunks = retriever.retrieve(question)
    result = generate_answer(question, chunks)
    sources = "\n".join(f"* {c}" for c in result["citations"]) or "None"
    return result["answer"], sources


demo = gr.Interface(
    fn=ask,
    cache_examples=False,
    inputs=gr.Textbox(
        label="Question",
        placeholder="Ask about the 15 filings (AMD, Boeing, 3M...).",
    ),
    outputs=[
        gr.Textbox(label="Answer", lines=8),
        gr.Textbox(label="Sources cited", lines=3),
    ],
    title="FinDocRAG - Financial Document Q&A",
    description=(
        "Grounded in 15 SEC 10-K filings. Cites sources; "
        "says 'I cannot find this' rather than guessing."
    ),
    examples=[
        ["What are AMD's main business risks?"],
        ["What is the FY2018 capital expenditure amount (in USD millions) for 3M?"],
        ["Has CVS Health paid dividends to shareholders?"],
        ["Is Boeing's business subject to cyclicality?"],
        ["What is the capital of France?"],
    ],
)

if __name__ == "__main__":
    demo.launch()
