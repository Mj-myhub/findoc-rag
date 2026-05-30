"""FastAPI app for FinDocRAG.  [PHASE 4 - Week 9]

Exposes one endpoint: POST /ask  -> grounded, cited answer (or abstention).
The Retriever is loaded once at startup, not per request.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from findoc_rag.generate.generator import generate_answer
from findoc_rag.retrieval.retriever import Retriever

state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading retriever (this takes a few seconds)...")
    state["retriever"] = Retriever()
    print("Ready.")
    yield


app = FastAPI(title="FinDocRAG", lifespan=lifespan)


class AskRequest(BaseModel):
    question: str
    top_k: int = 10


@app.get("/")
def root() -> dict:
    return {"status": "ok", "try": "POST /ask  body: {\"question\": \"...\"}  or open /docs"}


@app.post("/ask")
def ask(req: AskRequest) -> dict:
    r = state["retriever"]
    chunks = r.retrieve(req.question, top_k=req.top_k)
    result = generate_answer(req.question, chunks)
    return {
        "question": req.question,
        "answer": result["answer"],
        "citations": result["citations"],
        "abstained": result["abstained"],
        "chunks": [
            {"chunk_id": c["chunk_id"], "doc_name": c["doc_name"]} for c in chunks
        ],
    }
