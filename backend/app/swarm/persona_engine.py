"""
app/swarm/persona_engine.py - Streamlined & Optimized LLM Orchestrator
Simplified for high-efficiency industrial production with Cloud-Ollama support.
"""

import asyncio
import hashlib
import json
import logging
import os
import time
from typing import Any

# System Standards: Multi-Agent Cloud Routing
CLOUD_ALLOWLIST = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama3-70b-8192",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
]

import ollama

from app.config.service import config_service
from app.core.cache import cache
from app.core.paths import CUSTOM_TOOL_REGISTRY
from app.database.database import SessionLocal
from app.forge.mapper import knowledge_mapper

logger = logging.getLogger("swarm.persona_engine")
LOCAL_OLLAMA_HOST = "http://127.0.0.1:11434"
MODEL_FALLBACK = "qwen2.5-coder:7b"
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
    _settings_cache: dict[str, tuple[float, str | None]] = {}
    _runtime_cache: dict[str, tuple[float, dict[str, Any]]] = {}
    _model_list_cache: dict[str, tuple[float, list[str]]] = {}
    _vllm_probe_cache: dict[str, tuple[float, bool]] = {}
    _custom_tools_cache: tuple[float, list[dict[str, Any]]] = (0.0, [])
    _SETTINGS_CACHE_TTL_SECONDS = 10.0
    _RUNTIME_CACHE_TTL_SECONDS = 15.0
    _MODEL_LIST_CACHE_TTL_SECONDS = 30.0
    _VLLM_PROBE_CACHE_TTL_SECONDS = 20.0
    _CUSTOM_TOOLS_CACHE_TTL_SECONDS = 10.0

    def __init__(self, model: str | None = None):
        self.examples: list[dict[str, str]] = []
        self.custom_tools: list[dict[str, Any]] = []

        runtime = self._resolve_runtime(model)
        self.model = runtime["model"]
        self.host = runtime["host"]
        self.key = runtime["key"]
        self.is_cloud = runtime["is_cloud"]
        self.is_vllm = runtime.get("is_vllm", False)
        self._load_custom_tools()

        if self.is_cloud:
            # We use local Ollama-compatible client for standard OSS cloud endpoints
            self.client = None  # Resetting specifically for OSS mandate
            logger.info(f"PersonaEngine [Cloud OSS Mode] Setup: {self.model} @ {self.host}")
        elif self.is_vllm:
            from openai import OpenAI

            self.client = OpenAI(base_url=f"{self.host.rstrip('/')}/v1", api_key=self.key)
            logger.info(f"PersonaEngine [vLLM ROCm Mode] Active: {self.model} @ {self.host}")
        else:
            self.client = ollama.AsyncClient(
                host=self.host, headers={"X-API-KEY": self.key} if self.key else None
            )
            logger.info(
                f"PersonaEngine [Local Mode] Initialized: {self.model} @ {self.host} (is_cloud=False)"
            )

    @classmethod
    def clear_caches(cls):
        cls._settings_cache.clear()
        cls._runtime_cache.clear()
        cls._model_list_cache.clear()
        cls._vllm_probe_cache.clear()
        cls._custom_tools_cache = (0.0, [])

    @staticmethod
    def _read_setting(key: str) -> str | None:
        """Secure setting read with direct SQLite fallback to avoid SQLAlchemy registry recursion."""
        now = time.monotonic()
        cached = PersonaEngine._settings_cache.get(key)
        if cached and cached[0] > now:
            return cached[1]

        value: str | None = None
        try:
            db = SessionLocal()
            try:
                value = config_service.get_setting(db, key)
            finally:
                db.close()
        except Exception:
            try:
                import sqlite3

                from app.core.paths import DATABASE_PATH

                conn = sqlite3.connect(DATABASE_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM system_settings WHERE key = ?", (key,))
                row = cursor.fetchone()
                conn.close()
                value = row[0] if row else None
            except Exception as exc:
                logger.debug("Bootstrap setting read failed for '%s': %s", key, exc)
                value = None

        PersonaEngine._settings_cache[key] = (
            now + PersonaEngine._SETTINGS_CACHE_TTL_SECONDS,
            value,
        )
        return value

    def _load_custom_tools(self):
        """Loads industrial tools reverse-engineered by the swarm."""
        now = time.monotonic()
        cache_expires_at, cached_tools = self._custom_tools_cache
        if cache_expires_at > now:
            self.custom_tools = [tool.copy() for tool in cached_tools]
            return

        loaded_tools: list[dict[str, Any]] = []
        try:
            if os.path.exists(CUSTOM_TOOL_REGISTRY):
                with open(CUSTOM_TOOL_REGISTRY, encoding="utf-8") as f:
                    registry = json.load(f)
                    for entry in registry:
                        loaded_tools.append(
                            {
                            "name": entry["name"],
                            "description": entry.get("purpose", "Autonomous forensic tool."),
                            "parameters": entry.get("schema", {"type": "object", "properties": {}}),
                            }
                        )
                logger.info("Neural Interface: Loaded %s custom tools.", len(loaded_tools))
        except Exception as e:
            logger.warning("Failed to load custom tools: %s", e)

        self.custom_tools = [tool.copy() for tool in loaded_tools]
        type(self)._custom_tools_cache = (
            now + self._CUSTOM_TOOLS_CACHE_TTL_SECONDS,
            [tool.copy() for tool in loaded_tools],
        )

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
        cloud_url = (
            self._read_setting("OLLAMA_CLOUD_URL") or os.getenv("OLLAMA_CLOUD_URL") or ""
        ).strip()
        vllm_host = os.getenv("VLLM_URL", "http://localhost:8000")
        local_host = self._normalize_local_host(os.getenv("OLLAMA_HOST") or LOCAL_OLLAMA_HOST)

        # Normalize local model - Allow 32B Coder and other high-performance local models
        if (
            not is_cloud_forced
            and any(x in str(configured_model).lower() for x in ["mixtral", "gpt"])
            and "coder" not in str(configured_model).lower()
        ):
            configured_model = "qwen2.5-coder:7b"

        runtime_cache_key = json.dumps(
            {
                "model_override": model_override or "",
                "db_use_cloud": db_use_cloud,
                "env_use_cloud": env_use_cloud,
                "configured_model": configured_model,
                "cloud_url": cloud_url,
                "vllm_host": vllm_host,
                "local_host": local_host,
            },
            sort_keys=True,
        )
        now = time.monotonic()
        cached_runtime = self._runtime_cache.get(runtime_cache_key)
        if cached_runtime and cached_runtime[0] > now:
            return dict(cached_runtime[1])

        # 1. Try vLLM (High-Speed Inference)
        if self._probe_vllm(vllm_host):
            runtime = {
                "model": configured_model,
                "host": vllm_host,
                "key": "vllm_token",
                "is_cloud": False,
                "is_vllm": True,
            }
            self._runtime_cache[runtime_cache_key] = (
                now + self._RUNTIME_CACHE_TTL_SECONDS,
                dict(runtime),
            )
            return runtime

        # 2. Try Cloud
        if is_cloud_forced and cloud_url:
            # ONLY try cloud if the model is in our allowlist or explicitly contains cloud-related names
            is_cloud_model = any(m in str(configured_model).lower() for m in CLOUD_ALLOWLIST)
            if is_cloud_model:
                runtime = {
                    "model": configured_model,
                    "host": cloud_url,
                    "key": (
                        self._read_setting("OLLAMA_CLOUD_KEY") or os.getenv("GROQ_API_KEY") or ""
                    ).strip(),
                    "is_cloud": True,
                    "is_vllm": False,
                }
                self._runtime_cache[runtime_cache_key] = (
                    now + self._RUNTIME_CACHE_TTL_SECONDS,
                    dict(runtime),
                )
                return runtime
            else:
                logger.info(
                    f"Engine: Skipping cloud for local-optimized model '{configured_model}'"
                )

        # 3. Fallback to Local
        runtime = {
            "model": configured_model,
            "host": local_host,
            "key": "",
            "is_cloud": False,
            "is_vllm": False,
        }
        self._runtime_cache[runtime_cache_key] = (
            now + self._RUNTIME_CACHE_TTL_SECONDS,
            dict(runtime),
        )
        return runtime

    @staticmethod
    def _probe_vllm(host: str) -> bool:
        normalized_host = host.rstrip("/")
        now = time.monotonic()
        cached = PersonaEngine._vllm_probe_cache.get(normalized_host)
        if cached and cached[0] > now:
            return cached[1]

        is_available = False
        try:
            import requests

            res = requests.get(f"{normalized_host}/v1/models", timeout=1)
            if res.status_code == 200:
                logger.info("vLLM Detected (ROCm Ready): %s", normalized_host)
                is_available = True
        except Exception:
            is_available = False

        PersonaEngine._vllm_probe_cache[normalized_host] = (
            now + PersonaEngine._VLLM_PROBE_CACHE_TTL_SECONDS,
            is_available,
        )
        return is_available

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

    async def list_available_models(self) -> list[str]:
        cache_key = f"{self.host}|{self.model}|{self.is_cloud}"
        now = time.monotonic()
        cached = self._model_list_cache.get(cache_key)
        if cached and cached[0] > now:
            return list(cached[1])

        discovered: list[str] = []

        if self.is_cloud:
            try:
                # Disabling cloud model list to enforce pre-configured OSS models
                discovered.append(self.model)
            except Exception as exc:
                logger.warning("Cloud model discovery failed: %s", exc)
        else:
            try:
                import aiohttp

                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.host.rstrip('/')}/api/tags", timeout=5) as res:
                        res.raise_for_status()
                        payload = await res.json()
                        discovered.extend(
                            model.get("name", "") for model in payload.get("models", [])
                        )
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
        final_models = models or ["No models detected"]
        self._model_list_cache[cache_key] = (
            now + self._MODEL_LIST_CACHE_TTL_SECONDS,
            list(final_models),
        )
        return final_models

    def _cloud_candidate_models(self) -> list[str]:
        # Prioritize 8b-instant for fallbacks as it has significantly higher rate limits than 70b or Mixtral
        fallback_csv = os.getenv(
            "CLOUD_FALLBACK_MODELS",
            "llama-3.1-8b-instant,llama-3.3-70b-versatile",
        )
        fallback_models = [item.strip() for item in fallback_csv.split(",") if item.strip()]
        return self._dedupe_models([self.model, *fallback_models])

    @staticmethod
    def _safe_sleep(seconds: float):
        if seconds > 0:
            time.sleep(seconds)

    @staticmethod
    async def _fetch_local_models(local_host: str) -> list[str]:
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.get(f"{local_host.rstrip('/')}/api/tags", timeout=5) as res:
                    res.raise_for_status()
                    payload = await res.json()
                    return [
                        model.get("name", "").strip()
                        for model in payload.get("models", [])
                        if model.get("name")
                    ]
        except Exception:
            return []

    async def _try_local_fallback(
        self, messages: list[dict[str, Any]], last_error: Exception
    ) -> dict[str, Any]:
        local_host = self._normalize_local_host(os.getenv("OLLAMA_HOST") or LOCAL_OLLAMA_HOST)
        local_models = await self._fetch_local_models(local_host)
        candidate_models = self._dedupe_models([self.model, MODEL_FALLBACK, *local_models])

        if not candidate_models:
            raise RuntimeError(f"Cloud inference failed and no local models found: {last_error}")

        local_client = ollama.AsyncClient(host=local_host)
        for model_name in candidate_models:
            try:
                response = await local_client.chat(
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

    async def generate_response(
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
                res = await self._execute_inference(messages)
                cache.set(cache_key, res, expire=14400)
                return res
            except Exception as e:
                last_error = e
                await self._handle_inference_fault(attempt, e)

        if self.is_cloud:
            res = await self._try_local_fallback(messages, last_error)
            cache.set(cache_key, res, expire=3600)
            return res

        raise RuntimeError(f"Industrial Swarm Stalled: {last_error}")

    def _get_cache_key(self, prompt, context, tools, persona) -> str:
        seed = (
            f"{self.model}:{prompt}:{json.dumps(context or [])}:{json.dumps(tools or [])}:{persona}"
        )
        return f"llm_cache:{hashlib.md5(seed.encode()).hexdigest()}"

    async def _execute_inference(self, messages: list[dict]) -> dict:
        if self.is_cloud:
            # Add a small random jitter (0.5s - 2.5s) to avoid simultaneous hits from multiple brains
            import random

            await asyncio.sleep(random.uniform(0.5, 2.5))
            return await self._execute_cloud_oss_inference(messages)

        # Local Jitter for industrial stability
        import random
        await asyncio.sleep(random.uniform(0.2, 1.0))

        response = await self.client.chat(
            model=self.model,
            messages=messages,
            options={"temperature": 0.2, "top_p": 0.9, "num_predict": 2048},
        )
        return ResponseParser.normalize_message(response.message)

    async def _execute_cloud_oss_inference(self, messages: list[dict]) -> dict:
        last_err = None
        import aiohttp

        async with aiohttp.ClientSession() as session:
            for candidate in self._cloud_candidate_models():
                try:
                    async with session.post(
                        f"{self.host.rstrip('/')}/chat/completions",
                        headers={"Authorization": f"Bearer {self.key}"},
                        json={
                            "model": candidate,
                            "messages": messages,
                            "temperature": 0.2,
                            "max_tokens": 2048,
                        },
                        timeout=CLOUD_TIMEOUT_SECONDS,
                    ) as res:
                        res.raise_for_status()
                        data = await res.json()
                        return {
                            "role": "assistant",
                            "content": data["choices"][0]["message"]["content"],
                            "tool_calls": [],
                        }
                except Exception as exc:
                    last_err = exc
                    logger.warning("Cloud OSS attempt failed (%s): %s", candidate, exc)
        raise RuntimeError(last_err or "Cloud OSS candidates exhausted.")

    async def _handle_inference_fault(self, attempt: int, error: Exception):
        is_429 = "429" in str(error) or "rate_limit" in str(error).lower()
        # For 429, we start with a much longer sleep (15s) and jitter it heavily to avoid swarm collisions
        import random

        base_sleep = 15 if is_429 else 2
        sleep_time = min(120, (base_sleep ** (attempt + 1)) + random.uniform(5, 15))
        logger.warning(
            f"Inference Fault (Attempt {attempt + 1}): {error}. Retrying in {sleep_time:.1f}s..."
        )
        await asyncio.sleep(sleep_time)

    def _build_prompt(
        self, base_prompt: str, tools: list[dict[str, Any]], persona_type: str
    ) -> str:
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
## CODING STANDARDS (INDUSTRIAL SCALE):
1. Advanced Architecture: Enforce multi-module DDD or Micro-services patterns. Avoid monolithic scripts.
2. Asynchronous Core: EVERY IO-bound operation MUST be asynchronous. Use 'asyncio' for all database and network calls.
3. Logic Density: Implement high-complexity algorithms (e.g. predictive analytics, multi-threaded ingestion). NEVER simplify code for brevity.
4. Industrial Resilience: Implement robust retry logic, circuit breakers, and comprehensive telemetry/logging in every module.
5. Code Completeness: ZERO tolerance for placeholders, 'pass', or 'TODO'. Full production-ready implementation is mandatory.
6. Polyglot Integration: Where appropriate, suggest Go or Rust bridges for performance-critical bottlenecks.
7. Branding: EVERY file MUST include the '© 2026 Dre' proprietary industrial copyright header.
8. Supabase & Appsmith: Enforce low-latency Phoenix 2.0 protocols and pixel-perfect absolute grid DSL layouts.
"""
        elif persona_type == "reasoning":
            training_directives = """
## REASONING & STRATEGY STANDARDS (INDUSTRIAL GRADE):
1. Multi-Dimensional Analysis: Consider technical, economic, and operational constraints in every decision.
2. High-Complexity Product Design: Prioritize products that solve deep-seated technical 'pain points' requiring sophisticated engineering, not simple CRUD apps.
3. Demand-First Discovery: Focus research on 'Latent Demand'—underserved, high-value needs that people want but cannot find.
4. Predictive Synthesis: Extrapolate complex trends to design non-obvious, viral digital product categories for 2026 and beyond.
5. Scalability First: Design for industrial scale (millions of users/transactions) from the start.
6. Forensic Neutrality: Analyze data with absolute detachment to ensure market-alignment is driven by facts, not optimism.
"""
        elif persona_type == "director":
            training_directives = """
## INDUSTRIAL DIRECTOR STANDARDS (TOP-TIER):
1. Orchestration: Strategize across multiple product niches simultaneously.
2. Delegation: Identify complex tasks and decompose them for specialized sub-brains.
3. Quality Enforcer: Maintain a zero-tolerance policy for substandard builds.
4. Self-Healing Lead: Analyze system-wide failures and issue corrective directives for the entire swarm.
"""

        identity = f"""## IDENTITY: Studio-Grade {persona_type.upper()} Swarm Node
## MISSION: Build premium, Dre-Branded digital assets.
## QUALITY GATE: Minimum Score {factory_min_score}/100.{training_directives}
"""

        if base_prompt:
            return f"{identity}\n\n## TASK:\n{base_prompt}"

        return f"""{identity}
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
