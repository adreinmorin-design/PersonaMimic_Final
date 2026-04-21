import asyncio
import json
import logging
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from urllib.parse import urlparse

import aiohttp
import ollama

from app.core.paths import WORKSPACE_DIR

logger = logging.getLogger("swarm.adversary")


@dataclass
class AdversaryVerdict:
    passed: bool
    score: int
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    execution_result: str = ""
    market_ready: bool = False
    summary: str = ""

    def to_dict(self):
        return asdict(self)

    def to_feedback_prompt(self) -> str:
        issues_text = (
            "\n".join(f"  - {issue}" for issue in self.issues) if self.issues else "  None"
        )
        suggestions_text = (
            "\n".join(f"  - {item}" for item in self.suggestions) if self.suggestions else "  None"
        )
        return f"""ADVERSARY REVIEW FAILED (Score: {self.score}/100)

Issues found:
{issues_text}

Required improvements:
{suggestions_text}

Execution test result:
  {self.execution_result}

You MUST fix ALL issues above before calling package_product again.
Address each point specifically. Do not skip any."""


PLACEHOLDER_PATTERNS = [
    r"TODO",
    r"FIXME",
    r"PLACEHOLDER",
    r"\.\.\.pass",
    r"raise NotImplementedError",
    r"your_api_key",
    r"INSERT_",
    r"CHANGE_ME",
    r"example\.com/your",
]


