import logging
import os
import re
import shutil
import tempfile
from typing import Any

from app.core.paths import WORKSPACE_DIR
from app.swarm.tool_runtime import (
    FACTORY_MIN_MARKETING_CHARS,
    FACTORY_MIN_README_CHARS,
    FACTORY_MIN_SOURCE_CHARS,
    FACTORY_MIN_TITLE_CHARS,
)

SOURCE_FILE_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx"}
TEXT_FILE_EXTENSIONS = SOURCE_FILE_EXTENSIONS | {
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".csv",
    ".html",
    ".css",
}
IMAGE_FILE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
LOW_VALUE_PATTERNS = [
    r"\bhello world\b",
    r"\blorem ipsum\b",
    r"\bplaceholder\b",
    r"\bsample project\b",
    r"\bdemo app\b",
    r"\bchange me\b",
]

logger = logging.getLogger("swarm.workspace")


def resolve_workspace_path(filename: str | None = None) -> str:
    base = os.path.abspath(os.fspath(WORKSPACE_DIR))
    candidate = base if not filename else os.path.abspath(os.path.join(base, filename))
    if os.path.commonpath([candidate, base]) != base:
        raise ValueError("Path escapes workspace boundary.")
    return candidate


def iter_workspace_files(selected_files: list[str] | None = None):
    workspace_root = os.fspath(WORKSPACE_DIR)
    if selected_files:
        seen = set()
        for relative_name in selected_files:
            resolved = resolve_workspace_path(relative_name)
            if os.path.isdir(resolved):
                for root, _, files in os.walk(resolved):
                    for file_name in files:
                        abs_path = os.path.join(root, file_name)
                        rel_path = os.path.relpath(abs_path, workspace_root)
                        if rel_path not in seen:
                            seen.add(rel_path)
                            yield abs_path, rel_path
            elif os.path.isfile(resolved):
                rel_path = os.path.relpath(resolved, workspace_root)
                if rel_path not in seen:
                    seen.add(rel_path)
                    yield resolved, rel_path
        return

    for root, dirs, files in os.walk(workspace_root):
        dirs[:] = [directory for directory in dirs if directory != "__pycache__"]
        for file_name in files:
            abs_path = os.path.join(root, file_name)
            rel_path = os.path.relpath(abs_path, workspace_root)
            yield abs_path, rel_path


def normalize_product_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (name or "").strip().lower()).strip("_")


def infer_product_files(product_name: str, files: list[str] | None = None) -> list[str] | None:
    if files:
        return files

    inferred: list[str] = []
    product_roots: list[str] = []
    seen = set()
    normalized_name = normalize_product_name(product_name)
    candidates = [
        product_name,
        (product_name or "").replace(" ", "_"),
        (product_name or "").replace(" ", "-"),
        normalized_name,
    ]

    workspace_root = os.fspath(WORKSPACE_DIR)
    for candidate in candidates:
        candidate = (candidate or "").strip().strip("/\\")
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        try:
            resolved = resolve_workspace_path(candidate)
        except ValueError:
            continue
        if os.path.exists(resolved):
            relative_path = os.path.relpath(resolved, workspace_root)
            inferred.append(relative_path)
            if os.path.isdir(resolved):
                product_roots.append(relative_path)

    if not inferred:
        return None

    support_paths = ("README.md", "LICENSE", "requirements.txt", "MARKETING.md", "assets")
    support_candidates = []
    if product_roots:
        primary_root = product_roots[0]
        support_candidates.extend(
            os.path.join(primary_root, support_path) for support_path in support_paths
        )
    else:
        support_candidates.extend(support_paths)

    for support_path in support_candidates:
        try:
            resolved = resolve_workspace_path(support_path)
        except ValueError:
            continue
        if os.path.exists(resolved) and support_path not in inferred:
            inferred.append(support_path)

    return inferred


