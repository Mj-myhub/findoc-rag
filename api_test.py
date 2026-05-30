"""Test the API in-process (no uvicorn needed)."""
from fastapi.testclient import TestClient

from findoc_rag.api.app import app

with TestClient(app) as client:
    resp = client.post(
        "/ask",
        json={"question": "What are the main business risks for AMD?"},
    )

print("HTTP status:", resp.status_code, "\n")
data = resp.json()
print("Answer:\n", data["answer"], "\n")
print("Abstained:", data["abstained"])
print("Citations:", data["citations"])
print("\nChunks given to the model:")
for c in data["chunks"]:
    print(f"  [{c['chunk_id']}]  {c['doc_name']}")
