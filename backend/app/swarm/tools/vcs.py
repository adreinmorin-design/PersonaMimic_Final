import asyncio
import logging
from pydantic import BaseModel, Field
from app.core.paths import PROJECT_ROOT

logger = logging.getLogger("swarm.tools.vcs")

class VCSArgs(BaseModel):
    action: str = Field(..., pattern="^(status|add|commit|push|pull|sync|diff)$")
    message: str | None = None
    files: list[str] | None = None
    branch: str = "main"
    remote: str = "origin"
    run_quality: bool = True

async def vcs_manager(
    action: str, 
    message: str | None = None, 
    files: list[str] | None = None, 
    branch: str = "main", 
    remote: str = "origin",
    run_quality: bool = True
) -> str:
    """
    Industrial Version Control Management.
    Ensures code persistence to GitHub with optional quality gates.
    """
    try:
        match action:
            case "status":
                return await _run_git(["status"])
            case "diff":
                return await _run_git(["diff", "--stat"])
            case "add":
                if not files:
                    return "ERROR: No files specified to add."
                return await _run_git(["add"] + files)
            case "commit":
                if not message:
                    return "ERROR: Commit message required."
                
                if run_quality:
                    quality_res = await _run_quality_gate()
                    if "[FAIL]" in quality_res:
                        return f"COMMIT ABORTED: Quality Gate Failed.\n{quality_res}"
                
                if not files:
                    await _run_git(["add", "-A"])
                else:
                    await _run_git(["add"] + files)
                
                return await _run_git(["commit", "-m", message])
            case "push":
                return await _run_git(["push", remote, branch])
            case "pull":
                return await _run_git(["pull", remote, branch])
            case "sync":
                pull_res = await _run_git(["pull", remote, branch])
                if not message:
                    message = "Autonomous Sync: Updating repository state."
                commit_res = await vcs_manager("commit", message=message, run_quality=run_quality)
                push_res = await _run_git(["push", remote, branch])
                return f"SYNC LOG:\nPull: {pull_res}\nCommit: {commit_res}\nPush: {push_res}"
            case _:
                return f"ERROR: Unsupported VCS action '{action}'."
    except Exception as e:
        logger.error(f"VCS Error: {e}")
        return f"VCS Error: {str(e)}"

async def _run_git(args: list[str]) -> str:
    """Execute git commands safely."""
    try:
        process = await asyncio.create_subprocess_exec(
            "git", *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=PROJECT_ROOT
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60)
        
        output = stdout.decode().strip()
        errors = stderr.decode().strip()
        
        if process.returncode != 0:
            return f"[ERROR] Git {args[0]} failed (Code {process.returncode}):\n{errors or output}"
        
        return output or f"Git {args[0]} completed successfully."
    except asyncio.TimeoutError:
        return f"Git {args[0]} error: Timeout reached (60s)"
    except Exception as e:
        return f"Git {args[0]} error: {str(e)}"

async def _run_quality_gate() -> str:
    """Run ruff check and format as a pre-commit quality gate."""
    # 1. Format
    format_proc = await asyncio.create_subprocess_exec(
        "uv", "run", "ruff", "format", ".",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=PROJECT_ROOT
    )
    await format_proc.communicate()
    
    # 2. Check
    check_proc = await asyncio.create_subprocess_exec(
        "uv", "run", "ruff", "check", ".", "--fix",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=PROJECT_ROOT
    )
    stdout, stderr = await check_proc.communicate()
    
    if check_proc.returncode != 0:
        return f"[FAIL] Ruff check failed:\n{stdout.decode() or stderr.decode()}"
    
    return "[OK] Quality Gate Passed (Ruff)."
