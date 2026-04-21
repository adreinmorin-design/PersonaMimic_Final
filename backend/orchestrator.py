import asyncio
import datetime
import json
import os
import sys
import traceback

import aiohttp


# Production standard: Dedicated JSON logger for the orchestrator
class StructuredLogger:
    def __init__(self, service_name: str):
        self.service_name = service_name

    def _log(self, level: str, message: str, **kwargs):
        log_entry = {
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "level": level,
            "service": self.service_name,
            "message": message,
            **kwargs,
        }
        print(json.dumps(log_entry), flush=True)

    def info(self, message: str, **kwargs):
        self._log("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._log("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs):
        self._log("ERROR", message, **kwargs)
        if kwargs.get("traceback"):
            traceback.print_exc()

    def debug(self, message: str, **kwargs):
        self._log("DEBUG", message, **kwargs)


logger = StructuredLogger("ORCHESTRATOR")

# Constants
OLLAMA_PORT = 11434
OLLAMA_URL = f"http://127.0.0.1:{OLLAMA_PORT}"
BACKEND_URL = "http://127.0.0.1:8055"
FRONTEND_URL = "http://127.0.0.1:5173"
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(os.path.dirname(BACKEND_DIR), "frontend")


class AIOrchestrator:
    def __init__(self):
        self.processes: dict[str, asyncio.subprocess.Process | None] = {
            "ollama": None,
            "backend": None,
            "frontend": None,
        }
        self.stop_requested = asyncio.Event()

    def _is_admin(self) -> bool:
        """Check for administrative privileges on Windows."""
        try:
            import ctypes

            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception as exc:
            logger.debug(f"Admin privilege check failed: {exc}")
            return False

    async def preflight_cleanup(self):
        """Guard-heavy cleanup to ensure consistent state."""
        logger.info("Executing pre-flight process termination...")
        current_pid = os.getpid()

        # Name-based cleanup with guard (Avoid killing ourselves: no python.exe or uvicorn.exe here)
        kill_targets = ["ollama.exe", "ollama app.exe", "node.exe"]
        for target in kill_targets:
            try:
                # Use taskkill /F /T but don't fail if already gone
                await asyncio.create_subprocess_shell(
                    f'taskkill /F /T /IM "{target}"',
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )
            except Exception as e:
                logger.debug(f"Taskkill failed for {target}: {e}")

        # Port-based cleanup (More reliable than process name)
        for port in [8055, 5173]:
            await self._kill_process_on_port(port, current_pid)

        # Infrastructure Boot (NAT, Redis & Postgres via Docker)
        logger.info("Booting supporting infrastructure (NATS/Redis/Postgres)...")
        try:
            # Check if docker is running first (with 5s timeout)
            try:
                docker_check = await asyncio.create_subprocess_exec(
                    "docker",
                    "info",
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )
                await asyncio.wait_for(docker_check.wait(), timeout=5.0)

                if docker_check.returncode == 0:
                    infra_proc = await asyncio.create_subprocess_exec(
                        "docker-compose",
                        "up",
                        "-d",
                        "nats",
                        "redis",
                        "postgres",
                        cwd=os.path.dirname(BACKEND_DIR),
                        stdout=asyncio.subprocess.DEVNULL,
                        stderr=asyncio.subprocess.DEVNULL,
                    )
                    await asyncio.wait_for(infra_proc.wait(), timeout=15.0)
                    logger.info("Infrastructure services (NATS/Redis/Postgres) signaled to start.")
                else:
                    logger.warning("Docker NOT RUNNING. Using local fallbacks.")
            except TimeoutError:
                logger.warning("Docker check timed out. Proceeding in degraded mode.")
        except Exception as e:
            logger.warning(
                f"Could not start Docker infrastructure: {e}. Falling back to degraded mode."
            )

        logger.info("Pre-flight cleanup and infrastructure check complete.")

    async def _kill_process_on_port(self, port: int, current_pid: int):
        """Atomic helper to clear port bindings."""
        try:
            # We use PowerShell for more robust process identification
            ps_cmd = f"Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess"
            proc = await asyncio.create_subprocess_exec(
                "powershell",
                "-Command",
                ps_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            for pid_str in stdout.decode().splitlines():
                pid = pid_str.strip()
                if pid and pid.isdigit() and int(pid) != current_pid and pid != "0":
                    logger.info(f"Terminating rogue PID {pid} on port {port}")
                    # Try Stop-Process first (PowerShell) then taskkill
                    await asyncio.create_subprocess_shell(
                        f'powershell -Command "Stop-Process -Id {pid} -Force -ErrorAction SilentlyContinue"',
                        stdout=asyncio.subprocess.DEVNULL,
                        stderr=asyncio.subprocess.DEVNULL,
                    )
                    await asyncio.create_subprocess_shell(
                        f"taskkill /F /T /PID {pid}",
                        stdout=asyncio.subprocess.DEVNULL,
                        stderr=asyncio.subprocess.DEVNULL,
                    )
        except Exception as e:
            logger.debug(f"Failed to clear port {port}: {e}")

    async def execute_agent_action(self, url: str) -> bool:
        """Asynchronous action executor using aiohttp (Industrial Standard)."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=2) as response:
                    return response.status == 200
        except Exception as exc:
            logger.debug(f"Action failed for {url}: {exc}")
            return False

    async def check_ollama_health(self) -> bool:
        """Ping Ollama endpoint."""
        return await self.execute_agent_action(OLLAMA_URL)

    async def ensure_llm_models(self):
        """Ensure required local models are downloaded with non-blocking feedback."""
        required_models = ["qwen2.5:7b", "qwen2.5-coder:32b", "deepseek-r1:7b"]
        logger.info("Verifying LLM model availability...")

        for model in required_models:
            try:
                # Check list via async process
                process = await asyncio.create_subprocess_exec(
                    "ollama", "list", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                stdout, _ = await process.communicate()

                if model not in stdout.decode():
                    logger.warning(
                        f"Model '{model}' MISSING. Pulling from library (this may take 2-5 minutes)..."
                    )
                    # Pull with live logging logic could go here, but for now we wait asynchronously
                    pull_proc = await asyncio.create_subprocess_exec(
                        "ollama",
                        "pull",
                        model,
                        stdout=asyncio.subprocess.DEVNULL,
                        stderr=asyncio.subprocess.DEVNULL,
                    )
                    await pull_proc.wait()
                    logger.info(f"Model '{model}' successfully pulled.")
                else:
                    logger.info(f"Model '{model}' verified.")
            except Exception as e:
                logger.error(f"Failed to verify/pull model '{model}': {e}")

    async def start_ollama(self):
        """Logic-gated Ollama bootstrapper."""
        if await self.check_ollama_health():
            logger.info("Ollama engine already online.")
            await self.ensure_llm_models()
            return

        logger.warning("Ollama offline. Booting service...")
        try:
            # We use CREATE_NO_WINDOW on Windows to prevent popups
            self.processes["ollama"] = await asyncio.create_subprocess_exec(
                "ollama",
                "serve",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
                creationflags=0x08000000 if os.name == "nt" else 0,
            )
        except FileNotFoundError:
            logger.error("Ollama executable NOT FOUND. Install from ollama.com")
            sys.exit(1)

        # Wait Loop with Guard
        for _attempt in range(15):
            await asyncio.sleep(2)
            if await self.check_ollama_health():
                logger.info("Ollama engine verified ONLINE.")
                await self.ensure_llm_models()
                return

        logger.error("Ollama failed to respond after 30s sequence.")
        sys.exit(1)

    async def start_backend(self):
        """Industrial uvicorn launch via absolute uv."""
        logger.info("Launching AI Backend via absolute uv...")
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{BACKEND_DIR}:{env.get('PYTHONPATH', '')}"

        # Use absolute path for uv to ensure execution
        uv_path = r"C:\Users\Albert Morin\.local\bin\uv.exe"
        if not os.path.exists(uv_path):
            uv_path = "uv"

        self.processes["backend"] = await asyncio.create_subprocess_exec(
            uv_path,
            "run",
            "uvicorn",
            "main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8055",
            "--backlog",
            "2048",
            "--timeout-keep-alive",
            "30",
            cwd=BACKEND_DIR,
            env=env,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

    async def start_frontend(self):
        """Frontend Vite runner."""
        exists = await asyncio.to_thread(os.path.exists, FRONTEND_DIR)
        if not exists:
            logger.warning("Frontend directory missing. Skipping UI launch.")
            return

        logger.info("Launching UX Dashboard via npm...")
        cmd = "npm run dev"
        self.processes["frontend"] = await asyncio.create_subprocess_shell(
            cmd, cwd=FRONTEND_DIR, stdout=sys.stdout, stderr=sys.stderr
        )

    async def watchdog_task(self):
        """Self-healing health check loop."""
        logger.info("Watchdog initialized.")
        while not self.stop_requested.is_set():
            await asyncio.sleep(60)

            # Check backend process
            if self.processes["backend"] and self.processes["backend"].returncode is not None:
                logger.error("Backend process CRASHED. Attempting restart...")
                await self.start_backend()

            # Check frontend process
            if self.processes["frontend"] and self.processes["frontend"].returncode is not None:
                logger.error("Frontend process CRASHED. Attempting restart...")
                await self.start_frontend()

            # Health Pings
            if not await self.execute_agent_action(BACKEND_URL):
                logger.warning("Backend unresponsive to HTTP. Forcing restart...")
                await self._stop_process("backend")
                await self.start_backend()

    async def _stop_process(self, name: str):
        """Graceful termination with timeout."""
        proc = self.processes.get(name)
        if not proc:
            return

        logger.info(f"Stopping service: {name}")
        proc.terminate()
        try:
            await asyncio.wait_for(proc.wait(), timeout=5.0)
        except TimeoutError:
            logger.warning(f"Force killing {name} (timeout reached)")
            proc.kill()
        self.processes[name] = None

    async def shutdown(self):
        """Graceful orchestral shutdown."""
        self.stop_requested.set()
        logger.info("System shutdown sequence engaged.")

        # We shutdown in reverse order of criticality
        await self._stop_process("frontend")
        await self._stop_process("backend")

        # ONLY kill Ollama if we started it. If it was already running, leave it.
        if self.processes["ollama"]:
            await self._stop_process("ollama")

        logger.info("All systems purged. Safe to exit.")


async def main():
    orchestrator = AIOrchestrator()
    try:
        # Pre-flight
        await orchestrator.preflight_cleanup()

        # Parallel Boot Sequence via TaskGroup
        async with asyncio.TaskGroup() as tg:
            # Step 1: Core Engine
            await orchestrator.start_ollama()

            # Step 2: API & UI
            await orchestrator.start_backend()
            logger.info("Waiting for Neural Synapse stabilization (25s)...")
            await asyncio.sleep(
                25
            )  # Extended stabilization for staggered brain boot and voice model load
            await orchestrator.start_frontend()

            # Step 3: Lifecycle Management
            tg.create_task(orchestrator.watchdog_task())

            logger.info("=" * 50)
            logger.info("SYSTEM ONLINE: PREMIMUM NEURAL INTERFACE READY")
            logger.info(f"API: {BACKEND_URL}")
            logger.info(f"UI:  {FRONTEND_URL}")
            logger.info("=" * 50)

    except KeyboardInterrupt:
        logger.info("Interrupt detected.")
    except Exception as e:
        logger.error(f"Critical orchestrator failure: {e}", traceback=True)
        if hasattr(e, "exceptions"):
            for idx, sub_e in enumerate(e.exceptions):
                logger.error(f"  Sub-exception {idx}: {sub_e}")
    finally:
        await orchestrator.shutdown()


if __name__ == "__main__":
    import contextlib

    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
