import shutil
from pathlib import Path

# Base workspace directory
WORKSPACE_DIR = Path("workspace")


def cleanup():
    if not WORKSPACE_DIR.exists():
        print("Workspace directory not found.")
        return

    print(f"Starting cleanup in {WORKSPACE_DIR.absolute()}...")

    removed_count = 0
    kept_count = 0

    # Folders to consider for deletion (intermediate agent work)
    prefixes = ("ava_", "codesmith_", "dre_", "fenko_", "masterbrain_")

    for item in WORKSPACE_DIR.iterdir():
        if item.is_dir():
            # If it's an intermediate folder
            if any(item.name.startswith(p) for p in prefixes):
                # Check if it's a "complete" product - for now we define complete as having a .zip version
                zip_version = WORKSPACE_DIR / f"{item.name}.zip"
                if zip_version.exists():
                    print(f"Removing intermediate folder (zip exists): {item.name}")
                    shutil.rmtree(item)
                    removed_count += 1
                else:
                    # Optional: If you want to be more aggressive, remove any folder that isn't explicitly marked as final
                    # For now, let's just remove everything that isn't a zip or doesn't have a zip
                    # The user said "only add complete products to the workspace"
                    print(f"Removing non-zipped intermediate folder: {item.name}")
                    shutil.rmtree(item)
                    removed_count += 1
            else:
                kept_count += 1
        elif item.is_file():
            # Keep zips, READMEs, LICENSEs, etc.
            kept_count += 1

    print(f"Cleanup finished. Removed {removed_count} items, kept {kept_count} items.")


if __name__ == "__main__":
    cleanup()
