# FinDocRAG — Architecture

This document explains *how* the system is built and *why* each choice was made. It is written to be read by a recruiter or engineer reviewing the project.

## 1. The pipeline
## 2. Components and responsibilities

| Module        | Responsibility |
|---------------|----------------|
| `data/`       | Load FinanceBench (gold questions/answers); save local copies. |
| `ingest/`     | Table-aware PDF extraction, then split filings into overlapping, metadata-tagged chunks. |
| `index/`      | Build a BM25 keyword index and a dense vector index over the chunks. |
| `retrieval/`  | Expand the query into filing terminology, query both indexes, fuse with RRF, rerank with a cross-encoder. |
| `generate/`   | Build the prompt, call the LLM, enforce citation + abstention behaviour. |
| `evaluation/` | Score retrieval against FinanceBench gold evidence; produce the ablation table. |
| `api/`        | Expose the system as a FastAPI endpoint and a Gradio web demo. |

## 3. Key design decisions

**Why hybrid retrieval (BM25 + dense)?**
Dense embeddings capture meaning but miss exact identifiers — ticker symbols, line-item names, specific figures — which matter a lot in financial text. BM25 (keyword search) catches those. Combining both with Reciprocal Rank Fusion is the production-standard baseline and reliably beats either method alone on noisy document collections.

**Why a reranker?**
First-stage retrieval optimises for recall (get the right passage *somewhere* in the top 20). A cross-encoder reranker then re-scores those candidates with a more accurate but slower model, pushing the truly relevant passage to the top. Retrieval quality is the single biggest driver of final RAG quality, so this stage earns its cost.

**Why table-aware extraction and query expansion?**
These two came out of debugging a real failure: numerical questions that read financial-statement tables kept abstaining. Tracing it revealed two stacked causes. First, the default PDF reader scattered each table row's label away from its number, so no chunk held both — fixed with table-aware extraction (pdfplumber). Second, a vocabulary gap: a question asks about "capital expenditure" while the filing says "purchases of property, plant and equipment", and neither keyword nor embedding search bridged the two — fixed by having the LLM rewrite the question into filing terminology before retrieval. Together they raised best-config Recall@10 from 24.6% to 38.6%. The full investigation is in `eval/RESULTS.md`.

**Why abstention?**
A system that confidently invents an answer when the filing does not contain one is worse than useless in finance. The generator is explicitly prompted to say "I cannot find this in the filings" when the retrieved context is insufficient.

**Why evaluate against FinanceBench instead of self-written questions?**
Self-written evaluation questions are easy to game and unconvincing to a reviewer. FinanceBench is an external, expert-written benchmark — measuring against it makes the results credible.

**Why Groq for the LLM?**
The project must be free to run. Groq offers a free API tier with fast inference for open models (Llama 3.1). Generation and query expansion are the only components that call an external service; everything else runs locally.

## 4. Data flow at query time

1. User submits a question.
2. An LLM rewrites the question into likely 10-K line-item terminology and appends it to the query.
3. The expanded query is embedded and also tokenised for BM25.
4. Both indexes return their top-k chunks; RRF merges them into one ranked list.
5. The cross-encoder reranker re-scores the merged list against the original question; the top-N chunks are kept.
6. Those chunks + the question go into the prompt.
7. The LLM produces an answer with inline references to chunk IDs, or abstains.

## 5. What is intentionally simple

This is a portfolio project, not a production deployment. It deliberately does **not** include: multi-tenant auth, autoscaling, a managed vector database, streaming responses, or request tracing/observability (e.g. Langfuse). The focus is on demonstrating correct retrieval design, rigorous evaluation, and clean engineering — the skills junior NLP/LLM roles actually screen for.
