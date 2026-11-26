"""Regression checks for DSH profile edits and migration."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DshTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name) / "DSH 测试"
        self.config = self.home / "profiles" / "web" / "cordis.patch.yml"
        self.config.parent.mkdir(parents=True)
        self.env = {**os.environ, "XDG_CONFIG_HOME": temporary.name, "PYTHONIOENCODING": "utf-8",
                    "HANHAI_HYDROGLM_API_KEY": "offline-placeholder"}

    def run_script(self, script, *args):
        return subprocess.run(
            [sys.executable, str(ROOT / script), "--dsh-home", str(self.home),
             "--profile", "web", *args],
            cwd=self.home, env=self.env, timeout=10, capture_output=True,
            encoding="utf-8",
        )

    def test_installs_without_changing_existing_persona_and_is_repeatable(self):
        original = b"- id: system-prompt\r\n  config:\r\n    personaSuffix: keep existing\r\n"
        self.config.write_bytes(original)
        install = self.run_script("install_hydroglm_dsh.py")
        self.assertEqual(install.returncode, 0, install.stderr)
        installed = self.config.read_bytes()
        self.assertTrue(installed.startswith(original))
        self.assertIn(b"serverName: hydroglm\r\n", installed)
        backup, = self.config.parent.glob("cordis.patch.yml.bak-*")
        self.assertEqual(backup.read_bytes(), original)

        repeat = self.run_script("install_hydroglm_dsh.py")
        self.assertEqual(repeat.returncode, 0, repeat.stderr)
        self.assertEqual(self.config.read_bytes(), installed)
        self.assertEqual(list(self.config.parent.glob("cordis.patch.yml.bak-*")), [backup])
        verify = self.run_script("verify_hydroglm_dsh.py")
        self.assertEqual(verify.returncode, 0, verify.stdout + verify.stderr)
        self.assertNotIn(self.env["HANHAI_HYDROGLM_API_KEY"], verify.stdout)

    def test_empty_patch_list_can_be_installed(self):
        self.config.write_text("# User patches\n[] # Initially empty\n", encoding="utf-8")
        result = self.run_script("install_hydroglm_dsh.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("# Initially empty", self.config.read_text(encoding="utf-8"))
        self.assertNotIn("[] # Initially empty", self.config.read_text(encoding="utf-8"))

    def test_existing_legacy_registration_is_preserved(self):
        original = "- insert:\n    - id: mcp-hydroglm\n      config: {serverName: hydroglm}\n"
        for config in (self.config, self.home / "cordis.patch.yml"):
            with self.subTest(config=config):
                config.write_text(original, encoding="utf-8")
                result = self.run_script("install_hydroglm_dsh.py")
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(config.read_text(encoding="utf-8"), original)
                self.assertFalse((self.home / "skills").exists())
                config.unlink()


if __name__ == "__main__":
    unittest.main()
