"""Build a BM25 keyword index over the chunks, persist it, then test it."""
import pickle
from pathlib import Path
import pandas as pd
from rank_bm25 import BM25Okapi

df = pd.read_parquet("data/processed/chunks.parquet")
print(f"Loaded {len(df)} chunks.")

texts = df["text"].tolist()
tokenized = [t.lower().split() for t in texts]   # simple: lowercase + split on spaces

print("Building BM25 index...")
bm25 = BM25Okapi(tokenized)

out = {
    "bm25": bm25,
    "chunk_id": df["chunk_id"].tolist(),
    "doc_name": df["doc_name"].tolist(),
    "company": df["company"].tolist(),
    "text": texts,
}
Path("data/processed").mkdir(parents=True, exist_ok=True)
with open("data/processed/bm25.pkl", "wb") as f:
    pickle.dump(out, f)
print("Saved to data/processed/bm25.pkl\n")

for q in ["What are the main risks the company faces?",
          "capital expenditures property plant and equipment"]:
    scores = bm25.get_scores(q.lower().split())
    top = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:3]
    print(f"Test query: {q}\n")
    for rank, i in enumerate(top, 1):
        print(f"#{rank}  {df['doc_name'].iloc[i]}  (score {scores[i]:.2f})")
        print("   ", texts[i][:160].replace(chr(10), " "), "...\n")
    print("-" * 60)
