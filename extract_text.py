"""Extract plain text from each downloaded 10-K PDF into data/raw/text/."""
from pathlib import Path
from pypdf import PdfReader

pdf_dir = Path("data/raw/pdfs")
out_dir = Path("data/raw/text")
out_dir.mkdir(parents=True, exist_ok=True)

pdfs = sorted(pdf_dir.glob("*.pdf"))
print(f"Found {len(pdfs)} PDFs to process.\n")

for pdf_path in pdfs:
    name = pdf_path.stem
    out_path = out_dir / (name + ".txt")
    try:
        reader = PdfReader(str(pdf_path))
        pages = reader.pages
        texts = [(page.extract_text() or "") for page in pages]
        full_text = "\n".join(texts)
        out_path.write_text(full_text, encoding="utf-8")
        print(f"{name:32s} {len(pages):4d} pages  {len(full_text):>8d} chars")
    except Exception as e:
        print(f"{name:32s} FAILED ({e})")

print("\nDone. Text files are in data/raw/text/")
