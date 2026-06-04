#!/usr/bin/env bash
# Render bento-deployment.yaml and apply it to BentoCloud. `apply` is an upsert:
# it creates the deployment if it's new and updates it in place if it already
# exists, so re-running this is safe.
set -euo pipefail

cd "$(dirname "$0")"

DEPLOYMENT_NAME="${DEPLOYMENT_NAME:-hello-spear-dsp}"
export DEPLOYMENT_NAME

rendered="$(mktemp -t bento-deployment.XXXXXX.yaml)"
trap 'rm -f "$rendered"' EXIT

envsubst < bento-deployment.yaml > "$rendered"
uv run bentoml deployment apply -f "$rendered"
