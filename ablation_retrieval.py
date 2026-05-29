"""Recall@10 ablation: dense vs BM25 vs hybrid vs hybrid+rerank."""
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
K = 10
THRESHOLD = 0.5

df = pd.read_parquet("data/raw/financebench.parquet")
df = df[df["doc_name"].isin(SLICE)].reset_index(drop=True)
r = Retriever()


def recs(ids):
    return [r._as_record(cid) for cid in ids]


def dense(q):
    return recs(r._vector_search(q, K))


def bm25(q):
    return recs(r._bm25_search(q, K))


def hybrid(q):
    fused = reciprocal_rank_fusion([r._vector_search(q, K), r._bm25_search(q, K)])
    return recs(fused[:K])


def hybrid_rerank(q):
    fused = reciprocal_rank_fusion([r._vector_search(q, K), r._bm25_search(q, K)])
    cands = recs(fused)
    scores = r.reranker.predict([(q, c["text"]) for c in cands])
    ranked = [c for _, c in sorted(zip(scores, cands), key=lambda x: x[0], reverse=True)]
    return ranked[:K]


modes = {"dense": dense, "bm25": bm25, "hybrid": hybrid, "hybrid+rerank": hybrid_rerank}
results = {m: [] for m in modes}

print(f"Running ablation on {len(df)} questions (a few minutes)...\n")
for _, row in df.iterrows():
    gold = gold_evidence_text(row["evidence"])
    for m, fn in modes.items():
        results[m].append(best_overlap(gold, fn(row["question"])))

n = len(df)
print(f"{'Configuration':18s} {'Recall@10':>10s} {'avg overlap':>13s}")
print("-" * 43)
for m in modes:
    ovs = results[m]
    rec = sum(1 for o in ovs if o >= THRESHOLD) / n
    print(f"{m:18s} {rec:>9.1%} {sum(ovs) / n:>13.2f}")