def stage_review_workspace(selected_files: list[str] | None) -> tuple[str, list[str]]:
    staged_dir = tempfile.mkdtemp(prefix="pm_quality_")
    copied_files: list[str] = []

    try:
        for abs_path, rel_path in iter_workspace_files(selected_files):
            destination = os.path.join(staged_dir, rel_path)
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.copy2(abs_path, destination)
            copied_files.append(rel_path)
    except Exception as exc:
        logger.warning("Failed to stage review workspace: %s", exc)
        shutil.rmtree(staged_dir, ignore_errors=True)
        raise

    if not copied_files:
        shutil.rmtree(staged_dir, ignore_errors=True)
        raise FileNotFoundError("No files found for quality review.")

    return staged_dir, copied_files


def build_workspace_snapshot(workspace_root: str) -> dict[str, Any]:
    snapshot = {"files": [], "text": {}}
    for root, dirs, files in os.walk(workspace_root):
        dirs[:] = [directory for directory in dirs if directory not in {"__pycache__", ".git"}]
        for file_name in files:
            rel_path = os.path.relpath(os.path.join(root, file_name), workspace_root)
            snapshot["files"].append(rel_path)

            extension = os.path.splitext(file_name)[1].lower()
            lower_name = file_name.lower()
            if (
                extension in TEXT_FILE_EXTENSIONS
                or lower_name.startswith("readme")
                or lower_name.startswith("license")
            ):
                try:
                    with open(
                        os.path.join(root, file_name), encoding="utf-8", errors="ignore"
                    ) as handle:
                        snapshot["text"][rel_path] = handle.read()
                except Exception as exc:
                    logger.debug("Skipping unreadable workspace file '%s': %s", rel_path, exc)
                    continue

    snapshot["files"].sort()
    return snapshot


def build_snapshot_for_files(selected_files: list[str] | None) -> dict[str, Any]:
    if not selected_files:
        return build_workspace_snapshot(os.fspath(WORKSPACE_DIR))

    staged_dir, _ = stage_review_workspace(selected_files)
    try:
        return build_workspace_snapshot(staged_dir)
    finally:
        shutil.rmtree(staged_dir, ignore_errors=True)


def dedupe_preserve(items: list[str]) -> list[str]:
    return list(dict.fromkeys(item for item in items if item))


def assess_bundle_quality(product_name: str, snapshot: dict[str, Any]) -> dict[str, list[str]]:
    files = snapshot.get("files", [])
    text_files = snapshot.get("text", {})
    issues: list[str] = []
    suggestions: list[str] = []

    source_files = [
        path for path in files if os.path.splitext(path)[1].lower() in SOURCE_FILE_EXTENSIONS
    ]
    readme_files = [path for path in files if os.path.basename(path).lower().startswith("readme")]
    license_files = [
        path
        for path in files
        if os.path.basename(path).lower() in {"license", "license.md", "license.txt"}
    ]
    marketing_files = [path for path in files if os.path.basename(path).lower() == "marketing.md"]

    if not source_files:
        issues.append("Bundle is missing source code or executable product files.")
        suggestions.append("Include the actual product code or app files before packaging.")

    if not readme_files:
        issues.append("Bundle is missing README documentation.")
        suggestions.append("Add a README with setup, usage, and buyer-facing value.")
    else:
        primary_readme = max(
            (text_files.get(path, "") for path in readme_files), key=len, default=""
        )
        if len(primary_readme.strip()) < FACTORY_MIN_README_CHARS:
            issues.append(
                f"README is too thin for a sellable product ({len(primary_readme.strip())} chars; need at least {FACTORY_MIN_README_CHARS})."
            )
            suggestions.append(
                "Expand the README with problem, workflow, setup, and outcome details."
            )

    if not license_files:
        issues.append("Bundle is missing a LICENSE file.")
        suggestions.append("Add a clear license so buyers know their usage rights.")

    total_source_chars = sum(len(text_files.get(path, "")) for path in source_files)
    if source_files and total_source_chars < FACTORY_MIN_SOURCE_CHARS:
        issues.append(
            f"Source footprint is too small to look production-ready ({total_source_chars} chars; need at least {FACTORY_MIN_SOURCE_CHARS})."
        )
        suggestions.append("Expand the implementation beyond a trivial demo before packaging.")

    sales_text = "\n".join(text_files.get(path, "") for path in readme_files + marketing_files)
    if re.search("|".join(LOW_VALUE_PATTERNS), sales_text, re.IGNORECASE):
        issues.append(
            "Documentation or sales copy still reads like a demo/placeholder instead of a sellable product."
        )
        suggestions.append(
            "Rewrite the README/marketing copy so it explains a real outcome, not a demo."
        )

    branded_keyword = os.getenv("BRAND_NAME", "Dre").lower()
    if branded_keyword not in sales_text.lower():
        suggestions.append(
            f"Add the {branded_keyword.capitalize()} Brand Flair to your README and Marketing copy (e.g. 'Powered by the {branded_keyword.capitalize()} Neural Swarm')."
        )

    return {"issues": dedupe_preserve(issues), "suggestions": dedupe_preserve(suggestions)}


