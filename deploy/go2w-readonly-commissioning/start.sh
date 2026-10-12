#!/usr/bin/env bash
set -euo pipefail
deploy_dir="$(cd "$(dirname "$0")" && pwd)"
export ROBONIX_DEPLOY_DIR="$deploy_dir"
export GO2_ALLOW_MOTION=false
export ROBONIX_HOME="$deploy_dir/rbnx-build/robonix-home"
rbnx_bin="${RBNX_BIN:-rbnx}"
test -x "$deploy_dir/build/go2w_camera_probe" || {
  echo "Go2W camera probe missing; run bash build.sh first" >&2
  exit 1
}
exec "$rbnx_bin" boot -f "$deploy_dir/robonix_manifest.yaml" --no-update-check
