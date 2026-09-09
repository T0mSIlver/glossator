# The glossator application image: MCP server, HTTP API, and the ingestion CLI.
#
# The corpus is vendored in the repository, so the only thing fetched at build
# time is the locked set of Python packages. Nothing here reads a secret: the
# API key and the MCP bearer token arrive as environment variables at run time.

FROM python:3.12-slim-bookworm AS build

COPY --from=ghcr.io/astral-sh/uv:0.11.24 /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

# Dependencies resolve from the lock alone, so this layer survives every source
# edit and a redeploy re-installs nothing.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src
RUN uv sync --frozen --no-dev

FROM python:3.12-slim-bookworm

# Non-root, with a real home: the ingestion cache lives under $HOME/.cache and
# is bind-mounted from the operator's machine on a full deploy.
RUN groupadd --system --gid 10001 glossator \
 && useradd --system --uid 10001 --gid glossator --home-dir /home/glossator \
    --create-home --shell /usr/sbin/nologin glossator

ENV PATH=/app/.venv/bin:$PATH \
    HOME=/home/glossator \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    GLOSSATOR_CORPUS_DIR=/app/corpus/mistral-docs \
    GLOSSATOR_SNAPSHOT_MANIFEST=/app/eval/snapshots/manifest.json

WORKDIR /app

COPY --from=build --chown=glossator:glossator /app/.venv /app/.venv
COPY --chown=glossator:glossator src ./src
COPY --chown=glossator:glossator corpus ./corpus
COPY --chown=glossator:glossator pyproject.toml uv.lock ./
# The history tool reads the snapshot manifest; it is 4 KB of metadata, and
# without it that tool answers every call with an error.
COPY --chown=glossator:glossator eval/snapshots/manifest.json ./eval/snapshots/manifest.json
RUN mkdir -p /home/glossator/.cache/glossator/embeddings \
 && chown -R glossator:glossator /home/glossator

USER glossator

EXPOSE 8000
CMD ["python", "-m", "entrypoints.mcp_server", "--http", "--host", "0.0.0.0", "--port", "8000"]
