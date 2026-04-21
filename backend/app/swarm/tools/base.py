import datetime
import logging
import os
from typing import Any

from pydantic import BaseModel

from app.core.paths import CUSTOM_TOOLS_DIR, WORKSPACE_DIR
from app.swarm import tool_runtime, workspace_utils

logger = logging.getLogger("swarm.tools.base")

# --- Constants ---
FACTORY_MIN_SCORE = int(os.getenv("FACTORY_MIN_SCORE", "75"))
FACTORY_MIN_README_CHARS = max(40, int(os.getenv("FACTORY_MIN_README_CHARS", "200")))
FACTORY_MIN_SOURCE_CHARS = max(80, int(os.getenv("FACTORY_MIN_SOURCE_CHARS", "500")))
FACTORY_MIN_MARKETING_CHARS = max(80, int(os.getenv("FACTORY_MIN_MARKETING_CHARS", "400")))
FACTORY_MIN_TITLE_CHARS = max(6, int(os.getenv("FACTORY_MIN_TITLE_CHARS", "10")))

SOURCE_FILE_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx"}
TEXT_FILE_EXTENSIONS = SOURCE_FILE_EXTENSIONS | {
    ".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".csv", ".html", ".css",
}
IMAGE_FILE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}

CUSTOM_TOOL_REGISTRY = os.path.join(CUSTOM_TOOLS_DIR, "tool_registry.json")

# --- Common Pydantic Models ---
class SearchArgs(BaseModel):
    query: str

class ComplianceArgs(BaseModel):
    product_name: str
    niche: str
    specs: str | None = ""

# --- Workspace Utils Proxies ---
def _resolve_workspace_path(filename: str | None = None) -> str:
    return workspace_utils.resolve_workspace_path(filename)

def _iter_workspace_files(selected_files: list[str] | None = None):
    yield from workspace_utils.iter_workspace_files(selected_files)

def _normalize_product_name(name: str) -> str:
    return workspace_utils.normalize_product_name(name)

def _infer_product_files(product_name: str, files: list[str] | None = None) -> list[str] | None:
    return workspace_utils.infer_product_files(product_name, files)

def _stage_review_workspace(selected_files: list[str] | None) -> tuple[str, list[str]]:
    return workspace_utils.stage_review_workspace(selected_files)

def _build_workspace_snapshot(workspace_root: str) -> dict[str, Any]:
    return workspace_utils.build_workspace_snapshot(workspace_root)

def _build_snapshot_for_files(selected_files: list[str] | None) -> dict[str, Any]:
    return workspace_utils.build_snapshot_for_files(selected_files)

def _dedupe_preserve(items: list[str]) -> list[str]:
    return workspace_utils.dedupe_preserve(items)

def _assess_bundle_quality(product_name: str, snapshot: dict[str, Any]) -> dict[str, list[str]]:
    return workspace_utils.assess_bundle_quality(product_name, snapshot)

def _resolve_publish_description(snapshot: dict[str, Any], description: str) -> str:
    return workspace_utils.resolve_publish_description(snapshot, description)

def _assess_publish_readiness(platform: str, title: str, description: str, snapshot: dict[str, Any]) -> dict[str, Any]:
    return workspace_utils.assess_publish_readiness(platform, title, description, snapshot)

# --- Runtime Helpers ---
def get_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _load_json_file(path: str, default):
    return tool_runtime.load_json_file(path, default)

def _save_json_file(path: str, payload: Any):
    tool_runtime.save_json_file(path, payload)

def _is_failure_result(result: str) -> bool:
    return tool_runtime.is_failure_result(result)

def _custom_tool_module_path(name: str) -> str:
    return tool_runtime.custom_tool_module_path(name)

def _extract_code(text: str) -> str:
    import re
    match = re.search(r"```[a-zA-Z]*\n(.*?)\n```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

# --- Semantic Cache ---
class SemanticCache:
    def __init__(self):
        self.enabled = False
        self.model = None
        self.index = None
        self.store = []
        self._initialization_attempted = False

    def _ensure_ready(self):
        if self.enabled: return True
        if self._initialization_attempted: return False
        self._initialization_attempted = True
        try:
            import faiss
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
            self.index = faiss.IndexFlatL2(384)
            self.enabled = True
        except (ImportError, Exception) as exc:
            logger.warning("Semantic cache disabled: %s", exc)
        return self.enabled

    def get(self, query: str) -> str | None:
        if not self._ensure_ready(): return None
        try:
            vec = self.model.encode([query])
            distances, indexes = self.index.search(vec, 1)
            if indexes[0][0] != -1 and distances[0][0] < 0.3:
                return self.store[indexes[0][0]]["result"]
        except Exception as exc:
            logger.debug("Cache lookup failed: %s", exc)
        return None

    def add(self, query: str, result: str):
        if not self._ensure_ready(): return
        try:
            vec = self.model.encode([query])
            self.index.add(vec)
            self.store.append({"query": query, "result": result})
        except Exception as exc:
            logger.debug("Cache insert failed: %s", exc)

async def _persist_product_state(product_name: str, **kwargs):
    from app.database.database import SessionLocal
    from app.products.repository import product_repo
    try:
        db = SessionLocal()
        try:
            await product_repo.update_state(db, product_name, **kwargs)
        finally:
            db.close()
    except Exception as exc:
        logger.warning(f"[DB-AWARE] Could not persist state for {product_name}: {exc}. Continuing launch...")

tool_cache = SemanticCache()
