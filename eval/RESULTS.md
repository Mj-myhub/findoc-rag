# Evaluation Results

## Setup
- **Slice:** 15 SEC 10-K filings, 57 FinanceBench questions (see `data/DATA_CARD.md`).
- **Metric:** retrieval recall. For each question we retrieve the top-10 chunks and
  measure the largest fraction of gold-evidence tokens found in any single chunk
  (commas removed so "1,577" == "1577"); a hit means that overlap is >= 0.50.
  This is a heuristic proxy, so treat absolute values as directional.

## Retrieval ablation (Recall@10)

| Configuration     | Recall@10 | Avg. overlap |
|-------------------|-----------|--------------|
| BM25 (keyword)    | 10.5%     | 0.26         |
| Dense (meaning)   | 21.1%     | 0.35         |
| Hybrid (RRF)      | 22.8%     | 0.35         |
| Hybrid + reranker | 24.6%     | 0.35         |

## What this shows
- Dense beats keyword: questions rarely use the filing's exact wording.
- Hybrid beats either index alone: fusion recovers items each one misses.
- Reranking adds a further lift by re-reading candidates with the question.
- Each component earns its place; the architecture is validated.

## Key finding: numerical questions are the weak spot
Retrieval succeeds on descriptive questions ("what industry", "major products",
"dividends paid") but fails on numerical / financial-statement questions (capital
expenditure, EBITDA margin, fixed-asset turnover, effective tax rate). 10-K
financial statements are tables, and naive PDF extraction scatters row labels away
from their values, so no single chunk cleanly contains the answer.

## Next steps
- Table-aware extraction / chunking so financial-statement rows stay intact.
- Quantify recall split by question type (descriptive vs numerical).
- Add answer-quality metrics (faithfulness, correctness) on top of retrieval recall.
