#!/usr/bin/env bash
set -euo pipefail
pkg_root="${RBNX_PACKAGE_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
rbnx_bin="${RBNX_BIN:-rbnx}"
repo_root="${ROBONIX_REPO:-$(cd "$pkg_root/../../../../../robonix" && pwd)}"
venv="$pkg_root/rbnx-build/venv"
cd "$pkg_root"
if [[ ! -d "$venv" ]]; then uv venv "$venv"; fi
uv pip install --python "$venv/bin/python" -e "$repo_root/pylib/robonix-api[codegen]" -e "$pkg_root"
export ROBONIX_HOME="$pkg_root/rbnx-build/robonix-home"
"$rbnx_bin" setup "$repo_root"
RBNX_CODEGEN_PYTHON="$venv/bin/python" "$rbnx_bin" codegen -p "$pkg_root" --mcp
PYTHONPATH="$pkg_root:$pkg_root/rbnx-build/codegen/proto_gen:$pkg_root/rbnx-build/codegen/robonix_mcp_types" \
  "$venv/bin/python" -c 'import go2w_camera_snapshot.driver; print("go2w camera runtime imports OK")'
