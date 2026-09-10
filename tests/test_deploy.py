"""The deployment pipeline, checked without a host to deploy to.

The compose file and the Dockerfile are exercised through docker itself, so both
skip when docker is absent. Everything about `deploy/deploy.sh` that can be
checked without an ssh connection -- argument parsing, mode validation, and the
list of paths that must never leave this machine -- runs the real script through
a subprocess.
"""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest
from deploy import probe

REPO_ROOT = Path(__file__).resolve().parents[1]
DEPLOY_DIR = REPO_ROOT / "deploy"
COMPOSE_FILE = DEPLOY_DIR / "compose.yaml"
DEPLOY_SCRIPT = DEPLOY_DIR / "deploy.sh"
ENV_EXAMPLE = DEPLOY_DIR / ".env.deploy.example"

SAMPLE_ENV = """\
MISTRAL_API_KEY=test-key-not-a-real-one
GLOSSATOR_MCP_TOKEN=test-token-not-a-real-one
GLOSSATOR_MCP_TOOLS=search,cite
GLOSSATOR_VARIANT=sec1024
VESPA_ENDPOINT=http://192.168.1.98:18080
MCP_BIND_ADDRESS=127.0.0.1
MCP_PORT=8000
"""

# Set by deploy.sh from the host account rather than by whoever fills in
# .env.deploy, so the template does not list them.
SCRIPT_SUPPLIED = {"DEPLOY_UID", "DEPLOY_GID", "EMBEDDING_CACHE_DIR"}


def _docker_compose_available() -> bool:
    if shutil.which("docker") is None:
        return False
    try:
        return (
            subprocess.run(
                ["docker", "compose", "version"],
                capture_output=True,
                timeout=60,
            ).returncode
            == 0
        )
    except (OSError, subprocess.SubprocessError):
        return False


def _docker_daemon_available() -> bool:
    if shutil.which("docker") is None:
        return False
    try:
        return subprocess.run(["docker", "info"], capture_output=True, timeout=60).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


needs_compose = pytest.mark.skipif(
    not _docker_compose_available(),
    reason="docker with the compose plugin is not installed",
)


def _write_env(tmp_path: Path, body: str = SAMPLE_ENV) -> Path:
    env_file = tmp_path / ".env.deploy"
    env_file.write_text(body)
    return env_file


def _compose(env_file: Path, *args: str, profiles: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "docker",
            "compose",
            "--env-file",
            str(env_file),
            "-f",
            str(COMPOSE_FILE),
            *args,
        ],
        capture_output=True,
        text=True,
        timeout=180,
        env={"PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": str(env_file.parent)}
        | ({"COMPOSE_PROFILES": profiles} if profiles else {}),
    )


