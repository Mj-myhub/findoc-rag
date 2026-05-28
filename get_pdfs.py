"""Download the 15 chosen FinanceBench filings into data/raw/pdfs/."""
import urllib.request
from pathlib import Path

FILINGS = [
    "AMD_2022_10K", "AMERICANEXPRESS_2022_10K", "BOEING_2022_10K",
    "PEPSICO_2022_10K", "AMCOR_2023_10K", "3M_2022_10K",
    "AES_2022_10K", "BESTBUY_2023_10K", "CVSHEALTH_2022_10K",
    "JOHNSON_JOHNSON_2022_10K", "PFIZER_2021_10K", "VERIZON_2022_10K",
    "3M_2018_10K", "ACTIVISIONBLIZZARD_2019_10K", "ADOBE_2022_10K",
]

BASE = "https://raw.githubusercontent.com/patronus-ai/financebench/main/pdfs/"
out_dir = Path("data/raw/pdfs")
out_dir.mkdir(parents=True, exist_ok=True)

for name in FILINGS:
    url = BASE + name + ".pdf"
    dest = out_dir / (name + ".pdf")
    if dest.exists():
        print(f"already have   {name}")
        continue
    try:
        urllib.request.urlretrieve(url, dest)
        print(f"downloaded     {name}")
    except Exception as e:
        print(f"FAILED         {name}  ({e})")
