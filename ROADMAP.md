# FinDocRAG — Build Roadmap

This is your week-by-week plan. Work through it in order. Each step lists **what to do**,
**which files to touch**, and a **"done when"** test so you always know if you can move on.

When you get stuck: bring the **specific file**, the **exact error message**, and **what you
expected** back to Claude. That is enough to debug anything here. Do not try to hold the whole
project in your head — just focus on the current week.

---

## Phase 1 — Foundation (Weeks 1–2)

### Week 1 — Environment, repo, data
**Goal:** a working environment and the evaluation dataset on disk.

Tasks:
1. Push this scaffold to your GitHub repo `findoc-rag`.
2. Create a virtual environment and run `make install`.
3. Run `make explore`. This loads FinanceBench and saves `data/raw/financebench.parquet`.
   - If it fails with a "dataset not found" error, open `config/settings.yaml`, and follow the
     instructions in the error to correct `data.financebench_dataset_id`.
4. Open `notebooks/01_explore_financebench.ipynb` (upload it to Google Colab) and run it.
5. Run `make test` — all tests should pass.

Files: everything is already written for you this week. You are running and reading, not coding.

**Done when:** `data/raw/financebench.parquet` exists, `make test` passes, and you can explain
what columns FinanceBench has and what a single example looks like.

### Week 2 — Understand the corpus, define your evaluation slice
**Goal:** know exactly which questions you will answer and which filings hold the answers.

Tasks:
1. In the notebook, group FinanceBench by company and document. List the unique filings.
2. Pick a starting slice — e.g. 10–15 filings and the ~40–60 questions tied to them. Start small.
3. Collect the actual filing text for that slice into `data/raw/` (FinanceBench references the
   source documents; the FinanceBench GitHub repo links the PDFs).
4. Write a short `data/DATA_CARD.md` describing your slice: which companies, how many questions,
   question types, where the text came from.

Files: `notebooks/01_explore_financebench.ipynb`, new `data/DATA_CARD.md`.

**Done when:** you have the filing text for your chosen slice on disk, plus the matching gold
questions, and a data card describing them.

---

## Phase 2 — The RAG core (Weeks 3–6)

### Week 3 — Chunking
Implement `src/findoc_rag/ingest/chunking.py`. Split each filing into overlapping passages and
keep metadata (company, document, character span). Start with a simple fixed-size sliding
window; improve to section-aware chunking if time allows.

**Done when:** a script turns your filings into a list of chunks with metadata, saved to
`data/processed/chunks.parquet`.

### Week 4 — Indexing
Implement `src/findoc_rag/index/build_index.py`. Build two indexes over the chunks:
a BM25 keyword index and a dense vector index in ChromaDB using a sentence-transformer
embedding model.

**Done when:** you can take a query string and get back the top-k chunks from *each* index
separately.

### Week 5 — Retrieval (hybrid + reranking)
Implement `src/findoc_rag/retrieval/retriever.py`. Combine BM25 and dense results with
Reciprocal Rank Fusion (RRF), then re-order the merged list with a cross-encoder reranker.

**Done when:** one function takes a question and returns a final ranked list of the most
relevant chunks.

### Week 6 — Generation
Implement `src/findoc_rag/generate/generator.py`. Send the retrieved chunks plus the question
to an LLM (Groq free tier). The prompt must instruct the model to (a) answer only from the
provided context, (b) cite the source passages, and (c) say "I cannot find this in the
filings" when the context does not contain the answer (abstention).

**Done when (v0.2.0):** a command-line script answers a FinanceBench question end to end with
citations.

---

## Phase 3 — Evaluation and observability (Weeks 7–8)

### Week 7 — Evaluation
Implement `src/findoc_rag/evaluation/evaluate.py`. Measure two things:
- **Retrieval quality:** Recall@k, MRR, nDCG@10 — does the right passage get retrieved?
- **Answer quality:** faithfulness, answer relevancy, answer correctness — via RAGAS and
  DeepEval, scored against FinanceBench gold answers.

Run the evaluation four times — dense-only, BM25-only, hybrid, hybrid+reranker — and fill in
the **ablation table** in `README.md`.

**Done when:** the README results table has real numbers and shows each component's effect.

### Week 8 — Observability and error analysis
Add Langfuse tracing around every LLM and retrieval call. Then read 20–30 failing cases and
classify each failure: retrieval miss, citation mismatch, unsupported claim, abstention failure.
Write this up as `eval/ERROR_ANALYSIS.md`.

**Done when:** you have trace screenshots and a written failure taxonomy with at least one
concrete bug you found and fixed.

---

## Phase 4 — Ship it (Weeks 9–10)

### Week 9 — Serving and demo
Implement `src/findoc_rag/api/app.py` (a FastAPI `/query` endpoint) and a Streamlit demo with
three panes: the question, the answer with citations, and a debug panel showing retrieved
chunks and scores. Write the `Dockerfile`. Deploy the demo to Hugging Face Spaces.

**Done when:** there is a public URL where anyone can try FinDocRAG.

### Week 10 — Polish and launch
- Finish the README: architecture diagram, demo GIF, results, a "What I learned" section.
- Write the project up (a short blog post or GitHub Pages page).
- Draft the LinkedIn launch post and the CV bullet points.
- Pin the repo on your GitHub profile.

**Done when:** the repo is something you would confidently send to a recruiter.

---

## Versioning checkpoints

Tag a git release at each milestone so progress is visible in the repo history:

- `v0.1.0` — end of Phase 1 (data + scaffold)
- `v0.2.0` — end of Phase 2 (working end-to-end RAG)
- `v0.3.0` — end of Phase 3 (evaluated, with results)
- `v1.0.0` — end of Phase 4 (deployed and documented)

## A note on scope

If your job search becomes urgent, a credible **v0.5** is: Phases 1–2 plus a basic evaluation
(Week 7 only), skipping Langfuse, Docker, and the agentic extensions. Ship that, apply, and add
the rest afterwards. One genuinely finished, deployed, evaluated project beats three unfinished
ones.
