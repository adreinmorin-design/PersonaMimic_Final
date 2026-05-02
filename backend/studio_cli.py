# © 2026 Dre's Autonomous Neural Interface | Studio CLI Bridge
#
# backend/studio_cli.py - High-Performance, Low-Overhead Swarm Interface
#

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime

# Add parent to path for app imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.database.database import SessionLocal
    from app.products.models import Product
    from app.swarm.models import TaskQueue
    from app.swarm.service import swarm_manager
except ImportError as e:
    import traceback

    traceback.print_exc()
    print(
        f"\nError: Could not import app modules ({e}). Ensure you are running from the backend directory."
    )
    sys.exit(1)


# ANSI Colors for a "Studio" feel
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    DIM = "\033[2m"


async def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def format_timestamp(dt):
    if not dt:
        return "N/A"
    if isinstance(dt, str):
        return dt[:19]
    return dt.strftime("%H:%M:%S")


async def render_dashboard():
    await clear_screen()
    print(
        f"{Colors.HEADER}{Colors.BOLD}=== PERSONAMIMIC STUDIO CLI BRIDGE v1.1 (LOW-OVERHEAD) ==={Colors.ENDC}"
    )
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Environment: Local\n")

    # 1. BRAIN STATUS
    print(f"{Colors.BLUE}{Colors.BOLD}--- ACTIVE SWARM NODES ---{Colors.ENDC}")
    status = swarm_manager.get_status()
    if not status:
        print(f"{Colors.DIM}No brains initialized.{Colors.ENDC}")
    else:
        for name, b in status.items():
            color = Colors.GREEN if b["running"] else Colors.FAIL
            run_status = "ONLINE " if b["running"] else "OFFLINE"
            phase = (b["phase"] or "IDLE").upper()
            task_info = f"Task #{b['task_id']}" if b["task_id"] else "WAITING"
            model_info = f"{Colors.DIM}({b['model']}){Colors.ENDC}"
            print(
                f"[{color}{run_status}{Colors.ENDC}] {Colors.BOLD}{name:12}{Colors.ENDC} | Phase: {Colors.CYAN}{phase:15}{Colors.ENDC} | {task_info:10} | {model_info}"
            )
    print()

    # 2. LATEST TASKS
    print(f"{Colors.BLUE}{Colors.BOLD}--- MISSION PIPELINE (Latest 5) ---{Colors.ENDC}")
    db = SessionLocal()
    try:
        tasks = db.query(TaskQueue).order_by(TaskQueue.id.desc()).limit(5).all()
        if not tasks:
            print(f"{Colors.DIM}No tasks in queue.{Colors.ENDC}")
        for t in tasks:
            status_color = (
                Colors.GREEN
                if t.status == "completed"
                else (Colors.WARNING if t.status == "running" else Colors.FAIL)
            )
            print(
                f"#{t.id:3} | {t.brain_name:12} | {status_color}{t.status:15}{Colors.ENDC} | {format_timestamp(t.created_at)}"
            )
    except Exception as e:
        print(f"{Colors.FAIL}Database Error: {e}{Colors.ENDC}")
    finally:
        db.close()
    print()

    # 3. LATEST PRODUCTS (Quality Gate)
    print(f"{Colors.BLUE}{Colors.BOLD}--- QUALITY GATE: COMPLETED ASSETS ---{Colors.ENDC}")
    db = SessionLocal()
    try:
        products = db.query(Product).order_by(Product.id.desc()).limit(3).all()
        if not products:
            print(f"{Colors.DIM}No products generated yet.{Colors.ENDC}")
        for p in products:
            score = p.adversary_score if p.adversary_score is not None else "N/A"
            score_color = (
                Colors.GREEN
                if (isinstance(score, (int, float)) and score >= 90)
                else (
                    Colors.WARNING
                    if isinstance(score, (int, float)) and score >= 70
                    else Colors.FAIL
                )
            )

            # Show "Quality Badge" based on score
            badge = "[ELITE]" if isinstance(score, (int, float)) and score >= 95 else "[STABLE]"
            if score == "N/A":
                badge = "[PENDING]"

            print(
                f"ID: {p.id:2} | {Colors.BOLD}{p.name:25}{Colors.ENDC} | Score: {score_color}{score:3}{Colors.ENDC} {badge} | Status: {p.status}"
            )
    except Exception as e:
        print(f"{Colors.FAIL}Database Error: {e}{Colors.ENDC}")
    finally:
        db.close()

    # 4. SWARM TELEMETRY
    print(f"\n{Colors.CYAN}{Colors.BOLD}--- SWARM INTELLIGENCE METRICS ---{Colors.ENDC}")
    print(
        f"Workflow: {Colors.GREEN}Adversarial Loop (Gen->Audit->Repair){Colors.ENDC} | Mode: {Colors.BOLD}High-Quality Sequential{Colors.ENDC}"
    )

    print(
        f"\n{Colors.WARNING}Options: [R] Refresh | [T] Trigger Mission | [S] Stop Brains | [Q] Quit{Colors.ENDC}"
    )


