"""Tuned ablation: does a larger candidate pool help hybrid+rerank?"""
import pandas as pd

from findoc_rag.evaluation.evaluate import best_overlap, gold_evidence_text
from findoc_rag.retrieval.retriever import Retriever, reciprocal_rank_fusion

SLICE = [
    "AMD_2022_10K", "AMERICANEXPRESS_2022_10K", "BOEING_2022_10K",
    "PEPSICO_2022_10K", "AMCOR_2023_10K", "3M_2022_10K",
    "AES_2022_10K", "BESTBUY_2023_10K", "CVSHEALTH_2022_10K",
    "JOHNSON_JOHNSON_2022_10K", "PFIZER_2021_10K", "VERIZON_2022_10K",
    "3M_2018_10K", "ACTIVISIONBLIZZARD_2019_10K", "ADOBE_2022_10K",
]
THRESHOLD = 0.5
FINAL_K = 10
POOL_SIZES = [10, 30, 50]

df = pd.read_parquet("data/raw/financebench.parquet")
df = df[df["doc_name"].isin(SLICE)].reset_index(drop=True)
r = Retriever()


def hybrid_rerank(q, pool_k):
    fused = reciprocal_rank_fusion(
        [r._vector_search(q, pool_k), r._bm25_search(q, pool_k)]
    )
    cands = [r._as_record(cid) for cid in fused]
    scores = r.reranker.predict([(q, c["text"]) for c in cands])
    ranked = [c for _, c in sorted(zip(scores, cands), key=lambda x: x[0], reverse=True)]
    return ranked[:FINAL_K]


n = len(df)
print(f"Hybrid+rerank, varying candidate pool. {n} questions, top-{FINAL_K} returned.\n")
print(f"{'pool size':>10s} {'Recall@10':>11s} {'avg overlap':>13s}")
print("-" * 38)
for pool_k in POOL_SIZES:
    overlaps = []
    for _, row in df.iterrows():
        gold = gold_evidence_text(row["evidence"])
        overlaps.append(best_overlap(gold, hybrid_rerank(row["question"], pool_k)))
    hits = sum(1 for o in overlaps if o >= THRESHOLD)
    print(f"{pool_k:>10d} {hits / n:>10.1%} {sum(overlaps) / n:>13.2f}")
