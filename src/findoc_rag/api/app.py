"""FastAPI service.  [PHASE 4 — Week 9]

Exposes FinDocRAG as an HTTP API. Not yet implemented — see ROADMAP.md, Week 9.

The FastAPI import is guarded so this file can be imported safely in earlier
phases, before ``fastapi`` is installed. Once you reach Phase 4, uncomment the
FastAPI block in requirements.txt and build out the endpoints below.
"""

from __future__ import annotations

try:
    from fastapi import FastAPI

    _FASTAPI_AVAILABLE = True
except ImportError:  # FastAPI is a Phase 4 dependency.
    _FASTAPI_AVAILABLE = False


def create_app():
    """Build and return the FastAPI application.

    TODO (Week 9):
      - GET  /healthz  -> simple liveness check, returns {"status": "ok"}.
      - POST /query    -> accepts {"question": str}, runs retrieve + generate,
                          returns the answer, citations, and retrieved chunks.
      - Wire each request through Langfuse tracing (added in Week 8).
    """
    if not _FASTAPI_AVAILABLE:
        raise RuntimeError(
            "FastAPI is not installed. Uncomment the Phase 4 block in "
            "requirements.txt and run: pip install -r requirements.txt"
        )

    app = FastAPI(title="FinDocRAG", version="0.1.0")

    @app.get("/healthz")
    def healthz() -> dict:
        return {"status": "ok"}

    # TODO (Week 9): add the POST /query endpoint here.
    return app