def resolve_publish_description(snapshot: dict[str, Any], description: str) -> str:
    text_files = snapshot.get("text", {})
    marketing_candidates = [
        text_files[path]
        for path in snapshot.get("files", [])
        if os.path.basename(path).lower() == "marketing.md" and text_files.get(path, "").strip()
    ]
    if marketing_candidates:
        longest_marketing = max(marketing_candidates, key=len)
        if len(longest_marketing.strip()) >= len((description or "").strip()):
            return longest_marketing.strip()
    return (description or "").strip()


def assess_publish_readiness(
    platform: str, title: str, description: str, snapshot: dict[str, Any]
) -> dict[str, Any]:
    issues: list[str] = []
    suggestions: list[str] = []
    resolved_description = resolve_publish_description(snapshot, description)
    files = snapshot.get("files", [])

    if len((title or "").strip()) < FACTORY_MIN_TITLE_CHARS:
        issues.append(
            f"Title is too short for a strong listing (need at least {FACTORY_MIN_TITLE_CHARS} characters)."
        )
        suggestions.append(
            "Use a clearer, more specific title that communicates the product outcome."
        )

    if re.search("|".join(LOW_VALUE_PATTERNS), title or "", re.IGNORECASE):
        issues.append("Title still looks like a placeholder or demo label.")
        suggestions.append("Rename the product with a real market-facing title.")

    if len(resolved_description.strip()) < FACTORY_MIN_MARKETING_CHARS:
        issues.append(
            f"Listing description is too thin for conversion ({len(resolved_description.strip())} chars; need at least {FACTORY_MIN_MARKETING_CHARS})."
        )
        suggestions.append(
            "Expand the listing copy with problem, promise, deliverables, and buyer outcome."
        )

    if re.search("|".join(LOW_VALUE_PATTERNS), resolved_description, re.IGNORECASE):
        issues.append("Listing description still contains demo or placeholder language.")
        suggestions.append("Replace placeholder wording with concrete benefits and deliverables.")

    if platform == "whop":
        if len((title or "").strip()) > 40:
            issues.append("Whop titles should stay within 40 characters to publish reliably.")
            suggestions.append("Shorten the Whop title while keeping the hook strong.")

        image_assets = [
            path
            for path in files
            if os.path.splitext(path)[1].lower() in IMAGE_FILE_EXTENSIONS
            and ("assets" in path.replace("\\", "/").split("/"))
        ]
        if not image_assets:
            issues.append("Whop publish requires at least one gallery or icon asset under assets/.")
            suggestions.append(
                "Add at least one PNG/JPG/WebP asset to assets/ before publishing to Whop."
            )

    return {
        "issues": dedupe_preserve(issues),
        "suggestions": dedupe_preserve(suggestions),
        "description": resolved_description,
    }
