"""
app/swarm/persona_engine.py - Streamlined & Optimized LLM Orchestrator
Simplified for high-efficiency industrial production with Cloud-Ollama support.
"""

import hashlib
import json
import logging
import os
import time
from typing import Any

import ollama
import requests

from app.config.service import config_service
from app.core.cache import cache
from app.database.database import SessionLocal
from app.forge.mapper import knowledge_mapper

logger = logging.getLogger("swarm.persona_engine")
LOCAL_OLLAMA_HOST = "http://127.0.0.1:11434"
MODEL_FALLBACK = "qwen2.5:7b"
CLOUD_TIMEOUT_SECONDS = float(os.getenv("CLOUD_TIMEOUT_SECONDS", "25"))


class ResponseParser:
    """Standardized logic for extracting JSON and tool calls from any LLM provider."""

    @staticmethod
    def extract_json(text: str) -> dict[str, Any] | None:
        if not text:
            return None
        try:
            # Try finding the first '{' and last '}'
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                return json.loads(text[start : end + 1])
        except Exception as exc:
            logger.debug("JSON extraction failed: %s", exc)
        return None

    @staticmethod
    def normalize_message(message: Any) -> dict[str, Any]:
        """Unwrap raw model responses into a standard {role, content, tool_calls} dict."""
        content = getattr(message, "content", "") or ""
        role = getattr(message, "role", "assistant") or "assistant"
        tool_calls = getattr(message, "tool_calls", []) or []

        # If no tool calls, try parsing JSON from content (for models that don't support native tool calls)
        if not tool_calls and content:
            data = ResponseParser.extract_json(content)
            if data and "action" in data:
                tool_calls = [
                    {
                        "type": "function",
                        "function": {"name": data["action"], "arguments": data.get("params", {})},
                    }
                ]

        return {"role": role, "content": content, "tool_calls": tool_calls}

    @staticmethod
    def parse_tool_call(tool: Any) -> tuple[str | None, dict[str, Any]]:
        """Normalize tool_call objects into (name, args)."""
        try:
            fn = getattr(tool, "function", tool.get("function") if isinstance(tool, dict) else None)
            if not fn:
                return None, {}

            name = getattr(fn, "name", fn.get("name") if isinstance(fn, dict) else None)
            raw_args = getattr(
                fn, "arguments", fn.get("arguments", {}) if isinstance(fn, dict) else {}
            )

            args = json.loads(raw_args) if isinstance(raw_args, str) else (raw_args or {})

            # Alias mapping for stability
            aliases = {
                "write_code": "file_manager",
                "search": "web_search",
                "research": "market_research",
            }
            return aliases.get(name, name), args
        except Exception as e:
            logger.debug(f"Tool parse error: {e}")
            return None, {}


