import importlib.util
import io
import json
from pathlib import Path
import signal
import tempfile
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location(
    "supervisor", Path(__file__).resolve().parents[1] / "Ansible/files/run-server.py"
)
supervisor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(supervisor)


class SupervisorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.launcher = self.root / "ProjectZomboid64.json"
        self.launcher.write_text(json.dumps({
            "mainClass": "keep.me", "vmArgs": ["-Xmx8g", "-Xms2g", "-Dfoo=bar"]
        }), encoding="utf-8")
        self.config = {
            "install_dir": str(self.root), "server_name": "alexandria",
            "admin_password": "private-test-secret", "heap_initial_mb": 512,
            "heap_max_mb": 4096, "ready_file": str(self.root / "ready"),
        }

    def test_heap_preserves_other_launcher_options_and_is_idempotent(self):
        supervisor.configure_heap(self.root, 512, 4096)
        content = self.launcher.read_text(encoding="utf-8")
        parsed = json.loads(content)
        self.assertEqual(parsed["mainClass"], "keep.me")
        self.assertEqual(parsed["vmArgs"], ["-Dfoo=bar", "-Xms512m", "-Xmx4096m"])
        with patch.object(Path, "write_text") as write:
            supervisor.configure_heap(self.root, 512, 4096)
            write.assert_not_called()

    def test_ready_only_after_marker_and_stop_requests_quit(self):
        ready = Path(self.config["ready_file"])
        ready.write_text("stale", encoding="ascii")
        handlers = {}
        stdin = io.StringIO()

        def output():
            self.assertFalse(ready.exists())
            yield "Starting private-test-secret\n"
            self.assertFalse(ready.exists())
            yield "*** SERVER STARTED ****\n"
            self.assertTrue(ready.exists())
            handlers[signal.SIGTERM](signal.SIGTERM, None)
            self.assertFalse(ready.exists())
            yield "Saved world\n"

        class Process:
            def __init__(self):
                self.stdin = stdin
                self.stdout = output()

            def poll(self):
                return None

            def wait(self):
                return 0

        logged = io.StringIO()
        with patch.object(supervisor.signal, "signal", side_effect=lambda sig, fn: handlers.update({sig: fn})), \
             patch.object(supervisor.subprocess, "Popen", return_value=Process()) as start, \
             patch("sys.stdout", logged):
            result = supervisor.run(self.config)
        self.assertEqual(result, 0)
        self.assertEqual(stdin.getvalue(), "quit\n")
        self.assertFalse(ready.exists())
        self.assertNotIn(self.config["admin_password"], logged.getvalue())
        self.assertIn("[REDACTED]", logged.getvalue())
        self.assertIn("alexandria", start.call_args.args[0])

    def test_unexpected_clean_exit_is_failure_and_cleans_readiness(self):
        class Process:
            stdout = ["*** SERVER STARTED ****\n"]

            def wait(self):
                return 0

        with patch.object(supervisor.signal, "signal"), \
             patch.object(supervisor.subprocess, "Popen", return_value=Process()), \
             patch("sys.stdout", io.StringIO()):
            self.assertEqual(supervisor.run(self.config), 1)
        self.assertFalse(Path(self.config["ready_file"]).exists())


if __name__ == "__main__":
    unittest.main()
