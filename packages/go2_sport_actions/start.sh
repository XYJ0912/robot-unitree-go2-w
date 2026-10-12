#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
API_ROOT="$("${RBNX_BIN:-rbnx}" path robonix-api)"
test -f "$ROOT/rbnx-build/codegen/robonix_mcp_types/go2_sport_actions_mcp.py"
export PYTHONPATH="$API_ROOT:$ROOT:$ROOT/rbnx-build/codegen/proto_gen:$ROOT/rbnx-build/codegen/robonix_mcp_types:${PYTHONPATH:-}"
# Per-action selection remains until upstream robonix#276 supports RBNX_PROVIDES.
if [[ $# != 1 ]]; then
  echo "Use examples/seven-skills.yaml with one per-action manifest per Skill." >&2
  exit 2
fi
exec "${RBNX_RUNTIME_PYTHON:-python3}" -m go2_sport_actions.action_provider "$1"
