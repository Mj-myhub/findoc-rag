# Data Card — FinDocRAG evaluation slice

## Overview
This project does not use all of FinanceBench. It uses a fixed **slice** of 15 SEC 10-K
filings and the 57 expert-written questions tied to them. This card documents exactly
what that slice contains and where it came from, so the work is reproducible.

## Source
- **Benchmark:** FinanceBench (Patronus AI) — an open-source set of 150 expert-written
  question/answer pairs over real SEC filings.
- **Q/A metadata:** the `PatronusAI/financebench` dataset on the Hugging Face Hub,
  including the gold `evidence` passages used later to evaluate retrieval.
- **Filings (PDFs):** downloaded from the FinanceBench GitHub repo
  (patronus-ai/financebench, /pdfs/), then converted to plain text with pypdf.

## The slice
- **15 filings** across **14 companies** (3M appears twice: 2018 and 2022).
- **57 questions** total — picked by taking the 15 filings with the most associated
  questions, to maximise evaluation coverage per document downloaded.

### Companies / filings
3M (2018, 2022), Activision Blizzard (2019), Adobe (2022), AES (2022), Amcor (2023),
AMD (2022), American Express (2022), Best Buy (2023), Boeing (2022), CVS Health (2022),
Johnson & Johnson (2022), PepsiCo (2022), Pfizer (2021), Verizon (2022).

### Questions by type
| Question type     | Count | What it means |
|-------------------|-------|---------------|
| domain-relevant   | 38    | Questions a financial analyst would realistically ask; need domain reasoning. |
| novel-generated   | 12    | Harder, novel questions written to stress-test the system. |
| metrics-generated | 7     | Extract one specific figure from a known statement (e.g. FY2018 capex). |

### Coverage
- **Sectors (GICS):** Industrials (12), Information Technology (9), Health Care (9),
  Financials (7), Communication Services (5), Consumer Staples (5), Materials (4),
  Utilities (3), Consumer Discretionary (3).
- **Filing years:** 2022 (43), 2023 (7), 2021 (3), 2018 (2), 2019 (2).

## Files on disk
- data/raw/pdfs/ — the 15 source PDFs (git-ignored; regenerate with get_pdfs.py).
- data/raw/text/ — extracted plain text, one .txt per filing (regenerate with extract_text.py).
- data/raw/financebench.parquet — the Q/A metadata (regenerate with
  `python -m findoc_rag.data.load_financebench`).

## Evaluation note
Each question carries a gold **evidence** passage — the exact text the answer comes from.
In Phase 3 this is the ground truth for measuring whether retrieval finds the right passage.

## License / disclaimer
FinanceBench is released by Patronus AI under its own license; this project uses the
open-source subset for research/portfolio purposes only and redistributes no derived data.
This is not financial advice.
