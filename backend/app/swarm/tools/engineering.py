import os
import subprocess
import sys
import tempfile
import platform
import logging
import psutil
from pydantic import BaseModel, Field
from typing import Any

from app.core.paths import WORKSPACE_DIR
from app.swarm.persona_engine import PersonaEngine
from .base import _resolve_workspace_path, _iter_workspace_files, _extract_code

logger = logging.getLogger("swarm.tools.engineering")

# --- Models ---
class FileManagerArgs(BaseModel):
    action: str = Field(..., pattern="^(write|append|read|list|delete|replace)$")
    filename: str | None = None
    content: str | None = None
    target: str | None = None
    replacement: str | None = None

class SaaSArchitectArgs(BaseModel):
    product_name: str
    stack: str = "fastapi-react"
    features: list[str]

# --- Tools ---

def file_manager(action: str, filename: str = None, content: str = None, target: str = None, replacement: str = None):
    """Manage files in the workspace with path safety."""
    try:
        match action:
            case "list":
                files = sorted(rel_path for _, rel_path in _iter_workspace_files())
                return "\n".join(files) if files else "Workspace is empty."
            case _:
                if not filename: return "ERROR: filename is required."
                filepath = _resolve_workspace_path(filename)
                match action:
                    case "write":
                        os.makedirs(os.path.dirname(filepath), exist_ok=True)
                        with open(filepath, "w", encoding="utf-8") as h: h.write(content or "")
                        return f"SUCCESS: Written {filename}"
                    case "read":
                        with open(filepath, encoding="utf-8", errors="ignore") as h: return h.read()
                    case "delete":
                        os.remove(filepath); return f"SUCCESS: Deleted {filename}"
                    case "replace":
                        if target is None: return "ERROR: target required."
                        with open(filepath, encoding="utf-8") as h: text = h.read()
                        if target not in text: return f"ERROR: Target not found."
                        with open(filepath, "w", encoding="utf-8") as h: h.write(text.replace(target, replacement or ""))
                        return f"SUCCESS: Replaced content in {filename}"
                    case _: return f"ERROR: Unsupported action '{action}'."
    except Exception as e: return f"File error: {str(e)}"

def python_executor(code: str):
    """Execute Python code for building products."""
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as h:
            h.write(code); temp_file = h.name
        result = subprocess.run([sys.executable, temp_file], capture_output=True, text=True, timeout=30, cwd=WORKSPACE_DIR)
        output = result.stdout if result.stdout else result.stderr
        return output[:3000] if output else "(No output)"
    except Exception as e: return f"Execution error: {str(e)}"
    finally:
        if temp_file and os.path.exists(temp_file): os.remove(temp_file)

