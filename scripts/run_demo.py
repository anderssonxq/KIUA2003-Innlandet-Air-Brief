"""Start the pinned local model, run all pipeline stages, then stop our server.

The model must first be downloaded with scripts/setup_runtime.py. A server
already running at the configured loopback URL is reused, never terminated.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def healthy(base: str) -> bool:
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(base + "/health", timeout=2) as response:
            data = json.load(response)
        return data.get("status") == "ok"
    except (OSError, ValueError):
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=("fixture", "live"), default="fixture")
    parser.add_argument("--date", default="2026-10-28")
    parser.add_argument("--as-of", default=None)
    parser.add_argument("--output", default="data/output/demo")
    args = parser.parse_args()
    # Historical fixtures are explicitly dated; live mode uses the real clock.
    as_of = args.as_of or ("2026-10-27T16:25:25Z" if args.source == "fixture" else None)
    base = os.environ.get("LOCAL_LLM_URL", "http://127.0.0.1:8080").rstrip("/")
    parsed = urllib.parse.urlsplit(base)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost"} or parsed.path or parsed.query or parsed.username:
        raise ValueError("LOCAL_LLM_URL must be a plain loopback HTTP base URL")
    process = None
    log = None
    try:
        if not healthy(base):
            manifest_path = ROOT / ".runtime" / "manifest.json"
            if not manifest_path.is_file():
                raise ValueError("Run python scripts/setup_runtime.py first")
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            binary = ROOT / manifest["binary"]
            model = ROOT / manifest["model"]
            log = (ROOT / ".runtime" / "server.log").open("w", encoding="utf-8")
            command = [str(binary), "-m", str(model), "--host", "127.0.0.1", "--port", str(parsed.port or 8080),
                       "--ctx-size", "4096", "--parallel", "1", "--threads", "4", "--n-predict", "256",
                       "--no-ui", "--offline"]
            process = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
            deadline = time.monotonic() + 60
            while not healthy(base):
                if process.poll() is not None:
                    raise ValueError("Model server failed; inspect .runtime/server.log")
                if time.monotonic() >= deadline:
                    raise ValueError("Model startup timed out after 60 seconds")
                time.sleep(0.25)
            print("Started pinned local model on loopback.", flush=True)
        else:
            print("Reusing a healthy local model server.", flush=True)
        command = [sys.executable, "-m", "src.pipeline", "--source", args.source, "--date", args.date, "--output", args.output]
        if as_of:
            command.extend(["--as-of", as_of])
        result = subprocess.run(command, cwd=ROOT, check=False)
        if result.returncode:
            return result.returncode
        verification = [sys.executable, "-m", "src.verify", "--output", args.output]
        return subprocess.run(verification, cwd=ROOT, check=False).returncode
    finally:
        if process is not None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        if log is not None:
            log.close()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as exc:
        print(f"Demo failed: {exc}", file=sys.stderr)
        raise SystemExit(2)
