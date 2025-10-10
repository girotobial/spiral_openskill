FROM ghcr.io/astral-sh/uv:python3.12-bookworm as base
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev


COPY scripts/ /app/scripts

RUN mkdir -p /data
ENV DB_PATH=/data/data.db

ENV PATH="/app/.venv/bin:${PATH}"

EXPOSE 8000

CMD ["uv", "run", "--no-sync","uvicorn", "scripts.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]