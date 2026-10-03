#!/usr/bin/env bash
# Run inside the Ubuntu 24.04 songwriter container.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
export SSL_CERT_FILE=/run/songwriter-ca.crt
export REQUESTS_CA_BUNDLE="$SSL_CERT_FILE"
export PIP_CERT="$SSL_CERT_FILE"
export GIT_SSL_CAINFO="$SSL_CERT_FILE"
export MPLCONFIGDIR=/tmp/songwriter-matplotlib
apt-get -o Acquire::https::CaInfo="$SSL_CERT_FILE" update -qq
apt-get -o Acquire::https::CaInfo="$SSL_CERT_FILE" install -y --no-install-recommends ca-certificates python3 python3-dev python3-venv curl unzip >/dev/null
python3 -m venv /opt/songwriter-venv
export PATH="/opt/songwriter-venv/bin:$PATH"
python -m pip install --upgrade pip
# Limit compilation memory on the 10 GB worker.
mkdir -p /opt/songwriter-bin
printf '#!/bin/sh\nprintf "4\\n"\n' > /opt/songwriter-bin/nproc
chmod +x /opt/songwriter-bin/nproc
export PATH="/opt/songwriter-bin:$PATH"
cd /workspace/chatgpt-the-songwriter
bash scripts/setup.sh
workspace_owner="$(stat -c '%u:%g' .)"
mkdir -p /tmp/songwriter-home
chown -R "$workspace_owner" libs /tmp/songwriter-home
