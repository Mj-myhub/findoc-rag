# ---- Stage 1: builder ----
# Install Python dependencies into a clean, isolated location.
FROM python:3.12-slim AS builder

# Don't write .pyc files, and don't buffer stdout (so logs appear immediately).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install into a virtual environment so we can copy just this folder later.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy only the lock file first, so Docker can cache the (slow) install layer.
COPY requirements-lock.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements-lock.txt

# ---- Stage 2: final runtime image ----
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    HF_HOME=/app/.cache/huggingface

WORKDIR /app

# Bring over the installed dependencies from the builder stage.
COPY --from=builder /opt/venv /opt/venv

# Copy the application code, config, and prebuilt indexes into the image.
COPY src/ ./src/
COPY config/ ./config/
COPY chroma/ ./chroma/
COPY data/processed/bm25.pkl ./data/processed/bm25.pkl
COPY app.py ./app.py

# Gradio serves on 7860 by default.
EXPOSE 7860

# Bind to 0.0.0.0 so the app is reachable from outside the container.
ENV GRADIO_SERVER_NAME=0.0.0.0

CMD ["python", "app.py"]
