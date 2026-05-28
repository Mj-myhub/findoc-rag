"""Central configuration for FinDocRAG.

Loads project paths, settings from ``config/settings.yaml``, and secrets from a
``.env`` file. Import what you need from here rather than hard-coding paths or keys.

Example:
    from findoc_rag.config import SETTINGS, RAW_DATA_DIR
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

# Load variables from a .env file if present (no error if it is missing).
load_dotenv()

# --- Project paths -----------------------------------------------------------
# config.py lives at: <root>/src/findoc_rag/config.py  ->  parents[2] is <root>.
PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
DATA_DIR: Path = PROJECT_ROOT / "data"
RAW_DATA_DIR: Path = DATA_DIR / "raw"
PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
CONFIG_PATH: Path = PROJECT_ROOT / "config" / "settings.yaml"


def load_settings(path: Path = CONFIG_PATH) -> dict:
    """Read and parse the YAML settings file."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


# Parsed settings, available as a module-level dict.
SETTINGS: dict = load_settings()

# --- Secrets (loaded from .env; empty string if unset) -----------------------
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
HF_TOKEN: str = os.getenv("HF_TOKEN", "")
LANGFUSE_PUBLIC_KEY: str = os.getenv("LANGFUSE_PUBLIC_KEY", "")
LANGFUSE_SECRET_KEY: str = os.getenv("LANGFUSE_SECRET_KEY", "")
