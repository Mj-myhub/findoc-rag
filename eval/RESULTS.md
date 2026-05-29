# Evaluation Results

## Setup
- **Slice:** 15 SEC 10-K filings, 57 FinanceBench questions (see `data/DATA_CARD.md`).
- **Metric:** retrieval recall. For each question we retrieve the top-10 chunks and
  measure the largest fraction of gold-evidence tokens found in any single chunk
  (commas removed so "1,577" == "1577"); a hit means that overlap is >= 0.50.
  This is a heuristic proxy, so treat absolute values as directional.

## Baseline ablation (chunk_size = 800, overlap = 100)

| Configuration     | Recall@10 | Avg. overlap |
|-------------------|-----------|--------------|
| BM25 (keyword)    | 10.5%     | 0.26         |
| Dense (meaning)   | 21.1%     | 0.35         |
| Hybrid (RRF)      | 22.8%     | 0.35         |
| Hybrid + reranker | 24.6%     | 0.35         |

Dense beats keyword (questions rarely match the filing's wording); hybrid beats
either alone; reranking adds a final lift. Each component earns its place — but
absolute recall is low, especially on numerical / financial-statement questions.

## Tuning experiments

### Larger candidate pool (no lift)
Tested hybrid + rerank with candidate pool sizes 10, 30, 50.

| Pool size | Recall@10 |
|-----------|-----------|
| 10        | 24.6%     |
| 30        | 24.6%     |
| 50        | 21.1%     |

Recall did not improve, and pool=50 dropped — flooding the reranker with look-alikes
pushes the right chunk out. Conclusion: the right chunks are *not* reachable by
simply casting a wider net. The bottleneck is structural.

### Larger chunks (chunk_size = 1500, overlap = 300)

| Configuration     | Before (800) | After (1500) | Δ          |
|-------------------|--------------|--------------|------------|
| BM25              | 10.5%        | 19.3%        | +8.8 pts   |
| Dense             | 21.1%        | 33.3%        | +12.2 pts  |
| Hybrid            | 22.8%        | 29.8%        | +7.0 pts   |
| Hybrid + reranker | **24.6%**    | **33.3%**    | **+8.7 pts** |

Average best-overlap moved from 0.35 to 0.46.

## Honest interpretation
The chunk-size lift is real but partly mechanical: larger chunks contain more text,
so by chance they include more gold tokens, which boosts an overlap-based metric.

The metric-independent test: the 3M FY2018 capital-expenditure question (gold
answer $1,577M) **still abstains** under the larger chunks. Retrieval does not
surface the cash-flow chunk containing the figure. So while the metric improved
broadly, the core problem for numerical / table questions persists: the matching
signal between "capital expenditure" (the question) and "Purchases of property,
plant and equipment" (the line item) is weak in both keyword and embedding space.

## Key finding
Retrieval is reliable on **descriptive** questions and unreliable on **numerical /
financial-statement** questions. Larger chunks help on the margin but do not fix
the core failure mode, which is rooted in PDF table extraction scattering row
labels away from their values.

## Next steps
- Table-aware extraction so financial-statement rows stay intact (pdfplumber, unstructured).
- Query rewriting / vocabulary expansion ("capital expenditure" => "Purchases of property, plant and equipment").
- Split recall by question type (descriptive vs numerical) for a precise breakdown.
- Add answer-quality metrics (faithfulness, correctness) layered on top of retrieval recall.
