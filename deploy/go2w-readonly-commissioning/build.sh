#!/usr/bin/env bash
set -euo pipefail
deploy_dir="$(cd "$(dirname "$0")" && pwd)"
export ROBONIX_DEPLOY_DIR="$deploy_dir"
export GO2_ALLOW_MOTION=false
export ROBONIX_HOME="$deploy_dir/rbnx-build/robonix-home"
export UV_CACHE_DIR="$deploy_dir/rbnx-build/uv-cache"
rbnx_bin="${RBNX_BIN:-rbnx}"
cmake -S "$deploy_dir" -B "$deploy_dir/build" \
  -DCMAKE_PREFIX_PATH="${UNITREE_SDK2_PREFIX:-$deploy_dir/../../../../third_party/unitree_sdk2/install}"
cmake --build "$deploy_dir/build" -j2
"$rbnx_bin" setup "${ROBONIX_REPO:-$deploy_dir/../../../robonix}"
"$rbnx_bin" build -f "$deploy_dir/robonix_manifest.yaml" --no-update-check
