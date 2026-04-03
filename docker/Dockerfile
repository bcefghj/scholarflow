FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    curl \
    texlive-xetex \
    texlive-latex-extra \
    texlive-fonts-recommended \
    fonts-wqy-microhei \
    fontconfig \
    && fc-cache -fv \
    && rm -rf /var/lib/apt/lists/*

RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip config set global.trusted-host mirrors.aliyun.com

COPY pyproject.toml README.md LICENSE ./
COPY scholarflow/ ./scholarflow/
COPY cli/ ./cli/
COPY web/ ./web/
COPY mcp/ ./mcp/
COPY skill/ ./skill/

RUN pip install --no-cache-dir ".[web]"

EXPOSE 8080

CMD ["uvicorn", "web.backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
