"""Show hybrid (BM25 + dense, fused with RRF) retrieval."""
from findoc_rag.retrieval.retriever import Retriever

r = Retriever()
for q in ["What are the main risks the company faces?",
          "capital expenditures property plant and equipment"]:
    print("=" * 70)
    print("Q:", q, "\n")
    for rank, rec in enumerate(r.retrieve(q, top_k=10)[:5], 1):
        print(f"#{rank}  {rec['doc_name']}")
        print("   ", rec["text"][:150].replace(chr(10), " "), "...\n")
