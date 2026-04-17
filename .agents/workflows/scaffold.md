---
trigger: always_on
---

description: Scaffolds a new feature module using the Service-Repository pattern.
Get Feature Name: Ask the user for the name of the new domain (e.g., "billing", "notifications").

Create Directory Structure: Create a new folder under src/app/[feature_name]/.

Generate Boilerplate:

Create models.py: Define the SQLAlchemy/Tortoise ORM models.

Create schemas.py: Define Pydantic V2 schemas for request/response validation.

Create repository.py: Add a Repository class for pure database access.

Create service.py: Add a Service class for business logic and orchestration.

Create router.py: Add FastAPI route handlers that call the Service layer.

Register Domain: Update src/app/main.py to include the new router.

Test Template: Create a mirrored test file in tests/[feature_name]/test_service.py.