def _plan(*args: str) -> dict[str, str]:
    """`deploy.sh --print-plan` output as a mapping, with `excludes` left out."""
    result = subprocess.run(
        ["bash", str(DEPLOY_SCRIPT), *args, "--print-plan"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, result.stderr
    plan: dict[str, str] = {}
    for line in result.stdout.splitlines():
        if line.startswith(" ") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        plan[key.strip()] = value.strip()
    return plan


def _plan_excludes(*args: str) -> list[str]:
    result = subprocess.run(
        ["bash", str(DEPLOY_SCRIPT), *args, "--print-plan"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    start = lines.index("excludes:") + 1
    return [line.strip() for line in lines[start:] if line.startswith("  ")]


def test_deploy_script_is_executable_and_valid_bash() -> None:
    assert DEPLOY_SCRIPT.stat().st_mode & 0o111, "deploy/deploy.sh is not executable"
    result = subprocess.run(
        ["bash", "-n", str(DEPLOY_SCRIPT)], capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0, result.stderr


def test_default_mode_is_remote_index() -> None:
    plan = _plan("lxc-glossator")
    assert plan["mode"] == "remote-index"
    assert plan["host"] == "lxc-glossator"
    assert plan["remote-dir"] == "glossator"
    # No profile: the mcp service is the only one that starts on its own.
    assert plan["profiles"] == ""


def test_full_mode_selects_the_vespa_profile() -> None:
    assert _plan("host", "--mode", "full")["profiles"] == "full"
    assert _plan("host", "--mode=full", "--with-api")["profiles"] == "full,api"
    assert _plan("host", "--with-api")["profiles"] == "api"


def test_flags_are_parsed_in_either_form() -> None:
    plan = _plan("host", "--remote-dir=/srv/glossator", "--skip-ingest", "--skip-build")
    assert plan["remote-dir"] == "/srv/glossator"
    assert plan["skip-ingest"] == "1"
    assert plan["skip-build"] == "1"
    assert _plan("host", "--remote-dir", "/srv/other")["remote-dir"] == "/srv/other"


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        ([], "an ssh host is required"),
        (["host", "--mode", "bogus"], "unknown mode 'bogus'"),
        (["host", "--mode"], "--mode needs a value"),
        (["host", "--nonsense"], "unknown option: --nonsense"),
        (["one", "two"], "only one ssh host is accepted"),
        (["host", "--remote-dir", "with space"], "must not contain whitespace"),
    ],
)
def test_bad_arguments_are_refused_by_name(args: list[str], expected: str) -> None:
    result = subprocess.run(
        ["bash", str(DEPLOY_SCRIPT), *args, "--print-plan"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO_ROOT,
    )
    assert result.returncode != 0
    assert expected in result.stderr


def test_secrets_and_local_state_never_leave_this_machine() -> None:
    excludes = _plan_excludes("host", "--mode", "full")
    for pattern in (".env", ".env.*", ".envrc", ".git", ".venv", ".local", ".agent-runs"):
        assert pattern in excludes, f"{pattern} would be copied to the deployment host"


def test_evaluation_runs_and_tests_stay_here() -> None:
    excludes = _plan_excludes("host")
    assert "eval/runs" in excludes
    assert "tests" in excludes
    # The synced cache lives under deploy/, and a --delete sync must not fight
    # with the separate rsync that fills it.
    assert "deploy/embedding-cache" in excludes


def test_the_corpus_is_deployed() -> None:
    """The image is built on the host, so the vendored pages have to travel."""
    excludes = _plan_excludes("host")
    assert not any(pattern.startswith("corpus") for pattern in excludes)


@needs_compose
def test_compose_file_parses(tmp_path: Path) -> None:
    result = _compose(_write_env(tmp_path), "config")
    assert result.returncode == 0, result.stderr
    assert "glossator-mcp" in result.stdout
    assert "test-key-not-a-real-one" in result.stdout, "the API key is passed at run time"


@needs_compose
def test_remote_index_mode_starts_only_the_mcp_server(tmp_path: Path) -> None:
    result = _compose(_write_env(tmp_path), "config", "--services")
    assert result.returncode == 0, result.stderr
    assert result.stdout.split() == ["mcp"]


@needs_compose
def test_full_mode_adds_vespa(tmp_path: Path) -> None:
    result = _compose(_write_env(tmp_path), "config", "--services", profiles="full")
    assert result.returncode == 0, result.stderr
    assert set(result.stdout.split()) == {"mcp", "vespa"}


@needs_compose
def test_the_jobs_never_start_with_the_services(tmp_path: Path) -> None:
    """A finished migration or ingestion must not come back on the next boot."""
    result = _compose(_write_env(tmp_path), "config", "--services", profiles="full,api")
    assert result.returncode == 0, result.stderr
    services = set(result.stdout.split())
    assert "migrate" not in services
    assert "ingest" not in services


@needs_compose
def test_an_open_transport_is_refused(tmp_path: Path) -> None:
    """Without a token the MCP server is open to anyone who finds the tunnel."""
    body = "\n".join(
        line for line in SAMPLE_ENV.splitlines() if not line.startswith("GLOSSATOR_MCP_TOKEN=")
    )
    result = _compose(_write_env(tmp_path, body + "\n"), "config")
    assert result.returncode != 0
    assert "GLOSSATOR_MCP_TOKEN" in result.stderr


@needs_compose
def test_a_missing_api_key_is_refused(tmp_path: Path) -> None:
    body = "\n".join(
        line for line in SAMPLE_ENV.splitlines() if not line.startswith("MISTRAL_API_KEY=")
    )
    result = _compose(_write_env(tmp_path, body + "\n"), "config")
    assert result.returncode != 0
    assert "MISTRAL_API_KEY" in result.stderr


@needs_compose
def test_the_mcp_port_stays_on_the_loopback_address(tmp_path: Path) -> None:
    result = _compose(_write_env(tmp_path), "config", "--format", "json")
    assert result.returncode == 0, result.stderr
    published = json.loads(result.stdout)["services"]["mcp"]["ports"]
    assert [(entry["host_ip"], entry["published"], entry["target"]) for entry in published] == [
        ("127.0.0.1", "8000", 8000)
    ]


FAKE_SSH = """\
#!/usr/bin/env bash
# Stands in for ssh: everything after the host name is one command string, so
# an argument that survives this shim survives a real ssh connection.
while [ $# -gt 0 ]; do
  case "$1" in
    -o) shift 2 ;;
    -*) shift ;;
    *) shift; break ;;
  esac
done
exec /bin/sh -c "$*"
"""


def _with_fake_ssh(tmp_path: Path, body: str) -> subprocess.CompletedProcess[str]:
    """Source deploy.sh with ssh replaced, and run `body` against its functions."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "ssh"
    fake.write_text(FAKE_SSH)
    fake.chmod(0o755)
    script = tmp_path / "case.sh"
    script.write_text(f'set -euo pipefail\nsource "{DEPLOY_SCRIPT}"\nHOST=localhost\n{body}\n')
    return subprocess.run(
        ["bash", str(script)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO_ROOT,
        env={"PATH": f"{bin_dir}:/usr/bin:/bin:/usr/local/bin", "HOME": str(tmp_path)},
    )


def test_an_argument_with_a_space_survives_the_hop(tmp_path: Path) -> None:
    """ssh hands the far side one string, so every argument is quoted first."""
    result = _with_fake_ssh(
        tmp_path,
        'remote_bash "two words" second <<\'REMOTE\'\necho "[$1][$2]"\nREMOTE',
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "[two words][second]"


def test_a_full_disk_stops_the_deploy_before_anything_is_deleted(tmp_path: Path) -> None:
    result = _with_fake_ssh(tmp_path, "FEED_BLOCK_PERCENT=0\ncheck_remote_disk")
    assert result.returncode != 0
    assert "feed block" in result.stderr
    assert "empty the index" in result.stderr


def test_headroom_below_the_feed_block_is_reported(tmp_path: Path) -> None:
    result = _with_fake_ssh(tmp_path, "FEED_BLOCK_PERCENT=101\ncheck_remote_disk")
    assert result.returncode == 0, result.stderr
    assert "% full, under the 101% feed block." in result.stdout


def test_every_compose_variable_is_in_the_template() -> None:
    referenced = set(re.findall(r"\$\{([A-Z0-9_]+)[:?}-]", COMPOSE_FILE.read_text()))
    documented = set(re.findall(r"^([A-Z0-9_]+)=", ENV_EXAMPLE.read_text(), flags=re.MULTILINE))
    missing = referenced - documented - SCRIPT_SUPPLIED
    assert not missing, f"undocumented in deploy/.env.deploy.example: {sorted(missing)}"


def test_the_template_holds_no_value_for_either_secret() -> None:
    for line in ENV_EXAMPLE.read_text().splitlines():
        for name in ("MISTRAL_API_KEY", "GLOSSATOR_MCP_TOKEN"):
            if line.startswith(f"{name}="):
                assert line == f"{name}=", f"{name} carries a value in the committed template"


def test_the_image_runs_as_a_non_root_user() -> None:
    dockerfile = (REPO_ROOT / "Dockerfile").read_text()
    assert "\nUSER glossator\n" in dockerfile
    assert dockerfile.index("\nUSER glossator\n") < dockerfile.index("\nCMD ")


def test_the_build_ignores_secrets_and_the_test_suite() -> None:
    ignored = {
        line.strip()
        for line in (REPO_ROOT / ".dockerignore").read_text().splitlines()
        if line.strip() and not line.startswith("#")
    }
    assert {".env", ".venv", ".git", "tests", "deploy"} <= ignored


def test_probe_requests_the_latest_installed_protocol() -> None:
    request = json.loads(probe.INITIALIZE)
    assert request["params"]["protocolVersion"] == "2025-11-25"


def test_probe_prints_the_negotiated_protocol(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    responses = iter(
        [
            (200, b'{"status":"ok"}'),
            (401, b""),
            (
                200,
                b'data: {"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2025-11-25"}}\r\n\r\n',
            ),
        ]
    )
    monkeypatch.setattr(probe, "_status", lambda request: next(responses))

    assert probe.main("secret") == 0
    output = capsys.readouterr()
    assert "protocol check: requested 2025-11-25, negotiated 2025-11-25" in output.out
    assert output.err == ""


def test_probe_rejects_a_different_negotiated_protocol(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    responses = iter(
        [
            (200, b'{"status":"ok"}'),
            (401, b""),
            (200, b'{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2025-06-18"}}'),
        ]
    )
    monkeypatch.setattr(probe, "_status", lambda request: next(responses))

    assert probe.main("secret") == 1
    output = capsys.readouterr()
    assert "protocol check: requested 2025-11-25, negotiated 2025-06-18" in output.out
    assert "the server negotiated MCP protocol 2025-06-18; expected 2025-11-25" in output.err


@pytest.mark.slow
@pytest.mark.skipif(not _docker_daemon_available(), reason="the docker daemon is not reachable")
def test_the_image_builds() -> None:
    result = subprocess.run(
        ["docker", "build", "-t", "glossator:pytest", "-f", str(REPO_ROOT / "Dockerfile"), "."],
        capture_output=True,
        text=True,
        timeout=1800,
        cwd=REPO_ROOT,
    )
    assert result.returncode == 0, result.stderr[-4000:]
    inspected = subprocess.run(
        ["docker", "image", "inspect", "glossator:pytest", "--format", "{{.Config.User}}"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert inspected.stdout.strip() == "glossator"
