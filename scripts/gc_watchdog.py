#!/usr/bin/env python3
"""WSL-friendly storage guardian for PersonaMimic."""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = PROJECT_ROOT / "logs"
LOG_PATH = LOG_DIR / "gc_watchdog.log"
STATUS_PATH = LOG_DIR / "gc_watchdog_status.json"

CHECK_INTERVAL_SECONDS = 30 * 60
LOW_FREE_GB = 25.0
LOW_FREE_PERCENT = 10.0
SCRATCH_RETENTION_HOURS = 24
LOG_RETENTION_DAYS = 7

WORKSPACE_PREFIXES = ("ava_", "codesmith_", "dre_", "fenko_", "masterbrain_")
PROJECT_CACHE_DIRS = (
    "__pycache__",
    ".ruff_cache",
    ".pytest_cache",
    ".mypy_cache",
    ".tox",
)
PROJECT_CACHE_FILES = ("*.pyc", "*.pyo")
EXTRA_CACHE_PATHS = (
    Path.home() / ".cache" / "pip",
    Path.home() / ".cache" / "uv",
    Path.home() / ".npm" / "_cacache",
    Path.home() / ".cargo" / "registry" / "cache",
    Path.home() / ".cargo" / "git" / "db",
)
SKIP_PREFIXES = (
    PROJECT_ROOT / ".venv",
    PROJECT_ROOT / ".git",
    PROJECT_ROOT / "frontend" / "node_modules",
    PROJECT_ROOT / "products",
)
TRACKED_PATHS: set[str] | None = None


def configure_logging() -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return logging.getLogger("gc_watchdog")


logger = configure_logging()


@dataclass
class VolumeState:
    path: Path
    total_bytes: int
    used_bytes: int
    free_bytes: int

    @property
    def free_gb(self) -> float:
        return self.free_bytes / (1024**3)

    @property
    def free_percent(self) -> float:
        if self.total_bytes == 0:
            return 0.0
        return (self.free_bytes / self.total_bytes) * 100

    @property
    def is_low(self) -> bool:
        return self.free_gb < LOW_FREE_GB or self.free_percent < LOW_FREE_PERCENT

    def as_dict(self) -> dict[str, float | str | bool]:
        return {
            "path": str(self.path),
            "free_gb": round(self.free_gb, 2),
            "free_percent": round(self.free_percent, 2),
            "is_low": self.is_low,
        }


@dataclass
class CleanupResult:
    deleted_paths: list[str]
    reclaimed_bytes: int


def disk_state(path: Path) -> VolumeState:
    usage = shutil.disk_usage(path)
    used_bytes = usage.total - usage.free
    return VolumeState(path=path, total_bytes=usage.total, used_bytes=used_bytes, free_bytes=usage.free)


def age_cutoff(hours: int = 0, days: int = 0) -> datetime:
    return datetime.now(timezone.utc) - timedelta(hours=hours, days=days)


def is_older_than(path: Path, cutoff: datetime) -> bool:
    try:
        modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    except FileNotFoundError:
        return False
    return modified < cutoff


def remove_path(path: Path, deleted_paths: list[str]) -> int:
    if not path.exists():
        return 0

    size_bytes = 0
    if path.is_dir():
        try:
            size_bytes = sum(
                child.stat().st_size
                for child in path.rglob("*")
                if child.exists() and child.is_file()
            )
        except Exception:
            size_bytes = 0
        shutil.rmtree(path, ignore_errors=True)
    else:
        try:
            size_bytes = path.stat().st_size
        except FileNotFoundError:
            size_bytes = 0
        path.unlink(missing_ok=True)

    deleted_paths.append(str(path.relative_to(PROJECT_ROOT)) if path.is_relative_to(PROJECT_ROOT) else str(path))
    return size_bytes


def is_skipped(path: Path) -> bool:
    if any(path == prefix or path.is_relative_to(prefix) for prefix in SKIP_PREFIXES if prefix.exists()):
        return True
    return is_git_tracked(path)


