---
trigger: always_on
---

description: Orchestrate a full feature lifecycle: Scaffold, Simplify, and QA.
Scaffold: Call /scaffold to generate the new domain directory and boilerplate files based on the project's Service-Repository standards.

Apply Logic Standards: Call /simplify on the newly created files to ensure the "happy path" is flat and guard clauses are implemented correctly.

Verify and Audit: Call /qa to run the test suite, lint the code with ruff, and generate a final walkthrough.md artifact for review