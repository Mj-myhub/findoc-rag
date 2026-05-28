"""Smoke tests — confirm the project is correctly set up.

These run in CI on every push. They check that the package imports, that
configuration loads, and that project paths resolve. As you build later
phases, add real tests for chunking, retrieval, etc. alongside these.
"""

from __future__ import annotations

import findoc_rag
from findoc_rag import config


def test_package_version() -> None:
    """The package exposes a version string."""
    assert isinstance(findoc_rag.__version__, str)
    assert findoc_rag.__version__ != ""


def test_settings_load() -> None:
    """settings.yaml parses and contains the expected top-level sections."""
    assert isinstance(config.SETTINGS, dict)
    for section in ("data", "chunking", "retrieval", "generation"):
        assert section in config.SETTINGS, f"missing '{section}' in settings.yaml"


def test_dataset_id_configured() -> None:
    """A FinanceBench dataset id is configured."""
    dataset_id = config.SETTINGS["data"]["financebench_dataset_id"]
    assert isinstance(dataset_id, str) and dataset_id


def test_project_paths() -> None:
    """Core project paths are resolved and named as expected."""
    assert config.PROJECT_ROOT.exists()
    assert config.RAW_DATA_DIR.name == "raw"
    assert config.PROCESSED_DATA_DIR.name == "processed"
