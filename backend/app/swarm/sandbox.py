"""
app/swarm/sandbox.py - Industrial Code Sandbox
Implements 'Run-and-Kill' isolation using Docker.
Supports gVisor (runsc) if configured in the host environment.
"""

import logging
import os
import subprocess
import tempfile
import uuid

logger = logging.getLogger("swarm.sandbox")


class SandboxRuntime:
    def __init__(self, image: str = "python:3.12-slim-bookworm"):
        self.image = image
        self.runtime = os.getenv("DOCKER_RUNTIME", "runc")  # Set to 'runsc' for gVisor

    def execute_python(self, code: str, timeout: int = 30) -> str:
        """Execute Python code in a disposable container."""
        job_id = f"sandbox_{uuid.uuid4().hex[:8]}"
        with tempfile.TemporaryDirectory() as tmpdir:
            script_path = os.path.join(tmpdir, "execute_me.py")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(code)

            # Map the temp file into the container
            # We use --rm for 'Run-and-Kill' behavior
            cmd = [
                "docker",
                "run",
                "--rm",
                "--name",
                job_id,
                "--runtime",
                self.runtime,
                "--network",
                "none",  # Total isolation
                "-v",
                f"{script_path}:/app/execute_me.py:ro",
                self.image,
                "python",
                "/app/execute_me.py",
            ]

            try:
                logger.info(f"[SANDBOX] Launching {job_id}...")
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
                output = res.stdout if res.stdout else res.stderr
                return output if output else "(Execution completed with no output)"
            except subprocess.TimeoutExpired:
                # Force kill if timeout didn't work smoothly
                subprocess.run(["docker", "kill", job_id], capture_output=True)
                return "Error: Sandbox execution timed out."
            except Exception as e:
                logger.error(f"[SANDBOX] Fault: {e}")
                return f"Error: Sandbox failure: {str(e)}"

    def execute_shell(self, command: str, timeout: int = 30) -> str:
        """Execute a shell command in the sandbox."""
        job_id = f"sandbox_sh_{uuid.uuid4().hex[:8]}"
        cmd = [
            "docker",
            "run",
            "--rm",
            "--name",
            job_id,
            "--runtime",
            self.runtime,
            "--network",
            "none",
            self.image,
            "sh",
            "-c",
            command,
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return res.stdout if res.stdout else res.stderr
        except Exception as e:
            return f"Error: Sandbox Shell failure: {str(e)}"


# Singleton sandbox
sandbox = SandboxRuntime()
