.PHONY: installdeps install-workflows ingest search mcp test start-examples execute-ingestion
.PHONY: setup-vespa start-vespa verify-vespa stop-vespa reset-vespa migrate-vespa bruno generate-vespa-lock

ifneq (,$(wildcard .env))
include .env
export
endif

MCP_HOST := $(or $(host),127.0.0.1)
MCP_PORT := $(or $(port),8000)
VESPA_CONTAINER := glossator-vespa
VESPA_QUERY_PORT := $(or $(VESPA_QUERY_PORT),18080)
VESPA_CONFIG_PORT := $(or $(VESPA_CONFIG_PORT),19072)
VESPA_ENDPOINT := $(or $(VESPA_ENDPOINT),http://localhost:$(VESPA_QUERY_PORT))
VESPA_CONFIG_URL := $(or $(VESPA_CONFIG_URL),http://localhost:$(VESPA_CONFIG_PORT))

## Install dependencies
installdeps:
	uv sync

## Start Vespa and apply schema migrations
setup-vespa: start-vespa migrate-vespa

start-vespa:
	docker compose up -d --wait vespa
	@$(MAKE) verify-vespa

verify-vespa:
	@docker inspect -f '{{.State.Running}}' $(VESPA_CONTAINER) 2>/dev/null | grep -q true \
		|| { echo "error: $(VESPA_CONTAINER) is not running. Run: make start-vespa"; exit 1; }
	@curl -sf $(VESPA_CONFIG_URL)/state/v1/health >/dev/null \
		|| { echo "error: config server not reachable at $(VESPA_CONFIG_URL)"; exit 1; }
	@echo "Vespa OK: container=$(VESPA_CONTAINER) config=$(VESPA_CONFIG_URL) query=http://localhost:$(VESPA_QUERY_PORT)"

stop-vespa:
	docker compose stop vespa

## Stop Vespa and remove this project's data volume (wipes indexed documents; run `make setup-vespa` to start fresh)
reset-vespa:
	docker compose down -v --remove-orphans
	@echo "Vespa stopped and project volume removed. Run: make setup-vespa"

migrate-vespa: verify-vespa
	uv run mistral-vespa migrate --app-dir src/glossator/index \
		--config-server $(VESPA_CONFIG_URL) \
		--query-port $(VESPA_QUERY_PORT)

## Ingest a corpus directory into one index variant
## Usage: make ingest corpus=corpus/mistral-docs variant=sec1024
ingest:
	uv run python -m glossator.ingest --corpus $(corpus) --variant $(variant)

## Search one index variant
## Usage: make search query="how do I stream a response" [variant=sec1024] [top_k=10]
search:
	uv run python -m glossator.retrieval "$(query)" $(if $(variant),--variant $(variant),) $(if $(top_k),--top-k $(top_k),)

## Start the MCP server in HTTP mode
## Usage: make mcp [host=0.0.0.0] [port=8000]
mcp:
	uv run python -m entrypoints.mcp_server --http --host $(MCP_HOST) --port $(MCP_PORT)

## Round-trip a document through the configured backend (skips unless it is set up)
test:
	uv run pytest tests/ -q

## Generate Bruno API files under vespa/bruno/vespa/ (requires WORKSPACE_ROOT in .env)
bruno:
	uv run mistral-vespa bruno \
		--app-dir src/glossator/index \
		--query-url $(VESPA_ENDPOINT) \
		--document-url $(VESPA_ENDPOINT)

## Optional: write a vespa.lock snapshot for inspection or CI
generate-vespa-lock:
	uv run mistral-vespa generate \
		--app-dir src/glossator/index \
		--path ./vespa.lock

## Install optional workflows dependency (required for examples/workflows/)
install-workflows:
	uv sync --extra workflows

## Start a worker that registers the example workflows (requires install-workflows)
start-examples: install-workflows
	uv run python -m examples.workflows.worker

## Execute the ingestion workflow via the Mistral Workflows API
## Usage: make execute-ingestion input='{"file_path": "sample_data/hello.txt", "collection_name": "mydocs"}'
execute-ingestion: install-workflows
	uv run python -m examples.workflows.start --workflow document-ingestion $(if $(input),--input '$(input)',--input '{"file_path":"sample_data/hello.txt"}')