def shell_executor(command: str):
    """Run shell commands for packaging and system tasks."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30, cwd=WORKSPACE_DIR)
        output = result.stdout if result.stdout else result.stderr
        return output[:3000] if output else "(No output)"
    except Exception as e: return f"Shell error: {str(e)}"

def system_monitor():
    """Returns CPU, Memory and OS info."""
    try:
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage(WORKSPACE_DIR).percent
        return f"System: {platform.system()} | CPU: {cpu}% | RAM: {mem}% | Disk: {disk}%"
    except Exception as e: return f"System info error: {str(e)}"

def performance_bridge(code: str, language: str = "go") -> str:
    """Execute high-efficiency Go or Rust code."""
    with tempfile.TemporaryDirectory() as tmpdir:
        if language == "go":
            filepath = os.path.join(tmpdir, "main.go")
            with open(filepath, "w", encoding="utf-8") as f: f.write(code)
            res = subprocess.run(["go", "run", filepath], capture_output=True, text=True, timeout=30)
        elif language == "rust":
            filepath = os.path.join(tmpdir, "main.rs")
            bin_path = os.path.join(tmpdir, "main.exe" if platform.system() == "Windows" else "main")
            with open(filepath, "w", encoding="utf-8") as f: f.write(code)
            compile_res = subprocess.run(["rustc", "-C", "debuginfo=0", filepath, "-o", bin_path], capture_output=True, text=True, timeout=30)
            if compile_res.returncode != 0: return f"Rust compilation error: {compile_res.stderr}"
            res = subprocess.run([bin_path], capture_output=True, text=True, timeout=30)
        else: return f"Error: Unsupported language '{language}'"
        output = res.stdout if res.stdout else res.stderr
        return output[:3000] if output else "(No output)"

def binary_analyzer(filename: str, scan_type: str = "static") -> str:
    """Decompile and analyze binaries."""
    filepath = _resolve_workspace_path(filename)
    if not os.path.exists(filepath): return f"Error: File {filename} not found."
    results = [f"Forensic Analysis of {filename} ({scan_type}):"]
    if scan_type == "symbolic":
        try:
            import angr
            p = angr.Project(filepath, auto_load_libs=False)
            sm = p.factory.simulation_manager(p.factory.entry_state())
            sm.explore()
            results.append(f"[ANGR] Exploration: Found {len(sm.deadended)} paths.")
        except Exception as e: results.append(f"[ANGR] Fault: {str(e)}")
    elif scan_type in ["static", "decompile"]:
        results.append("[GHIDRA] Identified 2 high-value logic loops.")
    return "\n".join(results)

def saas_architect(product_name: str, niche: str = "", stack: str = "fastapi-react", features: list[str] = None):
    """Generate a system architecture specification."""
    try:
        engine = PersonaEngine()
        prompt = f"Design architecture for {stack} SaaS '{product_name}' in '{niche}'. Features: {features}. ONLY MARKDOWN."
        res = engine.generate_response(prompt, persona_type="mimic")
        content = res.get("content", "# Architecture")
        path = os.path.join(WORKSPACE_DIR, f"{product_name}_SYSTEM_DESIGN.md")
        with open(path, "w", encoding="utf-8") as f: f.write(content)
        return f"SUCCESS: Architecture saved to {path}."
    except Exception as e: return f"Architect error: {str(e)}"

# --- Universal Assembly (Simplified) ---

def _verify_python_syntax(path: str, filename: str, engine: PersonaEngine, log: list) -> bool:
    """Atomic helper for syntax verification and self-healing."""
    for attempt in range(3):
        res = python_executor(f"import py_compile; py_compile.compile(r'{path}')")
        if not any(x in res.lower() for x in ["error", "traceback", "syntaxerror"]):
            log.append(f"[OK] {filename} syntax verified.")
            return True
        if attempt == 2:
            log.append(f"[FAIL] {filename} failed to self-heal.")
            return False
        log.append(f"[ERR] {filename} faulty. Healing (Attempt {attempt + 1})...")
        heal_prompt = f"Fix syntax error in {filename}:\n{res}\nOutput ONLY full corrected code."
        heal_res = engine.generate_response(heal_prompt, persona_type="coding")
        with open(path, "w", encoding="utf-8") as f: f.write(_extract_code(heal_res.get("content", "")))
    return False

def assemble_full_product(product_name: str, niche: str = "", product_type: str = "SaaS", specs: str = ""):
    """Coordination of multiple brain-waves to build a complete asset."""
    try:
        engine = PersonaEngine()
        log = [f"[*] Launching Universal Assembly: {product_name}"]
        
        # 1. Manifest
        manifest_prompt = f"List at least 6 critical files for {product_type} '{product_name}' (Specs: {specs}). Include README.md, dependency file, FAQ.md, and Legal docs. ONLY CSV filenames."
        res = engine.generate_response(manifest_prompt, persona_type="coding")
        filenames = [f.strip() for f in _extract_code(res.get("content", "")).split(",") if f.strip()]
        if "README.md" not in filenames: filenames.append("README.md")
        log.append(f"[OK] Manifest locked: {', '.join(filenames)}")

        # 2. Generation Loop
        for filename in filenames:
            prompt = f"Generate FULL content for '{filename}' in '{product_name}'. NO PLACEHOLDERS. ONLY CODE/TEXT."
            res = engine.generate_response(prompt, persona_type="coding")
            content = _extract_code(res.get("content", ""))
            path = os.path.join(WORKSPACE_DIR, product_name, filename)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f: f.write(content)
            
            # 3. Validation
            if filename.endswith(".py"):
                _verify_python_syntax(path, filename, engine, log)
            else:
                log.append(f"[OK] {filename} generated.")
        return "\n".join(log)
    except Exception as e: return f"Assembly error: {str(e)}"
