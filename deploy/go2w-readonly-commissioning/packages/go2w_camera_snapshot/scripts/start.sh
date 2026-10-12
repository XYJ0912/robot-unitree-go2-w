#!/usr/bin/env bash
set -euo pipefail
pkg_root="${RBNX_PACKAGE_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
cd "$pkg_root"
export PYTHONPATH="$pkg_root:$pkg_root/rbnx-build/codegen/proto_gen:$pkg_root/rbnx-build/codegen/robonix_mcp_types${PYTHONPATH:+:$PYTHONPATH}"
exec "$pkg_root/rbnx-build/venv/bin/python" -m go2w_camera_snapshot.driver
