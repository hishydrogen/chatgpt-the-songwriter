#!/usr/bin/env bash
# Use the installed Ubuntu studio from the Debian workspace.
set -euo pipefail
DOCKER=(env -u DOCKER_HOST -u DOCKER_CONTEXT -u DOCKER_TLS -u DOCKER_TLS_VERIFY -u DOCKER_CERT_PATH docker --host=unix:///var/run/docker.sock)
if [[ "$("${DOCKER[@]}" inspect --format '{{.State.Running}}' songwriter-studio)" != true ]]; then
  "${DOCKER[@]}" start songwriter-studio >/dev/null
fi
tty_flags=(-i)
if [[ -t 0 && -t 1 ]]; then tty_flags+=(-t); fi
cmd=(/opt/songwriter-venv/bin/python -m songwriter)
if [[ "${1:-}" == --python ]]; then
  shift
  cmd=(/opt/songwriter-venv/bin/python)
fi
exec "${DOCKER[@]}" exec "${tty_flags[@]}" --user "$(id -u):$(id -g)" \
  -e PATH=/opt/songwriter-venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
  -e HOME=/tmp/songwriter-home -e MPLCONFIGDIR=/tmp/songwriter-matplotlib-user \
  -e PYTHONPATH=/workspace/chatgpt-the-songwriter \
  -e SSL_CERT_FILE=/run/songwriter-ca.crt -e REQUESTS_CA_BUNDLE=/run/songwriter-ca.crt \
  -e PIP_CERT=/run/songwriter-ca.crt -e GIT_SSL_CAINFO=/run/songwriter-ca.crt \
  songwriter-studio "${cmd[@]}" "$@"
