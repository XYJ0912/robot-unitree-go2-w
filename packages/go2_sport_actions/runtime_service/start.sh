#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
API_ROOT="$("${RBNX_BIN:-rbnx}" path robonix-api)"
test -f "$ROOT/rbnx-build/codegen/proto_gen/go2_sport_actions_pb2.py"
export PYTHONPATH="$API_ROOT:$ROOT:$ROOT/rbnx-build/codegen/proto_gen:${PYTHONPATH:-}"
exec "${RBNX_RUNTIME_PYTHON:-python3}" -m go2_sport_runtime.provider
