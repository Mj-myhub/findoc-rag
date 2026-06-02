"""Effect of LLM query expansion on hybrid+rerank Recall@10."""
import pandas as pd

from findoc_rag.evaluation.evaluate import best_overlap, gold_evidence_text
from findoc_rag.retrieval.retriever import (
    Retriever,
    expand_query,
    reciprocal_rank_fusion,
)

SLICE = [
    "AMD_2022_10K", "AMERICANEXPRESS_2022_10K", "BOEING_2022_10K",
    "PEPSICO_2022_10K", "AMCOR_2023_10K", "3M_2022_10K",
    "AES_2022_10K", "BESTBUY_2023_10K", "CVSHEALTH_2022_10K",
    "JOHNSON_JOHNSON_2022_10K", "PFIZER_2021_10K", "VERIZON_2022_10K",
    "3M_2018_10K", "ACTIVISIONBLIZZARD_2019_10K", "ADOBE_2022_10K",
]
THRESHOLD = 0.5
K = 10

df = pd.read_parquet("data/raw/financebench.parquet")
df = df[df["doc_name"].isin(SLICE)].reset_index(drop=True)
r = Retriever()


def hybrid_rerank(q, use_expand):
    sq = expand_query(q, r.groq) if use_expand else q
    fused = reciprocal_rank_fusion([r._vector_search(sq, K), r._bm25_search(sq, K)])
    cands = [r._as_record(cid) for cid in fused]
    scores = r.reranker.predict([(q, c["text"]) for c in cands])
    ranked = [c for _, c in sorted(zip(scores, cands), key=lambda x: x[0], reverse=True)]
    return ranked[:K]


n = len(df)
print(f"hybrid+rerank Recall@{K} across {n} questions (expansion adds an LLM call each)\n")
print(f"{'query expansion':>16s} {'Recall@10':>11s} {'avg overlap':>13s}")
print("-" * 42)
for use_expand in [False, True]:
    overlaps = []
    for _, row in df.iterrows():
        gold = gold_evidence_text(row["evidence"])
        overlaps.append(best_overlap(gold, hybrid_rerank(row["question"], use_expand)))
    hits = sum(1 for o in overlaps if o >= THRESHOLD)
    print(f"{'ON' if use_expand else 'OFF':>16s} {hits / n:>10.1%} {sum(overlaps) / n:>13.2f}")
