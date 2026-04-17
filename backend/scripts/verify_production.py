import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

load_dotenv()

from app.core.paths import WORKSPACE_DIR
from app.swarm.tools import assemble_full_product, package_product, validate_product


async def main():
    print("[*] Starting E2E Verification Cycle...")

    product_name = "Cloud_Verified_Asset_v9"
    niche = "End-to-End Validation Tools"
    product_type = "Script"
    specs = "Python script to test the robustness of a self-healing system deployment in the cloud."

    print(f"[*] Phase 1: Universal Assembly for '{product_name}'...")
    result = assemble_full_product(product_name, niche, product_type, specs)
    print(f"[RESULT] Assembly:\n{result}\n")

    print("[*] Phase 2: Peer-Review Quality Gate...")
    val_result = validate_product(product_name)
    print(f"[RESULT] Validation:\n{val_result}\n")

    print("[*] Phase 3: Packaging...")
    pkg_result = package_product(product_name)
    print(f"[RESULT] Packaging:\n{pkg_result}\n")

    zip_path = WORKSPACE_DIR / f"{product_name}.zip"
    if zip_path.exists():
        print("[SUCCESS] E2E Verified. Product packaged successfully.")
    else:
        print("[FAIL] Packaging failed.")


if __name__ == "__main__":
    asyncio.run(main())
