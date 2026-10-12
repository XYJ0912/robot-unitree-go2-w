from __future__ import annotations

from io import BytesIO
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

from PIL import Image as PillowImage

from go2w_camera_snapshot import driver


def jpeg_fixture() -> bytes:
    output = BytesIO()
    PillowImage.new("RGB", (4, 3), (10, 20, 30)).save(output, format="JPEG")
    return output.getvalue()


class CameraSnapshotTests(unittest.TestCase):
    def setUp(self):
        driver._capture_bin = Path("/tmp/go2w-camera-test")
        driver._interface = "enp131s0"

    def test_rgb8_shape_and_unknown_source_header(self):
        result = subprocess.CompletedProcess([], 0, jpeg_fixture(), b"")
        with patch.object(driver.subprocess, "run", return_value=result) as run:
            image = driver._capture()
        run.assert_called_once()
        self.assertEqual(run.call_args.args[0], ["/tmp/go2w-camera-test", "enp131s0", "--jpeg-stdout"])
        self.assertEqual((image.width, image.height, image.step), (4, 3, 12))
        self.assertEqual(image.encoding, "rgb8")
        self.assertEqual(len(image.data), 36)
        self.assertEqual(image.header.stamp.sec, 0)
        self.assertEqual(image.header.frame_id, "")

    def test_rejects_invalid_jpeg(self):
        result = subprocess.CompletedProcess([], 0, b"not a jpeg", b"")
        with patch.object(driver.subprocess, "run", return_value=result):
            with self.assertRaises(RuntimeError):
                driver._capture()

    def test_rejects_oversized_decoded_image(self):
        output = BytesIO()
        PillowImage.new("RGB", (1921, 1080)).save(output, format="JPEG")
        result = subprocess.CompletedProcess([], 0, output.getvalue(), b"")
        with patch.object(driver.subprocess, "run", return_value=result):
            with self.assertRaises(RuntimeError):
                driver._capture()


if __name__ == "__main__":
    unittest.main()
