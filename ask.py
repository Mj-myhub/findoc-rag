"""Ask FinDocRAG a question: retrieve, then generate a cited answer."""
import sys

from findoc_rag.generate.generator import generate_answer
from findoc_rag.retrieval.retriever import Retriever

question = sys.argv[1] if len(sys.argv) > 1 else \
    "What is the FY2018 capital expenditure amount (in USD millions) for 3M?"

print("Loading retriever...")
r = Retriever()
chunks = r.retrieve(question, top_k=10)

print(f"\nQuestion: {question}\n")
result = generate_answer(question, chunks)

print("Answer:")
print(result["answer"])
print(f"\nAbstained: {result['abstained']}")
print(f"Citations: {result['citations']}")
print("\n--- chunks given to the model ---")
for c in chunks:
    print(f"  [{c['chunk_id']}]  {c['doc_name']}")
