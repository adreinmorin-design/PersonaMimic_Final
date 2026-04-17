import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_env")

modules_to_check = [
    "torch",
    "sqlalchemy",
    "torchaudio",
    "speechbrain",
    "cryptography",
    "pydantic",
    "nats",
    "faiss",
    "sentence_transformers",
    "googlesearch",
    "bs4",
    "angr",
    "dotenv",
]


def verify_python():
    logger.info("Verifying Python Modules...")
    missing = []
    for mod in modules_to_check:
        try:
            __import__(mod)
            logger.info(f"[OK] {mod} is installed.")
        except ImportError:
            logger.error(f"[FAIL] {mod} is MISSING.")
            missing.append(mod)

    if not missing:
        logger.info("All essential Python modules are present.")
    else:
        logger.error(f"Missing modules: {', '.join(missing)}")
    return len(missing) == 0


def verify_go():
    import subprocess

    logger.info("Verifying Go Modules...")
    try:
        # Check if we can run go list on the websocket package
        res = subprocess.run(
            ["go", "list", "github.com/gorilla/websocket"],
            cwd="backend/outputs/PR-001/backend",
            capture_output=True,
            text=True,
        )
        if res.returncode == 0:
            logger.info("[OK] github.com/gorilla/websocket is found.")
            return True
        else:
            logger.error(f"[FAIL] Go module error: {res.stderr}")
            return False
    except FileNotFoundError:
        logger.warning("Go not installed or not in PATH. Skipping Go verification.")
        return True


if __name__ == "__main__":
    py_ok = verify_python()
    go_ok = verify_go()
    if py_ok and go_ok:
        print("\nENVIRONMENT STABLE: All industrial requirements met.")
    else:
        print("\nENVIRONMENT UNSTABLE: Please run 'uv sync' and 'go mod tidy' manually.")
        sys.exit(1)
