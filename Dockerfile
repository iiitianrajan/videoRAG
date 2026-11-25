
# Node.js runtime for yt-dlp JavaScript challenge support
FROM node:22-bookworm-slim AS node-runtime

FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:${PATH}"

WORKDIR /app

# Install FFmpeg and runtime libraries
RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        ffmpeg \
        ca-certificates \
        libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

# Copy Node.js runtime
COPY --from=node-runtime /usr/local/bin/node /usr/local/bin/node

# Install uv
RUN pip install --no-cache-dir "uv==0.13.5"

# Install dependencies first
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy application source
COPY app.py main.py ./
COPY core ./core
COPY utils ./utils
COPY videorag ./videorag

# Install project
RUN uv sync --frozen --no-dev

EXPOSE 8501

# Use Render's PORT when available; otherwise use 8501
CMD ["sh", "-c", "streamlit run app.py --server.address=0.0.0.0 --server.port=${PORT:-8501}"]
