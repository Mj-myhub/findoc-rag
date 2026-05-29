"""Measure retrieval recall for the current pipeline across the 57-question slice."""
import pandas as pd

from findoc_rag.evaluation.evaluate import best_overlap, gold_evidence_text
from findoc_rag.retrieval.retriever import Retriever

SLICE = [
    "AMD_2022_10K", "AMERICANEXPRESS_2022_10K", "BOEING_2022_10K",
    "PEPSICO_2022_10K", "AMCOR_2023_10K", "3M_2022_10K",
    "AES_2022_10K", "BESTBUY_2023_10K", "CVSHEALTH_2022_10K",
    "JOHNSON_JOHNSON_2022_10K", "PFIZER_2021_10K", "VERIZON_2022_10K",
    "3M_2018_10K", "ACTIVISIONBLIZZARD_2019_10K", "ADOBE_2022_10K",
]
THRESHOLD = 0.5

df = pd.read_parquet("data/raw/financebench.parquet")
df = df[df["doc_name"].isin(SLICE)].reset_index(drop=True)
print(f"Evaluating {len(df)} questions (this takes a couple of minutes)...\n")

r = Retriever()
hits, overlaps = 0, []
for _, row in df.iterrows():
    gold = gold_evidence_text(row["evidence"])
    chunks = r.retrieve(row["question"], top_k=10)   # hybrid + rerank (final ~5 chunks)
    ov = best_overlap(gold, chunks)
    overlaps.append(ov)
    if ov >= THRESHOLD:
        hits += 1
    tag = "HIT " if ov >= THRESHOLD else "miss"
    print(f"[{tag}] ov={ov:.2f}  {row['doc_name']:24s} {row['question'][:50]}")

n = len(df)
print(f"\nRecall (overlap >= {THRESHOLD}): {hits}/{n} = {hits / n:.1%}")
print(f"Average best-overlap: {sum(overlaps) / n:.2f}")
