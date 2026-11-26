"""Release checks are separate from the normal MCP service."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build_release
import server


class ReleaseTests(unittest.TestCase):
    def test_known_protocols_and_unknown_version_negotiation(self):
        for version in (*server.SUPPORTED_PROTOCOL_VERSIONS, "2099-01-01"):
            with self.subTest(version=version):
                response = server.handle_request({
                    "jsonrpc": "2.0", "id": 1, "method": "initialize",
                    "params": {"protocolVersion": version},
                })["result"]
                expected = version if version in server.SUPPORTED_PROTOCOL_VERSIONS else "2025-06-18"
                self.assertEqual(response["protocolVersion"], expected)
                self.assertEqual(response["serverInfo"]["version"], server.SERVER_VERSION)

    def test_all_local_markdown_links_point_to_packaged_files(self):
        files = build_release.release_files()
        included = {path.relative_to(ROOT).as_posix() for path in files}
        for path in files:
            if path.suffix == ".md":
                with self.subTest(path=path.name):
                    build_release.check_markdown(path, path.read_text(encoding="utf-8"), included=included)

    def test_possible_secret_stops_packaging_without_echoing_it(self):
        secret = "sk-" + "x" * 80
        with self.assertRaises(ValueError) as caught:
            build_release.validate_content("sample.txt", secret.encode())
        self.assertNotIn(secret, str(caught.exception))

    def test_broken_link_is_detected(self):
        with self.assertRaisesRegex(ValueError, "Broken local link"):
            build_release.check_markdown(ROOT / "README.md", "[missing](not-a-real-file.md)")

    def test_source_zip_has_no_generated_configs_or_credentials(self):
        with tempfile.TemporaryDirectory() as directory:
            report = build_release.build(Path(directory))
            with zipfile.ZipFile(Path(directory) / report["archive"]) as archive:
                self.assertIsNone(archive.testzip())
                names = archive.namelist()
                self.assertIn("HydroGLM-MCP-Bridge/docs/MCP原理与调用场景.md", names)
                self.assertIn("HydroGLM-MCP-Bridge/install_hydroglm_dsh.py", names)
                self.assertIn("HydroGLM-MCP-Bridge/skills/hydroglm-consult/SKILL.md", names)
                self.assertIn("HydroGLM-MCP-Bridge/tests/test_credentials.py", names)
                for name in names:
                    self.assertFalse(Path(name).name.startswith("local."))
                    self.assertNotEqual(Path(name).name, "credentials.json")
                    self.assertNotIn("__pycache__", name)
                self.assertEqual(len(names), report["file_count"])
            manifest = Path(directory) / f"HydroGLM-MCP-Bridge-v{server.SERVER_VERSION}.manifest.json"
            self.assertEqual(json.loads(manifest.read_text(encoding="utf-8")), report)
            with self.assertRaisesRegex(ValueError, "already exist"):
                build_release.build(Path(directory))


if __name__ == "__main__":
    unittest.main()
