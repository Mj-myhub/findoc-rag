"""Build a persistent ChromaDB vector (meaning) index over the chunks, then test it."""
import pandas as pd
import chromadb
from chromadb.utils import embedding_functions

from findoc_rag.config import SETTINGS

df = pd.read_parquet("data/processed/chunks.parquet")
print(f"Loaded {len(df)} chunks.")

model_name = SETTINGS["retrieval"]["dense_model"]
print(f"Embedding model: {model_name}  (first run downloads it, ~130 MB)")
ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)

client = chromadb.PersistentClient(path="chroma")
try:
    client.delete_collection("filings")   # start fresh, avoid duplicates
except Exception:
    pass
collection = client.create_collection("filings", embedding_function=ef)

ids = df["chunk_id"].tolist()
docs = df["text"].tolist()
metas = [
    {"company": str(r.company), "doc_name": str(r.doc_name),
     "start_char": int(r.start_char), "end_char": int(r.end_char)}
    for r in df.itertuples()
]

print("Embedding and storing chunks (this takes a few minutes)...")
batch = 1000
for i in range(0, len(df), batch):
    collection.add(ids=ids[i:i+batch], documents=docs[i:i+batch], metadatas=metas[i:i+batch])
    print(f"  stored {min(i+batch, len(df))}/{len(df)}")

print(f"\nDone. {collection.count()} chunks stored in ./chroma/\n")

# --- quick test query ---
q = "What are the main risks the company faces?"
res = collection.query(query_texts=[q], n_results=3)
print(f"Test query: {q}\n")
for rank, (doc, meta, dist) in enumerate(
    zip(res["documents"][0], res["metadatas"][0], res["distances"][0]), 1
):
    print(f"#{rank}  {meta['doc_name']}  (distance {dist:.3f})")
    print("   ", doc[:160].replace(chr(10), " "), "...\n")
