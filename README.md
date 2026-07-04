# FinDocRAG

Ask plain-English questions about SEC 10-K annual reports and get answers grounded in the filing text — with citations, or an honest "I cannot find this" when the answer isn't there.

A retrieval-augmented generation (RAG) system built from scratch over real financial filings, with a measured, honest evaluation.

## What it does

10-K filings run 100–200 pages of dense financial and legal text. FinDocRAG answers questions like *"What are AMD's main business risks?"* with a short response that cites the exact passages it used — and refuses to guess when the answer isn't in the filings.

> **Q:** What are the main business risks for AMD?
> **A:** Intel's dominance of the microprocessor market; global economic uncertainty; reliance on external financing. *[cites AMD_2022_10K::57, ::60, ::6]*

> **Q:** What is the capital of France?
> **A:** I cannot find this in the filings.

## How it works

```mermaid
flowchart LR
    Q[Question] --> E[LLM query expansion]
    E --> B[BM25 keyword search]
    E --> D[Dense vector search]
    B --> F[Reciprocal Rank Fusion]
    D --> F
    F --> R[Cross-encoder rerank]
    R --> L[LLM: grounded, cited answer or abstain]
```

- **Chunking:** filings split into 1,500-character overlapping passages
- **Extraction:** table-aware PDF parsing (`pdfplumber`) keeps each table row's label next to its numbers
- **Query expansion:** an LLM rewrites the question into the filing's own line-item wording before searching (e.g. "capital expenditure" → "purchases of property, plant and equipment")
- **Keyword index:** BM25 (`rank-bm25`)
- **Vector index:** `BAAI/bge-small-en-v1.5` embeddings in ChromaDB
- **Fusion:** Reciprocal Rank Fusion merges both rankings
- **Reranking:** `BAAI/bge-reranker-base` cross-encoder re-scores candidates
- **Generation:** Groq `openai/gpt-oss-20b` with a strict cite-or-abstain prompt
- **Interfaces:** FastAPI endpoint (`POST /ask`) and a Gradio web demo

## Results

Evaluated on 57 expert-written questions from [FinanceBench](https://github.com/patronus-ai/financebench) across a 15-filing slice. Metric: retrieval Recall@10 by gold-evidence overlap. Full methodology and the complete ablation are in [eval/RESULTS.md](eval/RESULTS.md).

**Retrieval ablation** — why each architecture choice earns its place:

| Configuration     | Recall@10 |
|-------------------|-----------|
| BM25 (keyword)    | 19.3%     |
| Dense (meaning)   | 33.3%     |
| Hybrid (RRF)      | 29.8%     |
| Hybrid + reranker | 33.3%     |

**Then two targeted improvements** attacked the system's hardest case — numerical questions that read financial-statement tables. Table-aware extraction made the values *retrievable*; query expansion made them *findable* across the question/filing vocabulary gap. Together they lifted the best configuration to **38.6%** Recall@10 and made previously-failing numerical questions (e.g. capital expenditure) answerable.

The standout piece of work is the **three-layer debugging investigation** behind that gain — tracing one stubborn failure through ranking, then PDF extraction, then a question/filing vocabulary mismatch. The full write-up is in [eval/RESULTS.md](eval/RESULTS.md).

**Honest note:** 38.6% is a real improvement, not a perfect score — some multi-table reasoning questions remain hard. The gap is measured and understood, not hidden.

## Quickstart

Requires Python 3.10+ and a free [Groq API key](https://console.groq.com).

```bash
# 1. Environment
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .

# 2. Add your Groq key
cp .env.example .env
# edit .env and set GROQ_API_KEY=gsk_...

# 3. Build data + indexes (downloads 15 filings; a few minutes)
python3 get_pdfs.py
python3 extract_text_v2.py      # table-aware extraction (pdfplumber)
python3 make_chunks.py
python3 build_vector_index.py
python3 build_bm25_index.py

# 4. Run the demo
python3 demo.py     # Gradio UI at http://127.0.0.1:7860
```

Or run the API:

```bash
uvicorn findoc_rag.api.app:app
# POST http://127.0.0.1:8000/ask  body: {"question": "..."}
```

## Tech stack

Python · sentence-transformers · ChromaDB · rank-bm25 · pdfplumber · Groq · FastAPI · Gradio · pytest · ruff · GitHub Actions

## Status & future work

A complete, working, evaluated, demoable system. Possible next steps: answer-quality metrics (faithfulness, correctness); a permanently hosted demo (e.g. Hugging Face Spaces); extending the evaluation slice beyond 15 filings.


## Deployment

FinDocRAG is packaged as a self-contained Docker image and has been run both as a
hosted demo and on a cloud server.

### Live demo

A Gradio demo runs on Hugging Face Spaces (free CPU tier):

**https://huggingface.co/spaces/thecodeholic/findoc-rag**

The first answer takes about 10–15 seconds while the embedding and reranker models
warm up on CPU.

### Containerization

The app ships as a multi-stage Docker image:

- A **builder** stage installs the pinned dependencies into an isolated virtualenv.
- The **runtime** stage copies only that virtualenv plus the app code and the
  prebuilt indexes, so the shipped image stays lean.
- Dependencies are fully pinned in `requirements-lock.txt` for reproducible builds.
- PyTorch is installed from the CPU-only wheel index
  (`--extra-index-url https://download.pytorch.org/whl/cpu`), which drops the unused
  CUDA libraries and cuts the image from ~3.4 GB to under 1 GB.

Build and run locally:

```bash
docker build -t findoc-rag:local .
docker run --rm -p 7860:7860 --env-file .env findoc-rag:local
# then open http://localhost:7860
```

The image is also published to Docker Hub:

```bash
docker pull jasperjafari/findoc-rag:latest
```

### AWS (Amazon EC2)

The container was deployed to a single EC2 instance to validate a container-to-URL
workflow on general-purpose cloud infrastructure.

- **Compute:** `t3.small` (2 vCPU, 2 GiB RAM), Ubuntu 24.04, `us-east-2`. The 2 GiB
  is what the model stack (PyTorch + embedding model + cross-encoder reranker +
  ChromaDB) needs to load without being killed.
- **Cross-architecture build:** the build host is Apple Silicon (ARM) but EC2 is
  x86, so the image is built for `linux/amd64` with `docker buildx`, pushed to
  Docker Hub, and pulled on the instance.
- **Networking:** a security group allows inbound `22` (admin) and `7860` (app);
  the instance gets an auto-assigned public IPv4.
- **Secrets:** the Groq API key is passed at runtime with `-e GROQ_API_KEY=...` and
  is never baked into the image.
- **Cost control:** an AWS Budgets alarm was created before any resource was
  provisioned, and the instance was terminated after validation.

On the instance:

```bash
sudo apt-get update && sudo apt-get install -y docker.io
sudo docker pull jasperjafari/findoc-rag:latest
sudo docker run -d --restart unless-stopped -p 7860:7860 \
  -e GROQ_API_KEY="<your-key>" --name findoc jasperjafari/findoc-rag:latest
```

### Screenshots

_Cited answer served from the EC2 public endpoint:_

![3M capital-expenditure answer, cited, served from EC2](docs/aws-capex.png)

_Multi-source answer with the EC2 address visible in the bar:_

![AMD business-risks answer with citations](docs/aws-amd.png)

_The EC2 instance, running with status checks passed:_

![EC2 t3.small instance running](docs/aws-ec2.png)
