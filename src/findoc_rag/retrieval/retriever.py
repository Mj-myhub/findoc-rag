"""Hybrid retrieval + reranking + LLM query expansion.  [v0.5.0]"""

from __future__ import annotations

import pickle

import chromadb
from chromadb.utils import embedding_functions
from groq import Groq
from sentence_transformers import CrossEncoder

from findoc_rag.config import GROQ_API_KEY, SETTINGS


def reciprocal_rank_fusion(rankings: list[list], k: int = 60) -> list:
    scores: dict = {}
    for ranking in rankings:
        for rank, item in enumerate(ranking, start=1):
            scores[item] = scores.get(item, 0.0) + 1.0 / (k + rank)
    return sorted(scores, key=scores.get, reverse=True)


_EXPAND_PROMPT = (
    "You convert a finance question into the exact line-item terminology used "
    "in SEC 10-K filings. For example 'capital expenditure' appears as "
    "'Purchases of property, plant and equipment'; 'revenue' often appears as "
    "'Net sales'. Reply with ONLY a short space-separated list of the most "
    "likely filing terms for the question - no explanation, no punctuation."
)


def expand_query(question: str, client: Groq) -> str:
    """Append likely 10-K line-item synonyms to a question to bridge vocab gaps."""
    resp = client.chat.completions.create(
        model=SETTINGS["generation"]["model"],
        messages=[
            {"role": "system", "content": _EXPAND_PROMPT},
            {"role": "user", "content": question},
        ],
        temperature=0,
        max_tokens=512,
        reasoning_effort="low",
    )
    extra = (resp.choices[0].message.content or "").strip()
    return f"{question} {extra}"


class Retriever:
    def __init__(self) -> None:
        model_name = SETTINGS["retrieval"]["dense_model"]
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)
        client = chromadb.PersistentClient(path="chroma")
        self.collection = client.get_collection("filings", embedding_function=ef)

        with open("data/processed/bm25.pkl", "rb") as f:
            data = pickle.load(f)
        self.bm25 = data["bm25"]
        self.ids = data["chunk_id"]
        self.text_by_id = dict(zip(data["chunk_id"], data["text"]))
        self.doc_by_id = dict(zip(data["chunk_id"], data["doc_name"]))

        self.rerank_model_name = SETTINGS["retrieval"]["rerank_model"]
        self.rerank_top_k = SETTINGS["retrieval"]["rerank_top_k"]
        self._reranker = None
        self._groq = None

    @property
    def reranker(self) -> CrossEncoder:
        if self._reranker is None:
            self._reranker = CrossEncoder(self.rerank_model_name)
        return self._reranker

    @property
    def groq(self) -> Groq:
        if self._groq is None:
            self._groq = Groq(api_key=GROQ_API_KEY)
        return self._groq

    def _as_record(self, chunk_id: str) -> dict:
        return {"chunk_id": chunk_id, "doc_name": self.doc_by_id.get(chunk_id, "?"),
                "text": self.text_by_id.get(chunk_id, "")}

    def _vector_search(self, query: str, k: int) -> list:
        return self.collection.query(query_texts=[query], n_results=k)["ids"][0]

    def _bm25_search(self, query: str, k: int) -> list:
        scores = self.bm25.get_scores(query.lower().split())
        top = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        return [self.ids[i] for i in top]

    def retrieve(self, question: str, top_k: int = 10, rerank: bool = True,
                 expand: bool = True) -> list:
        search_query = expand_query(question, self.groq) if expand else question
        dense = self._vector_search(search_query, top_k)
        sparse = self._bm25_search(search_query, top_k)
        fused = [self._as_record(cid) for cid in reciprocal_rank_fusion([dense, sparse])]
        if not rerank:
            return fused
        scores = self.reranker.predict([(question, c["text"]) for c in fused])
        for c, s in zip(fused, scores):
            c["rerank_score"] = float(s)
        fused.sort(key=lambda c: c["rerank_score"], reverse=True)
        return fused[: self.rerank_top_k]
