"""Chunk all extracted filings and save to data/processed/chunks.parquet."""
from pathlib import Path

import pandas as pd

from findoc_rag.config import SETTINGS
from findoc_rag.ingest.chunking import chunk_text

text_dir = Path("data/raw/text")
out_path = Path("data/processed/chunks.parquet")
out_path.parent.mkdir(parents=True, exist_ok=True)

# Map each document to its company name (from FinanceBench metadata).
meta = pd.read_parquet("data/raw/financebench.parquet")
company_map = dict(zip(meta["doc_name"], meta["company"]))

chunk_size = SETTINGS["chunking"]["chunk_size"]
overlap = SETTINGS["chunking"]["chunk_overlap"]
print(f"chunk_size={chunk_size}, overlap={overlap}\n")

rows = []
for txt_path in sorted(text_dir.glob("*.txt")):
    doc_name = txt_path.stem
    company = company_map.get(doc_name, "UNKNOWN")
    text = txt_path.read_text(encoding="utf-8")
    chunks = chunk_text(text, company, doc_name, chunk_size, overlap)
    for c in chunks:
        rows.append({
            "chunk_id": c.chunk_id,
            "company": c.company,
            "doc_name": c.doc_name,
            "start_char": c.start_char,
            "end_char": c.end_char,
            "text": c.text,
        })
    print(f"{doc_name:32s} {len(chunks):5d} chunks  (company: {company})")

df = pd.DataFrame(rows)
df.to_parquet(out_path)
print(f"\nTotal chunks: {len(df)}")
print(f"Saved to: {out_path}")
