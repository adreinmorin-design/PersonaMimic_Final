# Industrial App Building: Best Practices

## 🏗️ Architecture: Atomic & Modular
- **Vite/React**: Follow Atomic Design (Atoms, Molecules, Organisms).
- **Styling**: Always use Vanilla CSS with a global `index.css` for design system tokens (Colors, Spacing, Typography). Use CSS Variables for everything.
- **FastAPI**: One file per concern. `database.py` (models), `assistant_tools.py` (logic), `main.py` (routes).

## 🛡️ Security: Iron Shell
- **Pydantic**: Never accept raw dictionaries for tool arguments. Always define a `BaseModel`.
- **Validation**: catch `ValidationError` and convert it into a technical fix-it plan for the LLM.

## ⚡ Performance: Semantic Recall
- **Caching**: Use FAISS for sub-second recall of tool outcomes.
- **Async**: Use the `TaskQueue` for long-running building tasks.

## 🧩 Autonomous Workflow
1. **Design**: Write a `spec.md` first. Explain the logic.
2. **Review**: Solution Architect brain must peer-review the spec.
3. **Execute**: Code the atomic components first, then the pages.
4. **Audit**: Run `validate_product` after every major component.