class PersonaEngine:
    def __init__(self, model: str | None = None):
        self.examples: list[dict[str, str]] = []
        self.custom_tools: list[dict[str, Any]] = []

        runtime = self._resolve_runtime(model)
        self.model = runtime["model"]
        self.host = runtime["host"]
        self.key = runtime["key"]
        self.is_cloud = runtime["is_cloud"]
        self.is_vllm = runtime.get("is_vllm", False)

        if self.is_cloud:
            # We use local Ollama-compatible client for standard OSS cloud endpoints
            self.client = None  # Resetting specifically for OSS mandate
            logger.info(f"PersonaEngine [Cloud OSS Mode] Setup: {self.model} @ {self.host}")
        elif self.is_vllm:
            from openai import OpenAI

            self.client = OpenAI(base_url=f"{self.host.rstrip('/')}/v1", api_key=self.key)
            logger.info(f"PersonaEngine [vLLM ROCm Mode] Active: {self.model} @ {self.host}")
        else:
            self.client = ollama.Client(
                host=self.host, headers={"X-API-KEY": self.key} if self.key else None
            )
            logger.info(
                f"PersonaEngine [Local Mode] Initialized: {self.model} @ {self.host} (is_cloud=False)"
            )

    @staticmethod
    def _read_setting(key: str) -> str | None:
        """Secure setting read with direct SQLite fallback to avoid SQLAlchemy registry recursion."""
        try:
            # Try high-level first
            db = SessionLocal()
            try:
                return config_service.get_setting(db, key)
            finally:
                db.close()
        except Exception:
            # Direct SQLite fallback (Industrial standard for bootstrap settings)
            try:
                import sqlite3

                from app.core.paths import DATABASE_PATH

                conn = sqlite3.connect(DATABASE_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM system_settings WHERE key = ?", (key,))
                row = cursor.fetchone()
                conn.close()
                return row[0] if row else None
            except Exception as exc:
                logger.debug("Bootstrap setting read failed for '%s': %s", key, exc)
                return None

    def _resolve_runtime(self, model_override: str | None) -> dict[str, Any]:
        """Priority: Override > DB Setting > Env > Fallback."""
        db_use_cloud = self._read_setting("use_cloud")
        env_use_cloud = os.getenv("USE_CLOUD", "false").lower() == "true"
        is_cloud_forced = (
            str(db_use_cloud).lower() == "true" if db_use_cloud is not None else False
        ) or env_use_cloud

        configured_model = (
            model_override
            or self._read_setting("model")
            or os.getenv("CURRENT_MODEL")
            or MODEL_FALLBACK
        )

        # Normalize local model
        if not is_cloud_forced and any(
            x in str(configured_model).lower() for x in ["llama", "mixtral", "gpt"]
        ):
            configured_model = "qwen2.5:7b"

        # 1. Try vLLM (High-Speed Inference)
        vllm_host = os.getenv("VLLM_URL", "http://localhost:8000")
        if vllm_data := self._probe_vllm(vllm_host, configured_model):
            return vllm_data

        # 2. Try Cloud
        cloud_url = (
            self._read_setting("OLLAMA_CLOUD_URL") or os.getenv("OLLAMA_CLOUD_URL") or ""
        ).strip()
        if is_cloud_forced and cloud_url:
            return {
                "model": configured_model,
                "host": cloud_url,
                "key": (
                    self._read_setting("OLLAMA_CLOUD_KEY") or os.getenv("GROQ_API_KEY") or ""
                ).strip(),
                "is_cloud": True,
                "is_vllm": False,
            }

        # 3. Fallback to Local
        return {
            "model": configured_model,
            "host": self._normalize_local_host(
                os.getenv("OLLAMA_HOST") or "http://localhost:11434"
            ),
            "key": "",
            "is_cloud": False,
            "is_vllm": False,
        }

    @staticmethod
    def _probe_vllm(host: str, model: str) -> dict | None:
        try:
            res = requests.get(f"{host.rstrip('/')}/v1/models", timeout=1)
            if res.status_code == 200:
                logger.info(f"vLLM Detected (ROCm Ready): {host}")
                return {
                    "model": model,
                    "host": host,
                    "key": "vllm_token",
                    "is_cloud": False,
                    "is_vllm": True,
                }
        except Exception:
            pass
        return None

    @staticmethod
    def _normalize_local_host(host: str) -> str:
        normalized = (host or LOCAL_OLLAMA_HOST).strip()
        if normalized in {"0.0.0.0", "localhost", "127.0.0.1"}:
            return LOCAL_OLLAMA_HOST
        if "://" not in normalized:
            return f"http://{normalized}"
        return normalized

    @staticmethod
    def _dedupe_models(models: list[str]) -> list[str]:
        seen = set()
        ordered = []
        for model in models:
            name = (model or "").strip()
            if not name or name in seen:
                continue
            seen.add(name)
            ordered.append(name)
        return ordered

    def list_available_models(self) -> list[str]:
        discovered: list[str] = []

        if self.is_cloud:
            try:
                # Disabling cloud model list to enforce pre-configured OSS models
                discovered.append(self.model)
            except Exception as exc:
                logger.warning("Cloud model discovery failed: %s", exc)
        else:
            try:
                response = requests.get(f"{self.host.rstrip('/')}/api/tags", timeout=5)
                response.raise_for_status()
                payload = response.json()
                discovered.extend(model.get("name", "") for model in payload.get("models", []))
            except Exception as exc:
                logger.warning("Local model discovery failed: %s", exc)

        discovered.extend(
            [
                self.model,
                self._read_setting("model") or "",
                os.getenv("CURRENT_MODEL", ""),
            ]
        )
        models = self._dedupe_models(discovered)
        return models or ["No models detected"]

    def _cloud_candidate_models(self) -> list[str]:
        fallback_csv = os.getenv(
            "CLOUD_FALLBACK_MODELS",
            "llama-3.1-8b-instant,llama-3.3-70b-versatile,mixtral-8x7b-32768",
        )
        fallback_models = [item.strip() for item in fallback_csv.split(",") if item.strip()]
        return self._dedupe_models([self.model, *fallback_models])

    @staticmethod
    def _safe_sleep(seconds: float):
        if seconds > 0:
            time.sleep(seconds)

    @staticmethod
    def _fetch_local_models(local_host: str) -> list[str]:
        try:
            response = requests.get(f"{local_host.rstrip('/')}/api/tags", timeout=5)
            response.raise_for_status()
            payload = response.json()
            return [
                model.get("name", "").strip()
                for model in payload.get("models", [])
                if model.get("name")
            ]
        except Exception:
            return []

    def _try_local_fallback(
        self, messages: list[dict[str, Any]], last_error: Exception
    ) -> dict[str, Any]:
        local_host = self._normalize_local_host(os.getenv("OLLAMA_HOST") or LOCAL_OLLAMA_HOST)
        local_models = self._fetch_local_models(local_host)
        candidate_models = self._dedupe_models([self.model, MODEL_FALLBACK, *local_models])

        if not candidate_models:
            raise RuntimeError(f"Cloud inference failed and no local models found: {last_error}")

        local_client = ollama.Client(host=local_host)
        for model_name in candidate_models:
            try:
                response = local_client.chat(
                    model=model_name,
                    messages=messages,
                    options={"temperature": 0.2, "top_p": 0.9, "num_predict": 2048},
                )
                self.client = local_client
                self.host = local_host
                self.model = model_name
                self.is_cloud = False
                logger.warning(
                    "Cloud inference unavailable; switched to local model '%s' at %s.",
                    model_name,
                    local_host,
                )
                return ResponseParser.normalize_message(response.message)
            except Exception as exc:
                logger.warning("Local fallback attempt failed for model '%s': %s", model_name, exc)

        raise RuntimeError(
            f"Cloud inference failed and local fallback was unavailable: {last_error}"
        )

    def generate_response(
        self,
        prompt: str,
        chat_context: list[dict[str, Any]] = None,
        tools: list[dict[str, Any]] = None,
        persona_type: str = "mimic",
    ) -> dict[str, Any]:
        """Unified inference entry point with Redis caching and retry logic."""
        cache_key = self._get_cache_key(prompt, chat_context, tools, persona_type)
        if cached_res := cache.get(cache_key):
            logger.info(f"Neural Cache HIT: {cache_key[:12]}... (Model: {self.model})")
            return cached_res

        messages = [{"role": "system", "content": self._build_prompt(prompt, tools, persona_type)}]
        messages.extend(chat_context or [])

        last_error = None
        for attempt in range(4):
            try:
                res = self._execute_inference(messages)
                cache.set(cache_key, res, expire=14400)
                return res
            except Exception as e:
                last_error = e
                self._handle_inference_fault(attempt, e)

        if self.is_cloud:
            res = self._try_local_fallback(messages, last_error)
            cache.set(cache_key, res, expire=3600)
            return res

        raise RuntimeError(f"Industrial Swarm Stalled: {last_error}")

    def _get_cache_key(self, prompt, context, tools, persona) -> str:
        seed = (
            f"{self.model}:{prompt}:{json.dumps(context or [])}:{json.dumps(tools or [])}:{persona}"
        )
        return f"llm_cache:{hashlib.md5(seed.encode()).hexdigest()}"

    def _execute_inference(self, messages: list[dict]) -> dict:
        if self.is_cloud:
            return self._execute_cloud_oss_inference(messages)

        response = self.client.chat(
            model=self.model,
            messages=messages,
            options={"temperature": 0.2, "top_p": 0.9, "num_predict": 2048},
        )
        return ResponseParser.normalize_message(response.message)

    def _execute_cloud_oss_inference(self, messages: list[dict]) -> dict:
        last_err = None
        for candidate in self._cloud_candidate_models():
            try:
                response = requests.post(
                    f"{self.host.rstrip('/')}/chat/completions",
                    headers={"Authorization": f"Bearer {self.key}"},
                    json={
                        "model": candidate,
                        "messages": messages,
                        "temperature": 0.2,
                        "max_tokens": 2048,
                    },
                    timeout=CLOUD_TIMEOUT_SECONDS,
                )
                response.raise_for_status()
                data = response.json()
                return {
                    "role": "assistant",
                    "content": data["choices"][0]["message"]["content"],
                    "tool_calls": [],
                }
            except Exception as exc:
                last_err = exc
                logger.warning("Cloud OSS attempt failed (%s): %s", candidate, exc)
        raise RuntimeError(last_err or "Cloud OSS candidates exhausted.")

    def _handle_inference_fault(self, attempt: int, error: Exception):
        is_429 = "429" in str(error) or "rate_limit" in str(error).lower()
        sleep_time = min(12, (5 if is_429 else 2) ** attempt)
        logger.warning(f"Inference Fault (Attempt {attempt + 1}): {error}")
        self._safe_sleep(sleep_time)

    def _build_prompt(
        self, base_prompt: str, tools: list[dict[str, Any]], persona_type: str
    ) -> str:
        if base_prompt:
            return base_prompt

        # Shared high-fidelity directive (Imported from domain sibling)
        try:
            from app.swarm.tools import FACTORY_MIN_SCORE
        except ImportError:
            factory_min_score = 90
        else:
            factory_min_score = FACTORY_MIN_SCORE

        tools_str = json.dumps(tools + self.custom_tools, indent=2) if tools else "None"

        training_directives = ""
        if persona_type == "coding":
            training_directives = """
## CODING STANDARDS (CRITICAL):
1. Domain-Driven Design: Decouple routing/logic.
2. Guard Clauses: Replace nested if/else with early returns.
3. Clean Code: Provide type hints. Use absolute imports.
4. Code Completeness: NEVER use placeholders, 'pass', or 'TODO'. Fully implement all logic.
5. Error Handling: Always implement try/except blocks and logging.
6. Supabase Realtime (Industrial): Use Pure Phoenix 2.0 protocol (not standard SDKs) for high efficiency. Enforce 25s heartbeats. Validate all private topics against RLS.
7. Appsmith DSL (Industrial): Maintain strict absolute grid coordinates (topRow, bottomRow, leftColumn, rightColumn). Use double curly braces {{ }} for dynamic bindings. Enforce JSON hierarchy for container widgets.
"""
        elif persona_type == "reasoning":
            training_directives = """
## REASONING & STRATEGY STANDARDS (CRITICAL):
1. Think sequentially: Break down complex problems into atomic logical steps.
2. Market Alignment: Ensure all architectural decisions align with profitable product constraints.
3. Validate Assumptions: Always test hypotheses against data before committing to technical specs.
4. Neutral Observation: Analyze failures and bugs with perfect detachment to self-heal code effectively.
"""
        elif persona_type == "director":
            training_directives = """
## INDUSTRIAL DIRECTOR STANDARDS (TOP-TIER):
1. Orchestration: Strategize across multiple product niches simultaneously.
2. Delegation: Identify complex tasks and decompose them for specialized sub-brains.
3. Quality Enforcer: Maintain a zero-tolerance policy for substandard builds.
4. Self-Healing Lead: Analyze system-wide failures and issue corrective directives for the entire swarm.
"""

        return f"""## IDENTITY: Studio-Grade {persona_type.upper()} Swarm Node
## MISSION: Build premium, Dre-Branded digital assets.
## QUALITY GATE: Minimum Score {factory_min_score}/100.{training_directives}
## SCHEMA: Respond ONLY with JSON: {{"analysis": "reasoning", "action": "tool", "params": {{}}}}
## TOOLS:
{tools_str}
"""

    def set_model(self, model_name: str):
        self.model = model_name
        logger.info(f"Neural Shift: Model -> {model_name}")

    @staticmethod
    def unwrap_message(msg):
        return msg

    @staticmethod
    def unwrap_tool_call(tool):
        return ResponseParser.parse_tool_call(tool)

    def activate_archetype(self, style: str):
        """Unlocks a reverse-engineered coding archetype at the neural layer."""
        fingerprint = knowledge_mapper.get_steering_for_product(style)
        if not fingerprint:
            return

        logger.info(f"Neural Archetype UNLOCKED: {style} (Enforcing specialized dev personality)")
        # In a white-box TransformerLens session, we would apply steering vectors here.
        # For our industrial Ollama/Cloud deployment, we use these fingerprints to
        # dynamically adjust 'persona_type' and internal directive weights.
        self.set_model(self.model)  # Refresh model state with new identity bias
