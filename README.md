# bento-test

Hello-world BentoML service that calls `spear_dsp` from our private JFrog PyPI
index. Exists to prove out private JFrog credentials with BentoML's Python-SDK
runtime environment (no `bentofile.yaml`).

## Setup

Tooling is pinned in `mise.toml` (Python 3.12 + uv). Create the venv and install:

```bash
mise install
uv venv --python 3.12
uv sync
```

`uv sync` pulls `spear-dsp` from JFrog. You need credentials stored locally:

```bash
uv auth login spearai.jfrog.io --username [your-spear-email] --password [jfrog-token]
```

This writes `~/.local/share/uv/credentials/credentials.toml`. Generate the token
from JFrog: profile (top right) > "Set Me Up" > "PyPI", pick `spear-ai-pypi` and
the `uv` client.

## Run locally

```bash
uv run bentoml serve service:HelloSpearDsp --port 4400
curl -X POST http://localhost:4400/hello -H 'content-type: application/json' -d '{"seconds": 3}'
```

Locally `spear_dsp` is already in the venv, so the JFrog index in `service.py` is
unused at serve time — the `JFROG_*` env vars are only consumed when the image
builds.

## Runtime environment

`service.py` defines the image with the Python SDK. It only points pip at the
private index; the package list comes from `pyproject.toml`'s
`[project.dependencies]`, which BentoML reads at build time:

```python
image = bentoml.images.Image(python_version="3.12", lock_python_packages=False).python_packages(
    "--index-url https://pypi.org/simple",
    "--extra-index-url https://${JFROG_USERNAME}:${JFROG_ACCESS_TOKEN}@spearai.jfrog.io/artifactory/api/pypi/spear-ai-pypi/simple",
)
```

Add a dependency by editing `pyproject.toml` and re-running `uv sync` — never
touch `service.py`.

## Deploy to BentoCloud

Credentials resolve at build time from the `jfrog-build-credentials` secret. Log
in once, then run the deploy script:

```bash
uv run bentoml cloud login
./deploy.sh
```

`deploy.sh` renders `bento-deployment.yaml` (only the name is templated) and runs
`bentoml deployment apply`, which is an upsert — it creates the deployment the
first time and updates it in place on re-runs, so the script is idempotent.
Override the name with `DEPLOYMENT_NAME=other-name ./deploy.sh`.
