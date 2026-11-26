"""Validate launchable client snippets and coexistence with legacy settings."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import generate_config
try:
    import tomllib
except ImportError:
    tomllib = None


class ConfigTests(unittest.TestCase):
    def test_json_clients_launch_stdio_server_from_generated_arguments(self):
        for client in ("workbuddy", "claude", "generic"):
            with self.subTest(client=client):
                text = generate_config.build_config(client, sys.executable, ROOT / "server.py")
                entry = json.loads(text)["mcpServers"]["hydroglm_bridge"]
                self.assertNotIn("env", entry)
                self.assertNotIn("tool_timeout_sec", entry)
                self.assertNotIn("timeout", entry)
                run = subprocess.run([entry["command"], *entry["args"]],
                                     input='{"jsonrpc":"2.0","id":1,"method":"tools/list"}\n',
                                     text=True, encoding="utf-8", capture_output=True, check=True, timeout=10)
                self.assertEqual(json.loads(run.stdout)["result"]["tools"][0]["name"], "ask_hydroglm")

    @unittest.skipIf(tomllib is None, "TOML parser is available in Python 3.11+")
    def test_codex_fragment_can_coexist_with_legacy_entry(self):
        legacy = '[mcp_servers.hydroglm]\ncommand = "legacy-python"\nargs = ["legacy/server.py"]\n'
        new = generate_config.build_config("codex", sys.executable, ROOT / "server.py")
        combined = tomllib.loads(legacy + "\n" + new)
        self.assertEqual(combined["mcp_servers"]["hydroglm"], tomllib.loads(legacy)["mcp_servers"]["hydroglm"])
        self.assertEqual(combined["mcp_servers"]["hydroglm_bridge"]["tool_timeout_sec"], 660)

    def test_cli_writes_unicode_paths_and_refuses_accidental_overwrite(self):
        with tempfile.TemporaryDirectory(prefix="hydroglm-config-") as tmp:
            output = Path(tmp) / "配置 文件.json"
            command = [sys.executable, "-X", "utf8", str(ROOT / "generate_config.py"),
                       "--client", "workbuddy", "--output", str(output)]
            first = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", timeout=10)
            self.assertEqual(first.returncode, 0, first.stderr)
            original = output.read_bytes()
            second = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", timeout=10)
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual(output.read_bytes(), original)
            self.assertIn("hydroglm_bridge", json.loads(original)["mcpServers"])

    def test_invalid_name_or_missing_server_is_rejected(self):
        with self.assertRaises(ValueError):
            generate_config.build_config("generic", sys.executable, ROOT / "server.py", "bad.name")
        with self.assertRaises(ValueError):
            generate_config.build_config("generic", sys.executable, ROOT / "missing-server.py")

    def test_static_json_examples_parse_without_secrets(self):
        for path in (ROOT / "examples").glob("*.json"):
            text = path.read_text(encoding="utf-8")
            entry = json.loads(text)["mcpServers"]["hydroglm_bridge"]
            self.assertIn("server.py", entry["args"][-1])
            self.assertNotIn("sk-", text)


if __name__ == "__main__":
    unittest.main()