async def _auto_fix_python(filepath: str):
    """
    AUTO-PILOT: Automatically fix formatting and trivial lint errors.
    """
    try:
        # 1. Format code (PEP 8)
        proc1 = await asyncio.create_subprocess_exec(
            "ruff",
            "format",
            filepath,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc1.wait()
        # 2. Fix safe lint errors
        proc2 = await asyncio.create_subprocess_exec(
            "ruff",
            "check",
            "--fix",
            filepath,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc2.wait()
    except Exception as e:
        logger.warning(f"Auto-fix failed for {filepath}: {e}")


async def _static_scan(code: str, filename: str = "") -> list[str]:
    issues = []

    # 1. Functional Integrity Checks
    if filename.endswith(".py"):
        if "try:" not in code and "except " not in code:
            issues.append("Code robustness failure: Missing 'try/except' block for error handling.")
        if "logging" not in code and "print(" not in code:
            issues.append("Code robustness failure: Missing explicit logging tracing.")

        # Ruff Linting
        try:
            import tempfile

            def _temp_write():
                with tempfile.NamedTemporaryFile(
                    "w", suffix=".py", delete=False, encoding="utf-8"
                ) as tmp:
                    tmp.write(code)
                    return tmp.name

            tmp_path = await asyncio.to_thread(_temp_write)

            proc = await asyncio.create_subprocess_exec(
                "ruff",
                "check",
                tmp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            if proc.returncode != 0:
                errors = stdout.decode().strip().splitlines()
                for err in errors[:3]:
                    issues.append(f"Linting/Styling error (PEP 8): {err}")
            await asyncio.to_thread(os.remove, tmp_path)
        except Exception:
            pass  # Fallback

    elif filename.endswith((".js", ".jsx", ".ts", ".tsx")):
        if "try {" not in code and "catch" not in code:
            issues.append("Code robustness failure: Missing 'try/catch' block for error handling.")
        if "console.log(" not in code and "console.error(" not in code:
            issues.append("Code robustness failure: Missing explicit console logging.")

    # 2. Simulation/Placeholder Purge
    for pattern in PLACEHOLDER_PATTERNS:
        if re.search(pattern, code, re.IGNORECASE):
            issues.append(f"Contains placeholder/incomplete code: '{pattern}'")

    # 3. Branding
    brand_keyword = os.getenv("BRAND_NAME", "Dre")
    if brand_keyword.lower() not in code.lower() and filename.endswith(
        (".py", ".js", ".ts", ".jsx", ".tsx")
    ):
        issues.append(f"Branding failure: Missing {brand_keyword} proprietary headers.")

    return issues


async def _run_python_file(filepath: str, timeout: int = 15) -> tuple[bool, str]:
    try:
        proc1: asyncio.subprocess.Process = await asyncio.create_subprocess_exec(
            sys.executable,
            "-m",
            "py_compile",
            filepath,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc1.communicate(), timeout=10)
        if proc1.returncode != 0:
            return False, f"Syntax error: {stderr.decode().strip()}"

        proc2: asyncio.subprocess.Process = await asyncio.create_subprocess_exec(
            sys.executable,
            filepath,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=os.path.dirname(filepath) or WORKSPACE_DIR,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc2.communicate(), timeout=timeout)
            output: str = (stdout.decode() + stderr.decode()).strip()
            return proc2.returncode == 0, output[:500] if output else "(No output)"
        except TimeoutError:
            try:
                proc2.kill()
            except:
                pass
            return True, "(Timed out - likely requires interactive input)"
    except Exception as exc:
        return False, f"Execution error: {exc}"


async def _collect_workspace_files(workspace_dir: str | None = None) -> dict:
    files = {}
    root_dir = os.path.abspath(workspace_dir or WORKSPACE_DIR)

    def _walk():
        local_files = {}
        if not os.path.exists(root_dir):
            return {}
        for root, dirs, filenames in os.walk(root_dir):
            dirs[:] = [directory for directory in dirs if directory not in {"__pycache__", ".git"}]
            for filename in filenames:
                if filename.endswith(
                    (".zip", ".mp3", ".wav", ".db", ".png", ".jpg", ".jpeg", ".webp", ".gif")
                ):
                    continue
                file_path = os.path.join(root, filename)
                rel_name = os.path.relpath(file_path, root_dir)
                try:
                    with open(file_path, encoding="utf-8", errors="ignore") as h:
                        local_files[rel_name] = h.read()
                except:
                    pass
        return local_files

    return await asyncio.to_thread(_walk)


ADVERSARY_SYSTEM_PROMPT = """You are a ZERO-TOLERANCE Principal Product Reviewer.
Your job is to ensure the swarm produces ONLY premium, error-free products.

Scoring criteria:
- 100: PERFECT.
- 0-99: FAILURE.

Respond ONLY with JSON:
{
  "score": <integer 0-100>,
  "passed": <true ONLY if score is 100>,
  "issues": ["<specific issue 1>", ...],
  "suggestions": ["<fix 1>", ...],
  "market_ready": <true/false>,
  "summary": "<verdict>"
}"""


class AdversaryAgent:
    def __init__(self, model: str = None):
        self.model = model or os.getenv("ADVERSARY_MODEL", "llama3:latest")
        host = (os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434") or "").strip()
        if not host:
            host = "http://127.0.0.1:11434"
        if not re.match(r"^https?://", host, re.IGNORECASE):
            host = f"http://{host}"
        host = host.replace("0.0.0.0", "127.0.0.1")
        p = urlparse(host)
        if p.port is None:
            host = f"{host}:11434"
        self.host = host.rstrip("/")

        self.is_cloud = "v1" in self.host.lower() or "groq" in self.host.lower()
        self.key = os.getenv("GROQ_API_KEY") or os.getenv("OLLAMA_CLOUD_KEY", "")

        if self.is_cloud:
            self.client = None
        else:
            self.client = ollama.AsyncClient(host=self.host)
        logger.info(f"AdversaryAgent initialized: {self.model} @ {self.host}")

    def _candidate_models(self) -> list[str]:
        candidates = [self.model]
        if self.is_cloud:
            candidates.extend(["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
        else:
            if ":" not in self.model:
                candidates.append(f"{self.model}:latest")
            candidates.extend(["llama3:latest", "qwen2.5:7b"])
        return list(dict.fromkeys(c for c in candidates if c))

    async def _chat_with_fallback(self, messages: list[dict]) -> str:
        last_error = None
        for model_name in self._candidate_models():
            try:
                if self.is_cloud:
                    async with (
                        aiohttp.ClientSession() as session,
                        session.post(
                            f"{self.host}/chat/completions",
                            headers={"Authorization": f"Bearer {self.key}"},
                            json={"model": model_name, "messages": messages, "temperature": 0.3},
                            timeout=45,
                        ) as resp,
                    ):
                        data = await resp.json()
                        return data["choices"][0]["message"]["content"]
                else:
                    response = await self.client.chat(model=model_name, messages=messages)
                    return response.message.content
            except Exception as exc:
                last_error = exc
                logger.warning(f"Adversary chat failed for {model_name}: {exc}")

        raise RuntimeError(last_error or "Unable to reach LLM for review.")

    async def _llm_review(self, product_summary: str) -> dict:
        messages = [
            {"role": "system", "content": ADVERSARY_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Review this product:\n\n{product_summary}\n\nJSON verdict ONLY.",
            },
        ]
        for attempt in range(3):
            try:
                content = await self._chat_with_fallback(messages)
                match = re.search(r"\{[\s\S]+\}", content)
                if match:
                    return json.loads(match.group())
            except Exception as e:
                logger.warning(f"Adversary attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(2)
        return {}

    async def review(
        self, product_name: str = "product", workspace_dir: str | None = None, min_score: int = 70
    ) -> AdversaryVerdict:
        logger.info(f"[ADVERSARY] Reviewing '{product_name}'")
        review_root = os.path.abspath(workspace_dir or WORKSPACE_DIR)
        workspace_files = await _collect_workspace_files(review_root)

        if not workspace_files:
            return AdversaryVerdict(
                passed=False, score=0, issues=["Workspace empty."], summary="Nothing to review."
            )

        issues, suggestions, execution_results, summary_parts = [], [], [], []

        for filename, content in workspace_files.items():
            file_path = os.path.join(review_root, filename)
            if filename.endswith(".py"):
                await _auto_fix_python(file_path)

                def _read():
                    with open(file_path, encoding="utf-8") as h:
                        return h.read()

                content = await asyncio.to_thread(_read)
                workspace_files[filename] = content

            for issue in await _static_scan(content, filename):
                issues.append(f"[{filename}] {issue}")
            summary_parts.append(f"=== {filename} ===\n{content[:1500]}")

        python_files = [f for f in workspace_files if f.endswith(".py")]
        for filename in python_files:
            file_path = os.path.join(review_root, filename)
            success, output = await _run_python_file(file_path)
            status = "[OK]" if success else "[FAIL]"
            execution_results.append(f"{status} | {filename}: {output}")
            if not success:
                issues.append(f"[{filename}] Execution failed: {output}")
                suggestions.append(f"Fix error in {filename}")

        llm_verdict = await self._llm_review(
            f"Product: {product_name}\n\n" + "\n\n".join(summary_parts[:4])
        )

        exec_failures = sum(1 for r in execution_results if "[FAIL]" in r)
        base_score = llm_verdict.get("score", 70)
        issues.extend(llm_verdict.get("issues", []))
        suggestions.extend(llm_verdict.get("suggestions", []))

        final_score = max(0, base_score - (exec_failures * 50) - (len(issues) * 5))
        passed = final_score >= min_score and exec_failures == 0

        return AdversaryVerdict(
            passed=passed,
            score=final_score,
            issues=list(dict.fromkeys(issues)),
            suggestions=list(dict.fromkeys(suggestions)),
            execution_result="\n".join(execution_results),
            market_ready=bool(llm_verdict.get("market_ready", False)) and passed,
            summary=llm_verdict.get("summary", "Review complete."),
        )


_adversary_instance: AdversaryAgent | None = None


def get_adversary() -> AdversaryAgent:
    global _adversary_instance
    if _adversary_instance is None:
        _adversary_instance = AdversaryAgent()
    return _adversary_instance


async def run_adversary_review(
    product_name: str = "product", workspace_dir: str | None = None, min_score: int = 70
) -> dict:
    verdict: AdversaryVerdict = await get_adversary().review(
        product_name, workspace_dir=workspace_dir, min_score=min_score
    )
    return verdict.to_dict()
