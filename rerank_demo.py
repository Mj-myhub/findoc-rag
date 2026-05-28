"""Compare hybrid retrieval with and without the reranker."""
from findoc_rag.retrieval.retriever import Retriever

r = Retriever()
q = "What are the main risks the company faces?"

print("WITHOUT reranker (hybrid only):\n")
for rank, rec in enumerate(r.retrieve(q, rerank=False)[:5], 1):
    print(f"#{rank}  {rec['doc_name']}:  {rec['text'][:110].replace(chr(10), ' ')} ...")

print("\nWITH reranker:\n")
for rank, rec in enumerate(r.retrieve(q, rerank=True), 1):
    print(f"#{rank}  {rec['doc_name']}  (score {rec['rerank_score']:.2f}):  {rec['text'][:110].replace(chr(10), ' ')} ...")
