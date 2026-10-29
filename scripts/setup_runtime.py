"""Download pinned, checksum-verified CPU inference assets from their publishers.

Run once with Python 3.11+. Assets stay in .runtime/ and are not project data.
No API key, account, package manager, or administrator privilege is required.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
from pathlib import Path
import shutil
import sys
import tarfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".runtime"
RELEASE = "b11669"
MODEL_NAME = "qwen2.5-0.5b-instruct-q4_k_m.gguf"
MODEL_SHA = "74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db"
MODEL_URL = "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/" + MODEL_NAME
ASSETS = {
    "Windows": ("llama-b11669-bin-win-cpu-x64.zip", "37b3efcf962847ca869745fd4ccf7f5e7e8dacfeff9fa3523b4ca8cdc66d632b"),
    "Linux": ("llama-b11669-bin-ubuntu-x64.tar.gz", "cf07c1c112d709bd67e522017471de57ed0ec8bea031d732c5422351c07f65ac"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def download(url: str, target: Path, checksum: str, limit: int) -> None:
    if target.is_file() and sha256(target) == checksum:
        print(f"Verified cached {target.name}", flush=True)
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_suffix(target.suffix + ".partial")
    request = urllib.request.Request(url, headers={"User-Agent": "KIUA2003-InnlandetAirBrief-Setup/0.1"})
    count = 0
    try:
        with urllib.request.urlopen(request, timeout=60) as response, partial.open("wb") as output:
            while block := response.read(1024 * 1024):
                count += len(block)
                if count > limit:
                    raise ValueError("Download exceeds its size limit")
                output.write(block)
        if sha256(partial) != checksum:
            raise ValueError(f"Checksum mismatch for {target.name}; refusing to use it")
        partial.replace(target)
        print(f"Downloaded and verified {target.name} ({count:,} bytes)", flush=True)
    finally:
        partial.unlink(missing_ok=True)


def safe_destination(base: Path, name: str) -> Path:
    path = (base / name).resolve()
    if not path.is_relative_to(base.resolve()):
        raise ValueError("Archive contains an unsafe path")
    return path


def unpack(archive: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    if archive.suffix == ".zip":
        with zipfile.ZipFile(archive) as source:
            for member in source.infolist():
                safe_destination(destination, member.filename)
                # This Windows publisher archive requires no symlink extraction.
                if (member.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError("Unexpected symlink in ZIP")
            source.extractall(destination)
    else:
        with tarfile.open(archive) as source:
            for member in source.getmembers():
                target = safe_destination(destination, member.name)
                if member.issym():
                    safe_destination(destination, str(target.parent.relative_to(destination.resolve()) / member.linkname))
                elif member.islnk():
                    safe_destination(destination, member.linkname)
                elif not (member.isfile() or member.isdir()):
                    raise ValueError("Unexpected special file in archive")
            # All paths and link targets have been checked for Python 3.11 support.
            if hasattr(tarfile, "data_filter"):
                source.extractall(destination, filter="data")
            else:
                source.extractall(destination)


def main() -> int:
    system = platform.system()
    machine = platform.machine().lower()
    if system not in ASSETS or machine not in {"x86_64", "amd64"}:
        print("This helper supports Windows x64 and Linux x64. See README for manual localhost setup.", file=sys.stderr)
        return 2
    archive_name, runtime_sha = ASSETS[system]
    archive = RUNTIME / "downloads" / archive_name
    runtime_url = f"https://github.com/ggml-org/llama.cpp/releases/download/{RELEASE}/{archive_name}"
    download(runtime_url, archive, runtime_sha, 30 * 1024 * 1024)
    binary_name = "llama-server.exe" if system == "Windows" else "llama-server"
    binaries = list((RUNTIME / "bin").rglob(binary_name)) if (RUNTIME / "bin").exists() else []
    if not binaries:
        unpack(archive, RUNTIME / "bin")
        binaries = list((RUNTIME / "bin").rglob(binary_name))
    if len(binaries) != 1:
        raise ValueError("Expected exactly one llama-server executable")
    model = RUNTIME / "models" / MODEL_NAME
    download(MODEL_URL, model, MODEL_SHA, 510 * 1024 * 1024)
    manifest = {
        "runtime_release": RELEASE,
        "runtime_sha256": runtime_sha,
        "runtime_download": runtime_url,
        "model_download": MODEL_URL,
        "model_sha256": MODEL_SHA,
        "binary": str(binaries[0].relative_to(ROOT)),
        "model": str(model.relative_to(ROOT)),
        "platform": system,
    }
    (RUNTIME / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("Local CPU runtime ready. Model and runtime downloads total about 510 MB.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, zipfile.BadZipFile, tarfile.TarError) as exc:
        print(f"Setup failed: {exc}", file=sys.stderr)
        raise SystemExit(2)
