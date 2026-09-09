#!/usr/bin/env bash
#
# Deploy glossator to one Linux host over SSH.
#
#   deploy/deploy.sh <ssh-host> [--mode remote-index|full] [options]
#
# remote-index  the host runs the MCP server alone, against a Vespa that
#               already serves the shipped schemas somewhere else.
# full          the host also runs Vespa, applies the schema migrations, and
#               ingests the vendored corpus through the synced embedding cache.
#
# Re-running redeploys: the sync, the build and `compose up` are all idempotent.
# The host needs docker with the compose plugin and an ssh account that can use
# it; nothing else.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

MODE="remote-index"
REMOTE_DIR="glossator"
WITH_API=0
CHECK_ONLY=0
SKIP_INGEST=0
SKIP_BUILD=0
PRINT_PLAN=0
HOST=""

# Vespa refuses external feeds above this share of the disk, and re-indexing a
# page deletes its chunks before writing the replacements, so a blocked feed
# empties the index instead of refreshing it (D-025b).
FEED_BLOCK_PERCENT=80
HEALTH_TIMEOUT_SECONDS=300
HEALTH_POLL_SECONDS=10

# Never copied to the host: build output, machine-local state, evaluation runs,
# the test suite, and every form of secret file. deploy/.env.deploy is sent
# separately and deliberately.
EXCLUDES=(
  ".git"
  ".venv"
  ".local"
  ".agent-runs"
  ".cache"
  ".mypy_cache"
  ".pytest_cache"
  ".ruff_cache"
  "__pycache__"
  "*.py[cod]"
  "eval/runs"
  "tests"
  ".env"
  ".env.*"
  ".envrc"
  "deploy/embedding-cache"
)

die() {
  echo "error: $*" >&2
  exit 1
}

step() {
  echo
  echo "==> $*"
}

usage() {
  cat <<'USAGE'
Usage: deploy/deploy.sh <ssh-host> [options]

Options:
  --mode remote-index|full  What the host runs (default: remote-index).
  --remote-dir PATH         Directory on the host, relative to its home
                            (default: glossator).
  --with-api                Also run the HTTP API service.
  --skip-ingest             Full mode: migrate but do not ingest.
  --skip-build              Reuse the image already on the host.
  --check-only              Run the health and bearer-token checks and stop.
  --print-plan              Print what would be done, then exit.
  -h, --help                This message.
USAGE
}

parse_args() {
  while [ $# -gt 0 ]; do
    case "$1" in
      --mode)
        [ $# -ge 2 ] || die "--mode needs a value: remote-index or full"
        MODE="$2"
        shift 2
        ;;
      --mode=*)
        MODE="${1#--mode=}"
        shift
        ;;
      --remote-dir)
        [ $# -ge 2 ] || die "--remote-dir needs a path"
        REMOTE_DIR="$2"
        shift 2
        ;;
      --remote-dir=*)
        REMOTE_DIR="${1#--remote-dir=}"
        shift
        ;;
      --with-api)
        WITH_API=1
        shift
        ;;
      --skip-ingest)
        SKIP_INGEST=1
        shift
        ;;
      --skip-build)
        SKIP_BUILD=1
        shift
        ;;
      --check-only)
        CHECK_ONLY=1
        shift
        ;;
      --print-plan)
        PRINT_PLAN=1
        shift
        ;;
      -h | --help)
        usage
        exit 0
        ;;
      -*)
        usage >&2
        die "unknown option: $1"
        ;;
      *)
        [ -z "$HOST" ] || die "only one ssh host is accepted; got '$HOST' and '$1'"
        HOST="$1"
        shift
        ;;
    esac
  done

  if [ -z "$HOST" ]; then
    usage >&2
    die "an ssh host is required"
  fi
  case "$MODE" in
    remote-index | full) ;;
    *) die "unknown mode '$MODE'; use remote-index or full" ;;
  esac
  case "$REMOTE_DIR" in
    '') die "--remote-dir needs a path" ;;
    # rsync hands the far side of a transfer to the host's shell, which would
    # split a path with a space in it into two paths.
    *[[:space:]]*) die "--remote-dir must not contain whitespace: '$REMOTE_DIR'" ;;
  esac
}

