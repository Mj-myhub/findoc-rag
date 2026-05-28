"""Compare hybrid retrieval with and without the reranker."""
from findoc_rag.retrieval.retriever import Retriever

r = Retriever()
q = "What are the main risks the company faces?"

print("WITHOUT reranker (hybrid only):\n")
for rank, rec in enumerate(r.retrieve(q, rerank=False)[:5], 1):
    preview = rec["text"][:110].replace(chr(10), " ")
    print(f"#{rank}  {rec['doc_name']}:  {preview} ...")

print("\nWITH reranker:\n")
for rank, rec in enumerate(r.retrieve(q, rerank=True), 1):
    preview = rec["text"][:110].replace(chr(10), " ")
    score = rec["rerank_score"]
    print(f"#{rank}  {rec['doc_name']}  (score {score:.2f}):  {preview} ...")
