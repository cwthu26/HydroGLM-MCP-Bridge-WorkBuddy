"""Check hidden-input credential persistence without using real credentials."""
import contextlib
import io
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import configure_key


class CredentialTests(unittest.TestCase):
    def save(self, directory, agent, key):
        output = io.StringIO()
        with patch.object(configure_key, "config_dir", return_value=directory), \
                patch.object(configure_key.getpass, "getpass", return_value=key), \
                patch.object(sys, "argv", ["configure_key.py", "--agent", agent]), \
                contextlib.redirect_stdout(output):
            self.assertEqual(configure_key.main(), 0)
        self.assertNotIn(key, output.getvalue())
        return output.getvalue()

    def test_saving_plus_retains_legacy_hydroglm_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "credentials"
            self.save(directory, "HydroGLM", "sk-offline-one")
            self.save(directory, "HydroGLM-plus", "sk-offline-two")
            file = directory / "credentials.json"
            data = json.loads(file.read_text(encoding="utf-8"))
            self.assertEqual(data, {"hydroglm": "sk-offline-one", "hydroglm_plus": "sk-offline-two"})
            if os.name != "nt":
                self.assertEqual(stat.S_IMODE(file.stat().st_mode), 0o600)

    def test_windows_branch_avoids_unix_fchmod(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "windows-credentials"
            with patch.object(configure_key.os, "name", "nt"), \
                    patch.object(configure_key.os, "fchmod", create=True,
                                 side_effect=AssertionError("Unix-only fchmod must not run")):
                output = self.save(directory, "HydroGLM", "sk-offline-windows")
            self.assertIn("Windows", output)
            self.assertTrue((directory / "credentials.json").is_file())


if __name__ == "__main__":
    unittest.main()