# The compose profiles this mode needs, as COMPOSE_PROFILES wants them. Empty
# in remote-index mode, where the mcp service carries no profile and starts on
# its own.
profiles_for_mode() {
  local profiles=""
  if [ "$MODE" = "full" ]; then
    profiles="full"
  fi
  if [ "$WITH_API" = "1" ]; then
    profiles="${profiles:+$profiles,}api"
  fi
  echo "$profiles"
}

print_plan() {
  echo "host: $HOST"
  echo "mode: $MODE"
  echo "remote-dir: $REMOTE_DIR"
  echo "with-api: $WITH_API"
  echo "skip-ingest: $SKIP_INGEST"
  echo "skip-build: $SKIP_BUILD"
  echo "check-only: $CHECK_ONLY"
  echo "profiles: $(profiles_for_mode)"
  echo "excludes:"
  local pattern
  for pattern in "${EXCLUDES[@]}"; do
    echo "  $pattern"
  done
}

require_local_tools() {
  local missing=""
  command -v ssh >/dev/null 2>&1 || missing="$missing ssh"
  command -v rsync >/dev/null 2>&1 || missing="$missing rsync"
  [ -z "$missing" ] || die "missing on this machine:$missing"
}

# ssh hands the remote shell one string, so every argument is single-quoted
# here or the remote shell would re-split it on its own spaces.
shell_quote() {
  local arg out=""
  for arg in "$@"; do
    out="$out '${arg//\'/\'\\\'\'}'"
  done
  printf '%s' "$out"
}

# Run a script read from stdin on the host, with any extra words as $1, $2, ...
remote_bash() {
  ssh -o BatchMode=yes "$HOST" "bash -s --$(shell_quote "$@")"
}

require_remote_tools() {
  ssh -o BatchMode=yes "$HOST" true >/dev/null 2>&1 ||
    die "cannot reach '$HOST' over ssh without a prompt; add your key with ssh-copy-id"

  local missing
  missing="$(remote_bash <<'REMOTE'
missing=""
command -v docker >/dev/null 2>&1 || missing="$missing docker"
docker compose version >/dev/null 2>&1 || missing="$missing docker-compose-plugin"
docker info >/dev/null 2>&1 || missing="$missing docker-daemon-access"
printf '%s' "$missing"
REMOTE
  )"
  [ -z "$missing" ] ||
    die "missing on $HOST:$missing (install docker with the compose plugin and put the ssh account in the docker group)"
}

check_remote_disk() {
  local report percent path
  report="$(remote_bash <<'REMOTE'
root="$(docker info --format '{{.DockerRootDir}}' 2>/dev/null || true)"
[ -n "$root" ] || root=/var/lib/docker
df -P "$root" | awk 'NR==2 { gsub(/%/, "", $5); print $5, $6 }'
REMOTE
  )"
  percent="${report%% *}"
  path="${report#* }"
  case "$percent" in
    '' | *[!0-9]*) die "could not read disk usage on $HOST (got '$report')" ;;
  esac
  if [ "$percent" -ge "$FEED_BLOCK_PERCENT" ]; then
    die "$HOST: $path is ${percent}% full, at or above Vespa's ${FEED_BLOCK_PERCENT}% feed block.
Vespa rejects every write above that mark. Re-indexing a page deletes its chunks
before writing the replacements, so ingesting here would empty the index rather
than refresh it. Free disk space on $HOST and run this again, or deploy with
--mode remote-index against an index that already exists."
  fi
  echo "$path on $HOST is ${percent}% full, under the ${FEED_BLOCK_PERCENT}% feed block."
}

