#!/usr/bin/env bash
set -u
printf '%s\n' 'READ_ONLY: reports the CURRENT machine only; no SSH, DDS or robot commands.'
uname -smr
if [ -r /proc/device-tree/model ]; then
  printf 'board_model: '
  tr -d '\000' < /proc/device-tree/model
  printf '\n'
fi
if [ -r /sys/class/dmi/id/product_name ]; then
  printf 'product_model: '
  cat /sys/class/dmi/id/product_name
fi
if [ -r /etc/os-release ]; then cat /etc/os-release; fi
if command -v free >/dev/null 2>&1; then free -h; fi
if [ -r /etc/nv_tegra_release ]; then cat /etc/nv_tegra_release; fi
for tool in python3 rustc cargo gcc protoc; do
  if command -v "$tool" >/dev/null 2>&1; then "$tool" --version 2>&1 | head -n 1;
  else printf '%s: not installed\n' "$tool"; fi
done
if [ -d /opt/ros ]; then printf 'ROS installations: '; ls /opt/ros; fi
if [ -d /sys/class/net ]; then printf 'interface names: '; ls /sys/class/net; fi
exit 0
