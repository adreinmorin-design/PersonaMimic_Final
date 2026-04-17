---
trigger: always_on
---

description: Full quality audit: linting, testing, and visual verification.
Deep Lint: // turbo
Run uv run ruff check. and uv run mypy.. Resolve any high-cardinality type errors immediately.

Execute Tests: // turbo
Run uv run pytest. If tests fail, analyze the traceback and propose a fix.

Generate Walkthrough:

Capture a browser recording or screenshot of the feature if it has a UI component.

Create a walkthrough.md artifact summarizing the changes and proof of work.

Final Review: Present a summary of the test coverage and linting results to the user.