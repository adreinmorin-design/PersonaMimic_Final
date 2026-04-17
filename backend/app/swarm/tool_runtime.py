import datetime
import importlib.util
import inspect
import json
import logging
import os
from typing import Any

from app.core.paths import CUSTOM_TOOLS_DIR

logger = logging.getLogger("swarm.tools")

CUSTOM_TOOL_REGISTRY = os.path.join(CUSTOM_TOOLS_DIR, "tool_registry.json")

FACTORY_MIN_SCORE = max(0, min(100, int(os.getenv("FACTORY_MIN_SCORE", "95"))))
FACTORY_MIN_README_CHARS = max(40, int(os.getenv("FACTORY_MIN_README_CHARS", "500")))
FACTORY_MIN_SOURCE_CHARS = max(80, int(os.getenv("FACTORY_MIN_SOURCE_CHARS", "1000")))
FACTORY_MIN_MARKETING_CHARS = max(80, int(os.getenv("FACTORY_MIN_MARKETING_CHARS", "800")))
FACTORY_MIN_TITLE_CHARS = max(6, int(os.getenv("FACTORY_MIN_TITLE_CHARS", "10")))

MUTATING_TOOLS = {
    "file_manager",
    "package_product",
    "create_custom_tool",
    "spawn_sub_brain",
    "self_heal",
    "peer_review",
    "social_publisher",
    "generate_marketing_copy",
    "generate_whop_app",
    "generate_app_visuals",
    "assemble_full_product",
    "ecommerce_publisher",
    "python_executor",
    "shell_executor",
    "saas_architect",
}

CACHEABLE_TOOLS = {"web_search", "web_fetch", "market_research", "analyze_error_nlp"}


class SemanticCache:
    def __init__(self):
        self.enabled = False
        self.model = None
        self.index = None
        self.store = []
        self._initialization_attempted = False

    def _ensure_ready(self):
        if self.enabled:
            return True
        if self._initialization_attempted:
            return False

        self._initialization_attempted = True
        try:
            import faiss
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
            self.index = faiss.IndexFlatL2(384)
            self.enabled = True
        except ImportError:
            logger.warning("FAISS or Sentence-Transformers not found. Cache disabled.")
        except Exception as exc:
            logger.warning("Semantic cache disabled: %s", exc)
        return self.enabled

    def get(self, query: str) -> str | None:
        if not self._ensure_ready() or not self.enabled:
            return None
        try:
            vector = self.model.encode([query])
            distances, indexes = self.index.search(vector, 1)
            if indexes[0][0] != -1 and distances[0][0] < 0.3:
                return self.store[indexes[0][0]]["result"]
        except Exception as exc:
            logger.debug("Semantic cache lookup failed for '%s': %s", query, exc)
            return None
        return None

    def add(self, query: str, result: str):
        if not self._ensure_ready() or not self.enabled:
            return
        try:
            vector = self.model.encode([query])
            self.index.add(vector)
            self.store.append({"query": query, "result": result})
        except Exception as exc:
            logger.debug("Semantic cache insert failed for '%s': %s", query, exc)
            return


tool_cache = SemanticCache()


def get_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_json_file(path: str, default):
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return default
    except Exception as exc:
        logger.warning("Failed to read JSON file %s: %s", path, exc)
        return default


def save_json_file(path: str, payload: Any):
    temp_path = f"{path}.tmp"
    with open(temp_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    os.replace(temp_path, path)


def custom_tool_module_path(name: str) -> str:
    return os.path.join(CUSTOM_TOOLS_DIR, f"{name}.py")


def is_failure_result(result: str) -> bool:
    text = str(result).strip().lower()
    return (
        not text
        or text.startswith("error")
        or text.startswith("unknown tool")
        or text.startswith("tool execution error")
        or text.startswith("validation error")
        or text.startswith("file error")
        or text.startswith("packaging error")
        or text.startswith("packaging blocked")
        or text.startswith("adversary check error")
        or text.startswith("publish blocked")
        or "[fail]" in text
        or " blocked:" in text
        or " error:" in text
    )


def execute_custom_tool(name: str, args: dict[str, Any]) -> str | None:
    module_path = custom_tool_module_path(name)
    if not os.path.exists(module_path):
        return None

    spec = importlib.util.spec_from_file_location(f"custom_tool_{name}", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load custom tool module for {name}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    entrypoint = getattr(module, name, None) or getattr(module, "run", None)
    if not callable(entrypoint):
        public_functions = [
            obj
            for attr, obj in vars(module).items()
            if inspect.isfunction(obj)
            and obj.__module__ == module.__name__
            and not attr.startswith("_")
        ]
        if len(public_functions) == 1:
            entrypoint = public_functions[0]

    if not callable(entrypoint):
        raise RuntimeError(f"Custom tool '{name}' has no callable entrypoint.")

    signature = inspect.signature(entrypoint)
    accepts_kwargs = any(
        param.kind == inspect.Parameter.VAR_KEYWORD for param in signature.parameters.values()
    )
    call_args = (
        args
        if accepts_kwargs
        else {key: value for key, value in args.items() if key in signature.parameters}
    )
    result = entrypoint(**call_args)
    if isinstance(result, (dict, list)):
        return json.dumps(result)
    return str(result)
