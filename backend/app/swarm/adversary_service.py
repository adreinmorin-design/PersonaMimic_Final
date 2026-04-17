"""
app/swarm/adversary_service.py - Peer Adversary Agent
An independent reviewer that pressure-tests generated products before release.
"""

import json
import logging
import os
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from urllib.parse import urlparse

import ollama
import requests

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


def _auto_fix_python(filepath: str):
    """
    AUTO-PILOT: Automatically fix formatting and trivial lint errors to save API costs.
    """
    try:
        # 1. Format code (PEP 8)
        subprocess.run(["ruff", "format", filepath], capture_output=True, check=False)
        # 2. Fix safe lint errors (unused imports, etc.)
        subprocess.run(["ruff", "check", "--fix", filepath], capture_output=True, check=False)
    except Exception as e:
        logger.warning(f"Auto-fix failed for {filepath}: {e}")


def _static_scan(code: str, filename: str = "") -> list[str]:
    issues = []

    # 1. Functional Integrity Checks
    if filename.endswith(".py"):
        if "try:" not in code and "except " not in code:
            issues.append("Code robustness failure: Missing 'try/except' block for error handling.")
        if "logging" not in code and "print(" not in code:
            issues.append("Code robustness failure: Missing explicit logging tracing.")

        # Ruff Linting (Premium Mandate)
        try:
            import tempfile

            with tempfile.NamedTemporaryFile(
                "w", suffix=".py", delete=False, encoding="utf-8"
            ) as tmp:
                tmp.write(code)
                tmp_path = tmp.name

            res = subprocess.run(["ruff", "check", tmp_path], capture_output=True, text=True)
            if res.returncode != 0:
                errors = res.stdout.strip().splitlines()
                for err in errors[:3]:
                    issues.append(f"Linting/Styling error (PEP 8): {err}")
            os.remove(tmp_path)
        except Exception:
            pass  # Fallback if ruff is missing

    elif filename.endswith((".js", ".jsx", ".ts", ".tsx")):
        if "try {" not in code and "catch" not in code:
            issues.append("Code robustness failure: Missing 'try/catch' block for error handling.")
        if "console.log(" not in code and "console.error(" not in code:
            issues.append("Code robustness failure: Missing explicit console logging.")

    # 2. Simulation/Placeholder Purge
    for pattern in PLACEHOLDER_PATTERNS:
        if re.search(pattern, code, re.IGNORECASE):
            issues.append(f"Contains placeholder/incomplete code: '{pattern}'")

    # 3. Branding & Premium Polish
    brand_keyword = os.getenv("BRAND_NAME", "Dre")
    if brand_keyword.lower() not in code.lower() and filename.endswith(
        (".py", ".js", ".ts", ".jsx", ".tsx")
    ):
        issues.append(
            f"Branding failure: Missing {brand_keyword} proprietary headers or copyright info."
        )

    return issues


def _run_python_file(filepath: str, timeout: int = 15) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", filepath],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return False, f"Syntax error: {result.stderr.strip()}"

        result = subprocess.run(
            [sys.executable, filepath],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.path.dirname(filepath) or WORKSPACE_DIR,
            input="",
        )
        output = (result.stdout + result.stderr).strip()
        return result.returncode == 0, output[:500] if output else "(No output - ran cleanly)"
    except subprocess.TimeoutExpired:
        return True, "(Timed out - likely requires interactive input, which is expected)"
    except Exception as exc:
        return False, f"Execution error: {exc}"


def _collect_workspace_files(workspace_dir: str | None = None) -> dict:
    files = {}
    root_dir = os.path.abspath(workspace_dir or WORKSPACE_DIR)
    try:
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
                relative_name = os.path.relpath(file_path, root_dir)
                try:
                    with open(file_path, encoding="utf-8", errors="ignore") as handle:
                        files[relative_name] = handle.read()
                except Exception as exc:
                    logger.debug("Skipping unreadable adversary file '%s': %s", relative_name, exc)
    except Exception as exc:
        logger.warning(f"Could not read workspace: {exc}")
    return files