async def run_interactive():
    # Initialize swarm in headless mode
    print(f"{Colors.CYAN}Initializing Studio Engine...{Colors.ENDC}")
    await swarm_manager.initialize()

    while True:
        await render_dashboard()

        try:
            # We use a non-blocking way to wait for input
            choice = await asyncio.to_thread(input, "\nChoice > ")
            choice = choice.upper().strip()

            if choice == "Q":
                print(f"{Colors.WARNING}Purging system...{Colors.ENDC}")
                break
            elif choice == "R":
                continue
            elif choice == "S":
                print(f"{Colors.FAIL}Stopping all brains...{Colors.ENDC}")
                for b in swarm_manager.brains.values():
                    b.stop()
                await asyncio.sleep(1)
            elif choice == "T":
                niche = await asyncio.to_thread(
                    input, "Enter Target Niche (e.g. AI-SaaS, Fintech): "
                )
                if niche:
                    print(f"{Colors.GREEN}Injecting global directive: {niche}{Colors.ENDC}")
                    swarm_manager.set_directive(niche)
                    # Wake up brains
                    active = 0
                    for b in swarm_manager.brains.values():
                        if not b.running:
                            b.start()
                            active += 1
                    print(f"Activated {active} brains for mission.")
                    await asyncio.sleep(1)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"{Colors.FAIL}Error: {e}{Colors.ENDC}")
            await asyncio.sleep(2)


async def run_command(args):
    """Execute a single command without entering the loop."""
    print(f"{Colors.CYAN}Connecting to Studio Bridge...{Colors.ENDC}")
    await swarm_manager.initialize()

    if args.status:
        status = swarm_manager.get_status()
        print(json.dumps(status, indent=2))

    if args.stop:
        print("Stopping all brains...")
        for b in swarm_manager.brains.values():
            b.stop()
        print("Done.")

    if args.trigger:
        print(f"Triggering directive: {args.trigger}")
        swarm_manager.set_directive(args.trigger)
        for b in swarm_manager.brains.values():
            if not b.running:
                b.start()
        print("Mission engaged.")

    if args.list_products:
        db = SessionLocal()
        products = db.query(Product).order_by(Product.id.desc()).limit(10).all()
        for p in products:
            print(f"[{p.id}] {p.name} - Score: {p.adversary_score} - Status: {p.status}")
        db.close()


def main():
    parser = argparse.ArgumentParser(description="PersonaMimic Studio CLI Bridge")
    parser.add_argument("--status", action="store_true", help="Show current swarm status and exit")
    parser.add_argument("--stop", action="store_true", help="Stop all brains and exit")
    parser.add_argument("--trigger", type=str, help="Inject a global directive and start brains")
    parser.add_argument(
        "--list-products", action="store_true", help="List latest generated products"
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Run in interactive dashboard mode (default)",
    )
    parser.add_argument(
        "--lite", action="store_true", help="Run with reduced hardware footprint (2 brains)"
    )
    parser.add_argument(
        "--power", action="store_true", help="Run in 12-core optimized mode (3 brains)"
    )

    args = parser.parse_args()

    if args.lite:
        os.environ["STUDIO_LITE_MODE"] = "1"
        os.environ["STUDIO_POWER_MODE"] = "0"
        print(
            f"{Colors.WARNING}LITE MODE ENABLED: Reduced hardware footprint (2 Brains).{Colors.ENDC}"
        )

    if args.power:
        os.environ["STUDIO_LITE_MODE"] = "0"
        os.environ["STUDIO_POWER_MODE"] = "1"
        print(f"{Colors.CYAN}POWER MODE ENABLED: 12-Core Optimized (3 Brains).{Colors.ENDC}")

    # Default to interactive if no command args are provided
    is_cmd = args.status or args.stop or args.trigger or args.list_products

    try:
        if is_cmd and not args.interactive:
            asyncio.run(run_command(args))
        else:
            asyncio.run(run_interactive())
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Bridge connection terminated.{Colors.ENDC}")


if __name__ == "__main__":
    main()
