import asyncio
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Final

# --- Constants & Configuration ---
ROOT_DIR: Final[Path] = Path("c:/Users/Albert Morin/Desktop/PersonaMimic_Final")
PRIMARY_DB: Final[str] = "persona_mimic.db"
EXPIRY_HOURS: Final[int] = 24
CHECK_INTERVAL_SECONDS: Final[int] = 3600  # 1 hour
LOG_PATH: Final[Path] = ROOT_DIR / "logs" / "gc_watchdog.log"

# Setup Logging
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GCWatchdog")

class MaintenanceService:
    """Service layer for identifying and purging technical debt/bloat."""

    def __init__(self, root: Path):
        self.root = root
        self.expiry_threshold = datetime.now() - timedelta(hours=EXPIRY_HOURS)

    async def run_cleanup_cycle(self) -> None:
        """Orchestrates a single garbage collection pass."""
        logger.info("Starting Garbage Collection cycle...")
        
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._purge_temp_workspaces())
            tg.create_task(self._purge_expired_logs())
            tg.create_task(self._purge_orphaned_databases())
            tg.create_task(self._purge_build_caches())

        logger.info("Garbage Collection cycle complete.")

    async def _purge_temp_workspaces(self) -> None:
        """Removes temporary directories in workspace/ and scratch/ older than 24h."""
        targets = ["workspace", "scratch", ".agents"]
        for target_name in targets:
            target_path = self.root / target_name
            if not target_path.exists():
                continue

            for item in target_path.iterdir():
                if not item.is_dir():
                    continue
                
                if self._is_expired(item):
                    self._delete_recursive(item)

    async def _purge_expired_logs(self) -> None:
        """Removes log files older than 24h."""
        log_dir = self.root / "logs"
        if not log_dir.exists():
            return

        for log_file in log_dir.glob("*.log"):
            # Don't delete the watchdog's own active log if it's new
            if log_file.name == "gc_watchdog.log":
                continue
                
            if self._is_expired(log_file):
                self._delete_file(log_file)

    async def _purge_orphaned_databases(self) -> None:
        """Removes non-primary SQLite files and WAL/SHM artifacts."""
        for db_file in self.root.glob("*.db*"):
            if db_file.name.startswith(PRIMARY_DB):
                continue
            
            # Delete any other .db, .db-wal, .db-shm
            self._delete_file(db_file)

    async def _purge_build_caches(self) -> None:
        """Cleans up __pycache__, .ruff_cache, etc."""
        cache_patterns = ["**/__pycache__", "**/.ruff_cache", "**/.pytest_cache"]
        for pattern in cache_patterns:
            for cache_dir in self.root.glob(pattern):
                if cache_dir.is_dir():
                    self._delete_recursive(cache_dir)

    def _is_expired(self, path: Path) -> bool:
        """Checks if a path's modification time is beyond the threshold."""
        mtime = datetime.fromtimestamp(path.stat().st_mtime)
        return mtime < self.expiry_threshold

    def _delete_recursive(self, path: Path) -> None:
        """Safely removes a directory tree."""
        try:
            shutil.rmtree(path)
            logger.info(f"Deleted expired directory: {path.relative_to(self.root)}")
        except Exception as e:
            logger.error(f"Failed to delete {path}: {e}")

    def _delete_file(self, path: Path) -> None:
        """Safely removes a single file."""
        try:
            path.unlink()
            logger.info(f"Deleted expired file: {path.relative_to(self.root)}")
        except Exception as e:
            logger.error(f"Failed to delete {path}: {e}")

async def main():
    """Main entry point for the daemon."""
    service = MaintenanceService(ROOT_DIR)
    
    logger.info("GC Watchdog Daemon initialized and running.")
    
    while True:
        try:
            await service.run_cleanup_cycle()
        except Exception as e:
            logger.error(f"Unexpected error in GC cycle: {e}")
            
        logger.info(f"Sleeping for {CHECK_INTERVAL_SECONDS} seconds...")
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("GC Watchdog Daemon stopped by user.")