def git_tracked_paths() -> set[str]:
    global TRACKED_PATHS
    if TRACKED_PATHS is not None:
        return TRACKED_PATHS

    git_path = shutil.which("git")
    if not git_path or not (PROJECT_ROOT / ".git").exists():
        TRACKED_PATHS = set()
        return TRACKED_PATHS

    try:
        result = subprocess.run(
            [git_path, "ls-files", "-z"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
        )
    except Exception:
        TRACKED_PATHS = set()
        return TRACKED_PATHS

    TRACKED_PATHS = {
        raw.decode("utf-8", errors="ignore")
        for raw in result.stdout.split(b"\x00")
        if raw
    }
    return TRACKED_PATHS


def is_git_tracked(path: Path) -> bool:
    try:
        rel_path = path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return False

    tracked = git_tracked_paths()
    if rel_path in tracked:
        return True

    if path.is_dir():
        prefix = f"{rel_path}/"
        return any(item.startswith(prefix) for item in tracked)

    return False


def purge_workspace_intermediates(deleted_paths: list[str]) -> int:
    reclaimed = 0
    workspace_dir = PROJECT_ROOT / "workspace"
    if not workspace_dir.exists():
        return reclaimed

    for item in workspace_dir.iterdir():
        if not item.is_dir():
            continue
        if not any(item.name.startswith(prefix) for prefix in WORKSPACE_PREFIXES):
            continue
        zip_version = workspace_dir / f"{item.name}.zip"
        if zip_version.exists() or is_older_than(item, age_cutoff(hours=SCRATCH_RETENTION_HOURS)):
            logger.info("Removing workspace intermediate: %s", item)
            reclaimed += remove_path(item, deleted_paths)
    return reclaimed


def purge_old_directories(targets: Iterable[Path], cutoff: datetime, deleted_paths: list[str]) -> int:
    reclaimed = 0
    for target in targets:
        if not target.exists():
            continue
        for item in target.iterdir():
            if item.is_dir() and is_older_than(item, cutoff):
                logger.info("Removing expired directory: %s", item)
                reclaimed += remove_path(item, deleted_paths)
    return reclaimed


def purge_logs(log_dirs: Iterable[Path], deleted_paths: list[str]) -> int:
    reclaimed = 0
    cutoff = age_cutoff(days=LOG_RETENTION_DAYS)
    for log_dir in log_dirs:
        if not log_dir.exists():
            continue
        for log_file in log_dir.glob("*.log"):
            if log_file == LOG_PATH:
                continue
            if is_older_than(log_file, cutoff):
                logger.info("Removing old log: %s", log_file)
                reclaimed += remove_path(log_file, deleted_paths)
    return reclaimed


def purge_project_caches(deleted_paths: list[str]) -> int:
    reclaimed = 0
    for name in PROJECT_CACHE_DIRS:
        for cache_dir in PROJECT_ROOT.rglob(name):
            if cache_dir.is_dir() and not is_skipped(cache_dir):
                logger.info("Removing project cache: %s", cache_dir)
                reclaimed += remove_path(cache_dir, deleted_paths)

    for pattern in PROJECT_CACHE_FILES:
        for cache_file in PROJECT_ROOT.rglob(pattern):
            if cache_file == LOG_PATH:
                continue
            if cache_file.is_file() and not is_skipped(cache_file):
                logger.info("Removing project cache file: %s", cache_file)
                reclaimed += remove_path(cache_file, deleted_paths)

    frontend_dist = PROJECT_ROOT / "frontend" / "dist"
    if frontend_dist.exists():
        logger.info("Removing frontend dist artifact: %s", frontend_dist)
        reclaimed += remove_path(frontend_dist, deleted_paths)

    return reclaimed


def prune_tool_caches(deleted_paths: list[str]) -> int:
    reclaimed = 0

    uv_path = shutil.which("uv")
    if uv_path:
        try:
            logger.info("Running uv cache prune")
            subprocess.run([uv_path, "cache", "prune"], cwd=PROJECT_ROOT, check=False, capture_output=True, text=True)
        except Exception as exc:
            logger.warning("uv cache prune failed: %s", exc)

    pip_path = shutil.which("pip")
    if pip_path:
        try:
            logger.info("Running pip cache purge")
            subprocess.run([pip_path, "cache", "purge"], cwd=PROJECT_ROOT, check=False, capture_output=True, text=True)
        except Exception as exc:
            logger.warning("pip cache purge failed: %s", exc)

    npm_path = shutil.which("npm")
    if npm_path:
        try:
            logger.info("Running npm cache clean --force")
            subprocess.run(
                [npm_path, "cache", "clean", "--force"],
                cwd=PROJECT_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
        except Exception as exc:
            logger.warning("npm cache clean failed: %s", exc)

    for cache_path in EXTRA_CACHE_PATHS:
        if cache_path.exists():
            logger.info("Removing extra cache path: %s", cache_path)
            reclaimed += remove_path(cache_path, deleted_paths)

    return reclaimed


def git_housekeeping() -> None:
    git_path = shutil.which("git")
    if not git_path or not (PROJECT_ROOT / ".git").exists():
        return
    try:
        logger.info("Running git gc")
        subprocess.run(
            [git_path, "gc", "--prune=now"],
            cwd=PROJECT_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except Exception as exc:
        logger.warning("git gc failed: %s", exc)


def cleanup_cycle() -> CleanupResult:
    deleted_paths: list[str] = []
    reclaimed = 0

    root_state_before = disk_state(PROJECT_ROOT)
    host_state_before = disk_state(Path("/mnt/c")) if Path("/mnt/c").exists() else None
    low_space = root_state_before.is_low or (host_state_before.is_low if host_state_before else False)

    logger.info("Storage snapshot root=%s", root_state_before.as_dict())
    if host_state_before:
        logger.info("Storage snapshot host=%s", host_state_before.as_dict())

    reclaimed += purge_workspace_intermediates(deleted_paths)
    reclaimed += purge_old_directories(
        [
            PROJECT_ROOT / "scratch",
            PROJECT_ROOT / "backend" / "scratch",
        ],
        age_cutoff(hours=SCRATCH_RETENTION_HOURS),
        deleted_paths,
    )
    reclaimed += purge_logs([PROJECT_ROOT / "logs", PROJECT_ROOT / "backend" / "logs"], deleted_paths)
    reclaimed += purge_project_caches(deleted_paths)

    if low_space:
        logger.warning("Low free space detected; running deeper cache cleanup.")
        reclaimed += prune_tool_caches(deleted_paths)
        git_housekeeping()

    root_state_after = disk_state(PROJECT_ROOT)
    host_state_after = disk_state(Path("/mnt/c")) if Path("/mnt/c").exists() else None

    STATUS_PATH.write_text(
        json.dumps(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "low_space": low_space,
                "deleted_paths": deleted_paths,
                "reclaimed_bytes_estimate": reclaimed,
                "root_before": root_state_before.as_dict(),
                "root_after": root_state_after.as_dict(),
                "host_before": host_state_before.as_dict() if host_state_before else None,
                "host_after": host_state_after.as_dict() if host_state_after else None,
                "notes": [
                    "Finished products and source code are preserved.",
                    "WSL cleanup frees Linux space immediately.",
                    "Windows C: may need VHD compaction after large WSL cleanup.",
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    logger.info("Cleanup cycle complete. Estimated reclaimed bytes=%s", reclaimed)
    return CleanupResult(deleted_paths=deleted_paths, reclaimed_bytes=reclaimed)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PersonaMimic storage guardian")
    parser.add_argument("--once", action="store_true", help="Run a single cleanup cycle and exit")
    parser.add_argument("--daemon", action="store_true", help="Run continuously with a sleep interval")
    parser.add_argument(
        "--interval-seconds",
        type=int,
        default=CHECK_INTERVAL_SECONDS,
        help=f"Daemon interval in seconds (default: {CHECK_INTERVAL_SECONDS})",
    )
    return parser.parse_args()


def run_daemon(interval_seconds: int) -> None:
    while True:
        try:
            cleanup_cycle()
        except Exception:
            logger.exception("Unexpected error in cleanup cycle")
        time.sleep(interval_seconds)


def main() -> int:
    args = parse_args()

    try:
        if args.daemon and not args.once:
            run_daemon(args.interval_seconds)
        else:
            cleanup_cycle()
        return 0
    except Exception:
        logger.exception("Storage guardian failed")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
