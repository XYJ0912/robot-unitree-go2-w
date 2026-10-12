"""Expose one verified Go2W camera read as the existing snapshot capability."""

from __future__ import annotations

from io import BytesIO
import os
from pathlib import Path
import subprocess

from PIL import Image as PillowImage
from robonix_api import Err, Ok, Primitive

import builtin_interfaces_mcp
import std_msgs_mcp
from sensor_msgs_mcp import Image
from std_msgs_mcp import Empty


camera = Primitive(id="go2w_camera_snapshot", namespace="robonix/primitive/camera")
_interface = ""
_capture_bin = Path("")


def _capture() -> Image:
    result = subprocess.run(
        [str(_capture_bin), _interface, "--jpeg-stdout"],
        capture_output=True,
        timeout=4,
        check=False,
    )
    if result.returncode or not result.stdout.startswith(b"\xff\xd8") or not result.stdout.endswith(b"\xff\xd9"):
        raise RuntimeError(f"Go2W camera read failed (exit={result.returncode})")
    if len(result.stdout) > 4 * 1024 * 1024:
        raise RuntimeError("Go2W JPEG exceeds 4 MiB limit")
    with PillowImage.open(BytesIO(result.stdout)) as jpeg:
        jpeg.verify()
    with PillowImage.open(BytesIO(result.stdout)) as jpeg:
        if jpeg.width <= 0 or jpeg.height <= 0 or jpeg.width * jpeg.height > 1920 * 1080:
            raise RuntimeError("Go2W image dimensions exceed read-only limit")
        rgb = jpeg.convert("RGB")
        width, height = rgb.size
        pixels = rgb.tobytes()
    # The SDK image response has no verified source timestamp or optical frame.
    header = std_msgs_mcp.Header(
        stamp=builtin_interfaces_mcp.Time(sec=0, nanosec=0),
        frame_id="",
    )
    return Image(
        header=header,
        width=width,
        height=height,
        encoding="rgb8",
        is_bigendian=0,
        step=width * 3,
        data=pixels,
    )


@camera.mcp("robonix/primitive/camera/snapshot")
def snapshot(_request: Empty) -> Image:
    return _capture()


@camera.on_init
def init(cfg):
    global _interface, _capture_bin
    if os.environ.get("GO2_ALLOW_MOTION", "false").lower() != "false":
        return Err("GO2_ALLOW_MOTION must remain false")
    _interface = str(cfg.get("network_interface", ""))
    _capture_bin = Path(str(cfg.get("capture_bin", "")))
    if _interface != "enp131s0" or not _capture_bin.is_file() or not os.access(_capture_bin, os.X_OK):
        return Err("verified interface or capture binary missing")
    try:
        _capture()
    except (OSError, RuntimeError, subprocess.TimeoutExpired, ValueError) as error:
        return Err(str(error))
    return Ok()


if __name__ == "__main__":
    camera.run()