ADVERSARY_SYSTEM_PROMPT = """You are a ZERO-TOLERANCE Principal Product Reviewer.
Your job is to ensure the swarm produces ONLY premium, error-free products. We do NOT release "good enough" software. We only release "Flawless" software.

Scoring criteria:
- 100: PERFECT. Studio-Grade. No issues, no linting errors, no placeholders.
- 0-99: FAILURE. REJECT. If there is even ONE minor issue (unused import, missing header, unclear variable), the product is a FAILURE.

Respond ONLY with JSON:
{
  "score": <integer 0-100>,
  "passed": <true ONLY if score is 100>,
  "issues": ["<specific issue 1>", ...],
  "suggestions": ["<fix 1>", ...],
  "market_ready": <true/false>,
  "summary": "<verdict>"
}

Be brutally obsessive. Any single error = Score < 100 = FAIL."""


class AdversaryAgent:
    def __init__(self, model: str = None):
        self.model = model or os.getenv("ADVERSARY_MODEL", "llama3:latest")
        host = (os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434") or "").strip()
        if not host:
            host = "http://127.0.0.1:11434"
        if not re.match(r"^https?://", host, re.IGNORECASE):
            host = f"http://{host}"
        host = host.replace("0.0.0.0", "127.0.0.1")
        parsed_host = urlparse(host)
        if parsed_host.port is None:
            host = f"{host}:11434"

        self.host = host.rstrip("/")

        # Hybrid Client Management
        self.is_cloud = (
            "v1" in self.host.lower()
            or "groq" in self.host.lower()
            or "cortex" in self.host.lower()
        )
        self.key = os.getenv("GROQ_API_KEY") or os.getenv("OLLAMA_CLOUD_KEY", "")

        if self.is_cloud:
            # Cloud OSS Mode: Direct HTTP to avoid proprietary SDKs
            self.client = None
            logger.info(f"AdversaryAgent [Cloud OSS Mode] Setup: {self.model} @ {self.host}")
        else:
            self.client = ollama.Client(host=self.host)
            logger.info(f"AdversaryAgent [Local Mode] Initialized: {self.model} @ {self.host}")

    def _candidate_models(self) -> list[str]:
        candidates = [self.model]
        if self.is_cloud:
            candidates.extend(
                ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
            )
        else:
            if ":" not in self.model:
                candidates.append(f"{self.model}:latest")
            candidates.extend(["llama3:latest", "qwen2.5:7b", "mistral:latest"])
        return list(dict.fromkeys(candidate for candidate in candidates if candidate))

    def _chat_with_fallback(self, messages: list[dict]) -> str:
        last_error = None

        for model_name in self._candidate_models():
            try:
                if self.is_cloud:
                    # Direct HTTP completion for OSS Cloud endpoints
                    response = requests.post(
                        f"{self.host.rstrip('/')}/chat/completions",
                        headers={"Authorization": f"Bearer {self.key}"},
                        json={"model": model_name, "messages": messages, "temperature": 0.3},
                        timeout=45,
                    )
                    response.raise_for_status()
                    return response.json()["choices"][0]["message"]["content"]
                else:
                    response = self.client.chat(model=model_name, messages=messages)
                    raw_message = (
                        response.message
                        if hasattr(response, "message")
                        else response.get("message", {})
                    )
                    content = getattr(raw_message, "content", None) or raw_message.get(
                        "content", ""
                    )
                    if content:
                        return content
            except Exception as exc:
                last_error = exc
                logger.warning(f"Adversary client chat failed for model {model_name}: {exc}")

            try:
                response = requests.post(
                    f"{self.host}/api/chat",
                    json={"model": model_name, "messages": messages, "stream": False},
                    timeout=120,
                )
                response.raise_for_status()
                payload = response.json()
                content = payload.get("message", {}).get("content", "")
                if content:
                    return content
            except Exception as exc:
                last_error = exc
                logger.warning(f"Adversary HTTP chat failed for model {model_name}: {exc}")

        raise RuntimeError(last_error or "Unable to reach Ollama for adversary review.")

    def _llm_review(self, product_summary: str) -> dict:
        messages = [
            {"role": "system", "content": ADVERSARY_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Review this digital product:\n\n{product_summary}\n\nOutput only the JSON verdict.",
            },
        ]
        for attempt in range(3):
            try:
                content = self._chat_with_fallback(messages)
                json_match = re.search(r"\{[\s\S]+\}", content)
                if json_match:
                    return json.loads(json_match.group())
            except json.JSONDecodeError as exc:
                logger.warning(f"Adversary JSON parse error (attempt {attempt + 1}): {exc}")
            except Exception as exc:
                logger.error(f"Adversary LLM error (attempt {attempt + 1}): {exc}")
                time.sleep(3)
        return {}

    def review(
        self,
        product_name: str = "product",
        workspace_dir: str | None = None,
        min_score: int = 70,
    ) -> AdversaryVerdict:
        logger.info(f"[ADVERSARY] Starting review of '{product_name}'")
        review_root = os.path.abspath(workspace_dir or WORKSPACE_DIR)
        workspace_files = _collect_workspace_files(review_root)

        if not workspace_files:
            return AdversaryVerdict(
                passed=False,
                score=0,
                issues=["Workspace is empty - no product files found."],
                suggestions=["Build the product files before running adversary check."],
                execution_result="No files to test.",
                summary="Nothing to review. Product not built yet.",
            )

        issues: list[str] = []
        suggestions: list[str] = []
        execution_results: list[str] = []
        files_summary_parts = []

        for filename, content in workspace_files.items():
            file_path = os.path.join(review_root, filename)

            # Auto-Fix before scanning to reduce API costs
            if filename.endswith(".py"):
                _auto_fix_python(file_path)
                # Re-read content after auto-fix
                try:
                    with open(file_path, encoding="utf-8") as h:
                        workspace_files[filename] = h.read()
                        content = workspace_files[filename]
                except Exception:
                    pass

            for issue in _static_scan(content, filename):
                issues.append(f"[{filename}] {issue}")
            files_summary_parts.append(f"=== {filename} ===\n{content[:1500]}")

        python_files = [filename for filename in workspace_files if filename.endswith(".py")]
        if python_files:
            for filename in python_files:
                file_path = os.path.join(review_root, filename)
                success, output = _run_python_file(file_path)
                status = "[OK]" if success else "[FAIL]"
                execution_results.append(f"{status} | {filename}: {output}")
                if not success:
                    issues.append(f"[{filename}] Execution failed: {output}")
                    suggestions.append(f"Fix the error in {filename}: {output[:200]}")
        else:
            execution_results.append("No Python files to execute.")

        if not any(
            "readme" in filename.lower() or "description" in filename.lower()
            for filename in workspace_files
        ):
            suggestions.append("Add a README.md / description file - buyers need documentation.")

        product_summary = f"Product name: {product_name}\n\nFiles:\n" + "\n\n".join(
            files_summary_parts[:4]
        )
        llm_verdict = self._llm_review(product_summary)

        exec_failures = sum(1 for result in execution_results if "[FAIL]" in result)
        placeholder_hits = len([issue for issue in issues if "placeholder" in issue.lower()])
        static_score = 95 - (exec_failures * 25) - (placeholder_hits * 15)
        static_score -= max(0, len(issues) - exec_failures) * 5
        base_score = llm_verdict.get("score", max(0, static_score))

        issues.extend(llm_verdict.get("issues", []))
        suggestions.extend(llm_verdict.get("suggestions", []))

        final_score = max(0, base_score - (exec_failures * 50) - (len(issues) * 15))
        passed = final_score == 100 and exec_failures == 0

        verdict = AdversaryVerdict(
            passed=passed,
            score=final_score,
            issues=list(dict.fromkeys(issues)),
            suggestions=list(dict.fromkeys(suggestions)),
            execution_result="\n".join(execution_results),
            market_ready=bool(llm_verdict.get("market_ready", False)) and passed,
            summary=llm_verdict.get("summary", "Static adversary review complete."),
        )

        logger.info(
            f"[ADVERSARY] Verdict for '{product_name}': passed={verdict.passed} score={verdict.score}"
        )
        return verdict


_adversary_instance: AdversaryAgent | None = None


def get_adversary() -> AdversaryAgent:
    global _adversary_instance
    if _adversary_instance is None:
        _adversary_instance = AdversaryAgent()
    return _adversary_instance


def run_adversary_review(
    product_name: str = "product",
    workspace_dir: str | None = None,
    min_score: int = 70,
) -> dict:
    verdict = get_adversary().review(product_name, workspace_dir=workspace_dir, min_score=min_score)
    return verdict.to_dict()
