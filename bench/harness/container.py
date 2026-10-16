"""Host-side wrapper for running one repetition inside the pinned container.

One `docker run` per repetition, per docs/EVALUATION.md's isolation rule:
a fresh container, CPU-pinned, no auxiliary files other than what this
module stages into the mounted directory beforehand.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

DEFAULT_IMAGE = "auxflow-bench:v1"

_digest_cache: dict[str, str] = {}


def image_digest(image: str = DEFAULT_IMAGE) -> str:
    """The pinned image's content digest, recorded in every JSONL record."""
    if image in _digest_cache:
        return _digest_cache[image]
    proc = subprocess.run(
        ["docker", "inspect", image, "--format", "{{.Id}}"],
        capture_output=True,
        text=True,
        check=True,
    )
    digest = proc.stdout.strip()
    _digest_cache[image] = digest
    return digest


def run_in_container(
    host_dir: Path,
    workdir_rel: str,
    command: list[str],
    *,
    image: str = DEFAULT_IMAGE,
    env: dict[str, str] | None = None,
    cpus: str = "1",
    memory: str = "768m",
    timeout: int = 180,
) -> tuple[int, str, str, float]:
    """Run `command` inside one fresh container, cwd `/work/<workdir_rel>`.

    Returns (returncode, stdout, stderr, wall_clock_ms). `host_dir` is
    mounted read-write at /work so results are visible on the host after
    the container exits. A memory cap keeps one stray repetition from
    starving its siblings on a shared host.
    """
    docker_cmd = [
        "docker",
        "run",
        "--rm",
        f"--cpus={cpus}",
        f"--memory={memory}",
        "--network=none",
        "-v",
        f"{host_dir.resolve()}:/work",
        "-w",
        f"/work/{workdir_rel}" if workdir_rel else "/work",
    ]
    for key, value in (env or {}).items():
        docker_cmd += ["-e", f"{key}={value}"]
    docker_cmd += [image, *command]
    started = time.perf_counter()
    proc = subprocess.run(docker_cmd, capture_output=True, text=True, timeout=timeout)
    elapsed_ms = (time.perf_counter() - started) * 1000
    return proc.returncode, proc.stdout, proc.stderr, elapsed_ms
