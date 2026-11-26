"""Exercise the stdio contract and upstream request without network access."""
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import server


class BridgeTests(unittest.TestCase):
    def test_stdio_initialization_discovery_and_ping(self):
        messages = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05"}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {"jsonrpc": "2.0", "id": 3, "method": "ping"},
        ]
        payload = "".join(json.dumps(m) + "\n" for m in messages)
        run = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "server.py")],
                             input=payload, text=True, encoding="utf-8", capture_output=True,
                             check=True, timeout=10)
        replies = [json.loads(line) for line in run.stdout.splitlines()]
        self.assertEqual([r["id"] for r in replies], [1, 2, 3])
        self.assertEqual(replies[0]["result"]["serverInfo"]["name"], "hydroglm-mcp-bridge")
        tool = replies[1]["result"]["tools"][0]
        self.assertEqual(tool["name"], "ask_hydroglm")
        self.assertEqual(tool["inputSchema"]["required"], ["question"])
        self.assertNotIn("Codex", tool["description"])
        self.assertNotIn("Codex", replies[0]["result"]["instructions"])
        self.assertEqual(run.stderr, "")

    def test_existing_tool_parameters_and_session_are_forwarded(self):
        response = MagicMock()
        response.read.return_value = json.dumps({
            "choices": [{"message": {"content": "专业建议"}}], "session_id": 42,
        }).encode("utf-8")
        response.__enter__.return_value = response
        arguments = {"question": "水库调度", "agent": "HydroGLM-plus",
                     "web_search": False, "enable_thinking": False, "session_id": 7}
        with patch.object(server, "read_api_key", return_value="sk-offline-fixture"), \
                patch.object(server.urllib.request, "urlopen", return_value=response) as request:
            answer = server.call_hydroglm(arguments)
        payload = json.loads(request.call_args.args[0].data)
        self.assertEqual(payload["model"], "HydroGLM-plus")
        self.assertEqual(payload["session_id"], 7)
        self.assertIs(payload["stream"], False)
        self.assertIs(payload["web_search"], False)
        self.assertEqual(payload["messages"][0]["content"], "水库调度")
        self.assertEqual(request.call_args.kwargs["timeout"], 600)
        self.assertIn("专业建议", answer)
        self.assertIn("session_id: 42", answer)

    def test_invalid_arguments_do_not_call_upstream(self):
        invalid = [{}, {"question": "x", "agent": "unknown"},
                   {"question": "x", "web_search": "false"},
                   {"question": "x", "session_id": True}]
        with patch.object(server.urllib.request, "urlopen") as request:
            for arguments in invalid:
                result = server.handle_request({"jsonrpc": "2.0", "id": 4, "method": "tools/call",
                                                "params": {"name": "ask_hydroglm", "arguments": arguments}})
                self.assertTrue(result["result"]["isError"])
            request.assert_not_called()

    def test_connection_error_does_not_expose_key(self):
        with patch.object(server, "read_api_key", return_value="sk-offline-fixture"), \
                patch.object(server.urllib.request, "urlopen", side_effect=TimeoutError):
            result = server.handle_request({"jsonrpc": "2.0", "id": 5, "method": "tools/call",
                                            "params": {"name": "ask_hydroglm", "arguments": {"question": "test"}}})
        self.assertTrue(result["result"]["isError"])
        self.assertNotIn("sk-offline-fixture", json.dumps(result))


if __name__ == "__main__":
    unittest.main()
