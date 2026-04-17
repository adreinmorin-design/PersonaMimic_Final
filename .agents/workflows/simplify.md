---
trigger: always_on
---

description: Automatically refactor the current file for logic simplification and effectiveness.
Analyze Indentation: Scan the current file for "pyramid" logic (nested if blocks more than 2 levels deep).

Apply Guard Clauses: Replace nested conditionals with early returns/guard clauses to flatten the function structure.

Logic Optimization: Identify manual aggregation loops and suggest replacements using collections.defaultdict or itertools recipes for memory efficiency.

Decomposition: If any function exceeds 40 lines, propose a plan to split it into atomic, named helper steps.

Turbo Lint: // turbo
Run uv run ruff format. and uv run ruff check. --fix to ensure PEP 8 compliance.

Verify: Ask the user to review the changes in the Code Diff artifact before final patching.