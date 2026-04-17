from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
APP_DIR = Path(__file__).resolve().parents[1]

# In Docker, BACKEND_DIR is /app. If parents[3] is /, we use BACKEND_DIR as PROJECT_ROOT
try:
    potential_root = Path(__file__).resolve().parents[3]
    PROJECT_ROOT = BACKEND_DIR if potential_root == Path("/") else potential_root
except IndexError:
    PROJECT_ROOT = BACKEND_DIR

STATIC_DIR = BACKEND_DIR / "static"
WORKSPACE_DIR = PROJECT_ROOT / "workspace"
CUSTOM_TOOLS_DIR = BACKEND_DIR / "custom_tools"
DATABASE_PATH = PROJECT_ROOT / "persona_mimic.db"
PREDICTIVE_MODEL_PATH = BACKEND_DIR / "predictive_model.pkl"

LOGS_DIR = BACKEND_DIR / "logs"

STATIC_DIR.mkdir(parents=True, exist_ok=True)
WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
CUSTOM_TOOLS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def brain_log_path(name: str) -> Path:
    return LOGS_DIR / f"brain_{name.lower()}_log.json"
