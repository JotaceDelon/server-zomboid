"""Supervise the game, detect readiness, and send quit on systemd stop."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys


def configure_heap(install_dir, initial_mb, maximum_mb):
    path = Path(install_dir) / "ProjectZomboid64.json"
    config = json.loads(path.read_text(encoding="utf-8"))
    args = [arg for arg in config["vmArgs"] if not arg.startswith(("-Xms", "-Xmx"))]
    config["vmArgs"] = args + [f"-Xms{initial_mb}m", f"-Xmx{maximum_mb}m"]
    updated = json.dumps(config, indent=2) + "\n"
    if path.read_text(encoding="utf-8") != updated:
        path.write_text(updated, encoding="utf-8")


def run(config):
    ready = Path(config["ready_file"])
    ready.unlink(missing_ok=True)
    configure_heap(config["install_dir"], config["heap_initial_mb"], config["heap_max_mb"])
    child = None
    stopping = False

    def stop(_signal, _frame):
        nonlocal stopping
        stopping = True
        ready.unlink(missing_ok=True)
        if child is not None and child.poll() is None:
            try:
                child.stdin.write("quit\n")
                child.stdin.flush()
            except (BrokenPipeError, OSError):
                pass

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    try:
        child = subprocess.Popen(
            ["/bin/bash", "./start-server.sh", "-servername", config["server_name"],
             "-adminpassword", config["admin_password"]],
            cwd=config["install_dir"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
            start_new_session=True,
        )
        if stopping:
            stop(None, None)
        for line in child.stdout:
            # The game can log startup arguments. Avoid publishing the secret.
            print(line.replace(config["admin_password"], "[REDACTED]"), end="", flush=True)
            if "SERVER STARTED" in line and not stopping:
                ready.write_text(str(os.getpid()), encoding="ascii")
        result = child.wait()
        # Unexpected clean exit must also restart under Restart=on-failure.
        return result if stopping or result else 1
    finally:
        ready.unlink(missing_ok=True)


if __name__ == "__main__":
    settings = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    sys.exit(run(settings))