sync_repository() {
  local args=(-az --delete)
  local pattern
  for pattern in "${EXCLUDES[@]}"; do
    args+=(--exclude "$pattern")
  done
  remote_bash "$REMOTE_DIR" <<'REMOTE'
mkdir -p "$1"
REMOTE
  rsync "${args[@]}" "$REPO_DIR/" "$HOST:$REMOTE_DIR/"
}

sync_env_file() {
  if [ -f "$SCRIPT_DIR/.env.deploy" ]; then
    rsync -a "$SCRIPT_DIR/.env.deploy" "$HOST:$REMOTE_DIR/deploy/.env.deploy"
    remote_bash "$REMOTE_DIR" <<'REMOTE'
chmod 600 "$1/deploy/.env.deploy"
REMOTE
    echo "copied deploy/.env.deploy"
    return
  fi
  remote_bash "$REMOTE_DIR" <<'REMOTE' || die_missing_env
test -f "$1/deploy/.env.deploy"
REMOTE
  echo "keeping the deploy/.env.deploy already on $HOST"
}

die_missing_env() {
  die "no deploy/.env.deploy here and none on $HOST.
Copy deploy/.env.deploy.example to deploy/.env.deploy and fill in
MISTRAL_API_KEY and GLOSSATOR_MCP_TOKEN."
}

sync_embedding_cache() {
  local cache="${GLOSSATOR_EMBEDDING_CACHE:-$HOME/.cache/glossator/embeddings}"
  remote_bash "$REMOTE_DIR" <<'REMOTE'
mkdir -p "$1/deploy/embedding-cache"
REMOTE
  if [ ! -d "$cache" ]; then
    echo "no embedding cache at $cache; every chunk will be embedded through the API."
    return
  fi
  rsync -az "$cache/" "$HOST:$REMOTE_DIR/deploy/embedding-cache/"
  echo "synced $(find "$cache" -type f -name '*.json' | wc -l | tr -d ' ') cached embeddings from $cache"
}

# `docker compose` on the host with this mode's profiles and this deployment's
# env file. DEPLOY_UID and DEPLOY_GID let the ingest job write the cache mount.
compose() {
  remote_bash "$REMOTE_DIR" "$(profiles_for_mode)" "$@" <<'REMOTE'
dir="$1"
profiles="$2"
shift 2
cd "$dir"
COMPOSE_PROFILES="$profiles" DEPLOY_UID="$(id -u)" DEPLOY_GID="$(id -g)" \
  docker compose --env-file deploy/.env.deploy -f deploy/compose.yaml "$@"
REMOTE
}

# A one-off job container. The jobs profile is never part of `up`, so a
# finished job does not come back on the next boot.
compose_job() {
  remote_bash "$REMOTE_DIR" "$@" <<'REMOTE'
dir="$1"
shift
cd "$dir"
COMPOSE_PROFILES=jobs DEPLOY_UID="$(id -u)" DEPLOY_GID="$(id -g)" \
  docker compose --env-file deploy/.env.deploy -f deploy/compose.yaml run --rm "$@"
REMOTE
}

wait_for_vespa() {
  step "Waiting for Vespa to accept a deploy"
  local waited=0
  while [ "$waited" -lt "$HEALTH_TIMEOUT_SECONDS" ]; do
    if compose exec -T vespa curl -sf http://localhost:19071/state/v1/health >/dev/null 2>&1; then
      echo "the Vespa config server is up."
      return 0
    fi
    sleep "$HEALTH_POLL_SECONDS"
    waited=$((waited + HEALTH_POLL_SECONDS))
  done
  die "Vespa did not come up within ${HEALTH_TIMEOUT_SECONDS}s; check 'docker compose -f deploy/compose.yaml logs vespa' on $HOST"
}

# Streams deploy/probe.py into the container's python: prints the health JSON,
# then checks that an unauthenticated MCP call is refused and an authenticated
# one is accepted.
run_probe() {
  remote_bash "$REMOTE_DIR" <<'REMOTE'
dir="$1"
cd "$dir"
set -a
# shellcheck disable=SC1091
. ./deploy/.env.deploy
set +a
docker compose --env-file deploy/.env.deploy -f deploy/compose.yaml \
  exec -T mcp python - "$GLOSSATOR_MCP_TOKEN" < deploy/probe.py
REMOTE
}

