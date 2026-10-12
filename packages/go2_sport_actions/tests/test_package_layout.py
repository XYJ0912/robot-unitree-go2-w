# SPDX-License-Identifier: Apache-2.0
"""Public provider boundaries and the shared service's wire compatibility."""
from pathlib import Path
import unittest
import yaml

from go2_sport_actions.skills import DEFINITIONS

ROOT = Path(__file__).resolve().parents[1]


class PackageLayoutTests(unittest.TestCase):
    def test_skill_package_publishes_only_seven_namespaces(self):
        manifest = yaml.safe_load((ROOT / "package_manifest.yaml").read_text())
        caps = manifest["capabilities"]
        self.assertEqual(len(caps), 28)
        self.assertEqual({c["name"].rsplit("/", 1)[0] for c in caps},
                         {d["namespace"] for d in DEFINITIONS})
        for cap in caps:
            contract = (ROOT / cap["path"]).read_text()
            self.assertIn('id = "' + cap["name"] + '"', contract)
        alias = ROOT / "package_manifest.catalog.yaml"
        if alias.exists():
            self.assertEqual(yaml.safe_load(alias.read_text()), manifest)

    def test_service_is_a_separate_package_without_skill_contracts(self):
        root = ROOT / "runtime_service"
        manifest = yaml.safe_load((root / "package_manifest.yaml").read_text())
        self.assertEqual(manifest["package"]["name"], "robonix.service.unitree.go2.sport_runtime")
        self.assertEqual(len(manifest["capabilities"]), 4)
        for cap in manifest["capabilities"]:
            self.assertTrue(cap["name"].startswith("robonix/service/unitree_go2_sport_runtime/"))
            self.assertTrue((root / cap["path"]).is_file())

    def test_consumer_and_service_idl_agree(self):
        for name in ("ExecuteAction", "GetActionStatus", "CancelAction"):
            relative = Path("capabilities/lib/go2_sport_actions/srv") / (name + ".srv")
            self.assertEqual((ROOT / relative).read_bytes(),
                             (ROOT / "runtime_service" / relative).read_bytes())

    def test_deployments_resolve_the_separate_service(self):
        for name in ("seven-skills.yaml", "offline-seven-skills.yaml"):
            manifest = yaml.safe_load((ROOT / "examples" / name).read_text())
            service = manifest["service"][0]
            self.assertEqual(service["path"], "${GO2_SKILL_DIR}/runtime_service")
            self.assertNotIn("manifest", service)
            self.assertEqual(len(manifest["skill"]), 7)


if __name__ == "__main__":
    unittest.main()
