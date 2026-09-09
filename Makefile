.PHONY: installdeps install-workflows ingest search ask api mcp test start-examples execute-ingestion
.PHONY: corpus-refresh corpus-check dev-set dev-noisy eval-report eval-answers eval-retrieval calibrate-floors failures
.PHONY: setup-vespa start-vespa verify-vespa stop-vespa reset-vespa migrate-vespa bruno generate-vespa-lock
.PHONY: deploy deploy-check

ifneq (,$(wildcard .env))
include .env
export
endif

MCP_HOST := $(or $(host),127.0.0.1)
MCP_PORT := $(or $(port),8000)
API_HOST := $(or $(host),127.0.0.1)
API_PORT := $(or $(port),8080)
VESPA_CONTAINER := glossator-vespa
VESPA_QUERY_PORT := $(or $(VESPA_QUERY_PORT),18080)
VESPA_CONFIG_PORT := $(or $(VESPA_CONFIG_PORT),19072)
VESPA_ENDPOINT := $(or $(VESPA_ENDPOINT),http://localhost:$(VESPA_QUERY_PORT))
VESPA_CONFIG_URL := $(or $(VESPA_CONFIG_URL),http://localhost:$(VESPA_CONFIG_PORT))

# Docs repo commit the vendored corpus is built from (DECISIONS.md D-001, D-009).
CORPUS_REF := $(or $(REF),2e094f7bbe1395de4a738a3483def3573143d973)
CORPUS_DIR := $(or $(CORPUS_DIR),corpus/mistral-docs)

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

## Answer a question from the documentation, with verified citations
## Usage: make ask question="how do I stream a chat completion" [strategy=single_pass] [variant=sec1024] [model=id] [record=path]
ask:
	uv run python -m glossator.answer "$(question)" $(if $(strategy),--strategy $(strategy),) $(if $(variant),--variant $(variant),) $(if $(model),--model $(model),) $(if $(record),--record $(record),)

## Start the HTTP API
## Usage: make api [host=0.0.0.0] [port=8080]
api:
	uv run uvicorn entrypoints.api:app --host $(API_HOST) --port $(API_PORT)

## Start the MCP server in HTTP mode
## Usage: make mcp [host=0.0.0.0] [port=8000]
mcp:
	uv run python -m entrypoints.mcp_server --http --host $(MCP_HOST) --port $(MCP_PORT)

## Round-trip a document through the configured backend (skips unless it is set up)
test:
	uv run pytest tests/ -q

## Generate the 300-question development set
dev-set:
	uv run python -m glossator.eval.generate --corpus corpus/mistral-docs --out eval/dev.jsonl --n 300 --provider zai --model glm-5.3-flash --seed 0

## Build badly worded variants of a stratified subset of a dataset
## Usage: make dev-noisy [dataset=eval/dev.jsonl] [out=eval/dev-noisy.jsonl] [n=120] [seed=0]
dev-noisy:
	uv run python -m glossator.eval.perturb \
		--dataset $(or $(dataset),eval/dev.jsonl) \
		--out $(or $(out),eval/dev-noisy.jsonl) \
		--n $(or $(n),120) --seed $(or $(seed),0) \
		--provider zai --model glm-5.3 --name $(or $(name),dev-noisy)

## Score a question dataset through the answer strategies
## Usage: make eval-answers dataset=eval/dev.jsonl name=answers-dev [strategies=single_pass,search_loop,outline] [variant=sec1024] [limit=N] [model=id] [judge_model=glm-5.3] [skip_judge=1] [rewrite=1]
eval-answers:
	uv run python -m glossator.eval.answer_eval --dataset $(dataset) --name $(name) \
		$(if $(strategies),--strategies $(strategies),) \
		$(if $(variant),--variant $(variant),) \
		$(if $(limit),--limit $(limit),) \
		$(if $(model),--model $(model),) \
		$(if $(judge_model),--judge-model $(judge_model),) \
		$(if $(note),--note "$(note)",) \
		$(if $(rewrite),--rewrite,) \
		$(if $(skip_judge),--skip-judge,)
## Run every question through every retrieval configuration in the grid
## Usage: make eval-retrieval dataset=eval/dev.jsonl name=dev [configs=a,b] [limit=N]
eval-retrieval:
	uv run python -m glossator.eval.retrieval_grid \
		--dataset $(dataset) \
		--grid $(or $(grid),eval/configs/retrieval-grid.yaml) \
		--name $(name) \
		$(if $(configs),--configs $(configs),) \
		$(if $(limit),--limit $(limit),)

## Classify the failed answers of one or more answer-evaluation runs
## Usage: make failures runs="eval/runs/a eval/runs/b" [name=failure-analysis] [judge_model=zai:glm-5.3]
failures:
	uv run python -m glossator.eval.failures \
		$(foreach run,$(runs),--run $(run)) \
		--name $(or $(name),failure-analysis) \
		$(if $(judge_model),--judge-model $(judge_model),)

## Measure the similarity corridor between real and junk questions (D-030)
## Usage: make calibrate-floors dataset=eval/dev.jsonl name=dev [variant=sec1024]
calibrate-floors:
	uv run python -m glossator.eval.calibrate_floors \
		--dataset $(dataset) --name $(name) $(if $(variant),--variant $(variant),)

## Regenerate a run's README and figures from its records
## Usage: make eval-report run=eval/runs/2026-09-08-2312-dev-smoke
eval-report:
	uv run python -m glossator.eval.report $(run)

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

## Rebuild the vendored documentation corpus from the docs repo
## Usage: make corpus-refresh [REF=<commit|tag|branch>]
corpus-refresh:
	uv run python -m glossator.corpus.mistral_docs build \
		--ref $(CORPUS_REF) \
		--out $(CORPUS_DIR) \
		--refresh-openapi

## Check every corpus URL and anchor against docs.mistral.ai
corpus-check:
	uv run pytest tests/corpus -q
	uv run python -m glossator.corpus.mistral_docs check --live --corpus $(CORPUS_DIR)

## Deploy the MCP server to a Linux host over SSH
## Usage: make deploy HOST=lxc-glossator [MODE=remote-index|full] [API=1] [REMOTE_DIR=path]
deploy:
	@test -n "$(HOST)" || { echo "error: HOST is required. Usage: make deploy HOST=<ssh-host> [MODE=full]"; exit 1; }
	deploy/deploy.sh $(HOST) --mode $(or $(MODE),remote-index) \
		$(if $(API),--with-api,) $(if $(REMOTE_DIR),--remote-dir $(REMOTE_DIR),)

## Check a deployed host: GET /health, then one MCP call without the token and one with it
## Usage: make deploy-check HOST=lxc-glossator
deploy-check:
	@test -n "$(HOST)" || { echo "error: HOST is required. Usage: make deploy-check HOST=<ssh-host>"; exit 1; }
	deploy/deploy.sh $(HOST) --check-only $(if $(REMOTE_DIR),--remote-dir $(REMOTE_DIR),)
