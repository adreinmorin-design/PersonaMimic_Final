"""
scripts/storage_migration.py - Total Industrial Migration Orchestrator
Migrates ALL factory data and binaries to E: drive and establishes NTFS Junctions.
"""

import os
import shutil
import subprocess
from pathlib import Path

# Configuration - Root Targets
BASE_PROJECT = Path("C:/Users/Albert Morin/Desktop/PersonaMimic_Final")
TARGET_ROOT = Path("E:/PersonaMimic_Production")

TARGETS = {
    "outputs": BASE_PROJECT / "backend" / "outputs",
    "database": BASE_PROJECT / "persona_mimic.db",
    "knowledge": BASE_PROJECT / "backend" / "app/swarm/knowledge",
    "workspace": BASE_PROJECT / "workspace",
    "logs": BASE_PROJECT / "backend" / "logs",
    "venv": BASE_PROJECT / ".venv",
}


def create_junction(source: Path, target: Path):
    print(f" -> Establishing Junction: {source.name} -> {target}")
    try:
        # PowerShell New-Item -ItemType Junction is robust for Windows
        cmd = [
            "powershell",
            "-Command",
            f'New-Item -ItemType Junction -Path "{source}" -Target "{target}"',
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(f" -> SUCCESS: {source.name} bound.")
        else:
            print(f" -> FAIL: {res.stderr}")
    except Exception as e:
        print(f" -> ERROR: {e}")


def migrate_target(name: str, source: Path):
    target = TARGET_ROOT / name
    print(f"[*] Processing {name}: {source} -> {target}")

    if not source.exists():
        print(" -> SKIP: Source missing.")
        return

    # If it's already a junction/link, skip migration but maybe re-link
    if os.path.islink(source) or (source.is_dir() and any(source.iterdir())):
        # Check if already points to target
        pass

    # Transfer logic
    if not target.exists():
        target.mkdir(parents=True, exist_ok=True)

    if source.is_file():
        # Special case for DB
        shutil.copy2(source, target / source.name)
        source.unlink()
        # For files, we can't 'junction' a single file, but we can symlink it.
        # mklink <link> <target> (no /J)
        print(f" -> Migrated file: {source.name}")
        subprocess.run(["cmd", "/c", f'mklink "{source}" "{target / source.name}"'])
    else:
        # For directories
        print(" -> Syncing directory data...")
        # Move contents
        for item in source.iterdir():
            dest = target / item.name
            if dest.exists():
                if dest.is_dir():
                    shutil.rmtree(dest)
                else:
                    dest.unlink()
            shutil.move(str(item), str(dest))

        source.rmdir()
        create_junction(source, target)


def run_total_migration():
    print("=== TOTAL INDUSTRIAL MIGRATION START ===")
    if not TARGET_ROOT.exists():
        TARGET_ROOT.mkdir(parents=True, exist_ok=True)

    for name, path in TARGETS.items():
        migrate_target(name, path)

    print("=== MIGRATION COMPLETE ===")


if __name__ == "__main__":
    run_total_migration()