wait_for_health() {
  step "Waiting for GET /health and checking the bearer token"
  local waited=0
  while [ "$waited" -lt "$HEALTH_TIMEOUT_SECONDS" ]; do
    if run_probe >/dev/null 2>&1; then
      run_probe
      return 0
    fi
    sleep "$HEALTH_POLL_SECONDS"
    waited=$((waited + HEALTH_POLL_SECONDS))
  done
  echo "last attempt:" >&2
  run_probe >&2 || true
  die "the MCP server on $HOST was not healthy within ${HEALTH_TIMEOUT_SECONDS}s;
check 'docker compose -f deploy/compose.yaml logs mcp' on $HOST"
}

public_url() {
  local hostname
  hostname="$(remote_bash "$REMOTE_DIR" <<'REMOTE' || true
dir="$1"
cd "$dir" || exit 0
# shellcheck disable=SC1091
. ./deploy/.env.deploy >/dev/null 2>&1 || exit 0
printf '%s' "${GLOSSATOR_PUBLIC_HOSTNAME:-}"
REMOTE
  )"
  if [ -n "$hostname" ]; then
    echo "https://$hostname"
  else
    echo "https://<your-tunnel-hostname>"
  fi
}

print_client_commands() {
  local base initialize
  base="$(public_url)"
  initialize='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"curl","version":"1"}}}'
  cat <<EOF

The bearer token is enforced. Prove it from anywhere that reaches the tunnel,
with <token> replaced by the GLOSSATOR_MCP_TOKEN value:

  # 401 without an Authorization header
  curl -s -o /dev/null -w '%{http_code}\\n' -X POST $base/mcp \\
    -H 'content-type: application/json' \\
    -H 'accept: application/json, text/event-stream' \\
    -d '$initialize'

  # 200 with the token
  curl -s -o /dev/null -w '%{http_code}\\n' -X POST $base/mcp \\
    -H 'authorization: Bearer <token>' \\
    -H 'content-type: application/json' \\
    -H 'accept: application/json, text/event-stream' \\
    -d '$initialize'

  # /health needs no header
  curl -s $base/health

Add it to Claude Code:

  claude mcp add --transport http glossator $base/mcp --header "Authorization: Bearer <token>"

Add it to Mistral Work: Connectors > + Add Connector > Custom MCP Connector,
Server URL $base/mcp. deploy/README.md has the tunnel and Connector steps.
EOF
}

main() {
  parse_args "$@"
  if [ "$PRINT_PLAN" = "1" ]; then
    print_plan
    exit 0
  fi

  require_local_tools
  require_remote_tools

  if [ "$CHECK_ONLY" = "1" ]; then
    step "Checking the deployment on $HOST"
    run_probe || die "the deployment on $HOST is not healthy"
    print_client_commands
    exit 0
  fi

  if [ "$MODE" = "full" ]; then
    step "Checking disk headroom on $HOST"
    check_remote_disk
  fi

  step "Syncing the repository to $HOST:$REMOTE_DIR"
  sync_repository
  sync_env_file

  if [ "$MODE" = "full" ]; then
    step "Syncing the embedding cache"
    sync_embedding_cache
  fi

  if [ "$SKIP_BUILD" = "0" ]; then
    step "Building the image on $HOST"
    compose build
  fi

  if [ "$MODE" = "full" ]; then
    step "Starting Vespa"
    compose up -d vespa
    wait_for_vespa
    step "Applying schema migrations"
    compose_job migrate
    if [ "$SKIP_INGEST" = "0" ]; then
      step "Ingesting the vendored corpus"
      compose_job ingest
    else
      echo "skipping ingestion (--skip-ingest)"
    fi
  fi

  step "Starting the services"
  compose up -d

  wait_for_health
  print_client_commands
}

main "$@"
