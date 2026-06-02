"""Re-extract filings with pdfplumber, keeping table rows intact.  [v0.5.0]

pypdf reads tables linearly, scattering row labels from their numbers.
pdfplumber detects tables and returns them as rows of cells, so we append
each row as a single line "label | val1 | val2 ...", keeping the label next
to its values. We keep the normal page text too, so we only add signal.
"""
from pathlib import Path

import pdfplumber

pdf_dir = Path("data/raw/pdfs")
out_dir = Path("data/raw/text")
out_dir.mkdir(parents=True, exist_ok=True)

pdfs = sorted(pdf_dir.glob("*.pdf"))
print(f"Found {len(pdfs)} PDFs. pdfplumber is slow - this may take 10+ minutes.\n")

for pdf_path in pdfs:
    name = pdf_path.stem
    print(f"processing {name} ...", flush=True)
    parts = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                parts.append(page.extract_text() or "")
                for table in page.extract_tables():
                    for row in table:
                        cells = [(c or "").replace("\n", " ").strip() for c in row]
                        line = " | ".join(c for c in cells if c)
                        if line:
                            parts.append(line)
        full = "\n".join(parts)
        (out_dir / f"{name}.txt").write_text(full, encoding="utf-8")
        print(f"  -> {len(full):,} chars")
    except Exception as e:
        print(f"  FAILED ({e})")

print("\nDone. Re-extracted text written to data/raw/text/")
