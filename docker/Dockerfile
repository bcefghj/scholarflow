FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic@0.15.0/tectonic-0.15.0-x86_64-unknown-linux-gnu.tar.gz \
    | tar xz -C /usr/local/bin/

COPY pyproject.toml README.md LICENSE ./
COPY scholarflow/ ./scholarflow/
COPY cli/ ./cli/
COPY web/ ./web/
COPY mcp/ ./mcp/
COPY skill/ ./skill/

RUN pip install --no-cache-dir ".[web]"

EXPOSE 8080

CMD ["uvicorn", "web.backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
