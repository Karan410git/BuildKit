# BuildKit

BuildKit is a reusable, domain-agnostic full-stack starter for hackathons and rapid prototypes. It generates only the generic infrastructure a project needs so teams can spend their time on the actual problem statement.

BuildKit provides infrastructure—not pre-built domain solutions. Generated projects contain no healthcare, agriculture, government, analytics, ML, or other problem-specific behavior unless a team adds it afterward.

## What BuildKit provides

Every project starts with the default foundation:

- Centralized configuration
- Reusable logging
- FastAPI with a health route
- React, TypeScript, Vite, routing, and a shared API client

Selectable modules:

- `auth` — registration, login, JWT authentication, profile UI, PostgreSQL, and migrations
- `upload` — generic validated upload API and single-file UI
- `charts` — reusable static charts with mock data
- `maps` — reusable maps with mock markers

BuildKit resolves required foundation modules automatically. It never silently adds unrelated selectable features.

## CLI

List available modules:

```bash
buildkit modules
```

Create the default starter or select modules:

```bash
buildkit create my-project
buildkit create my-project --modules auth charts maps
```

From the root of a generated project, add or remove modules:

```bash
buildkit add auth
buildkit add charts maps
buildkit remove maps
buildkit remove auth charts
```

Removing a feature also removes transitive foundations that are no longer needed. The permanent default foundation—`config`, `logging`, `fastapi`, and `frontend`—is retained.

## Safe module management

Generated projects contain `.buildkit/project.json`. It records explicit selections, fully resolved modules, and the owner and SHA-256 hash of every managed file.

Add/remove operations are deterministic and idempotent. BuildKit refuses to overwrite an unowned path or overwrite/delete a managed file whose content no longer matches its recorded hash. There is intentionally no force-removal option in V1.

Controlled routes, navigation, dependencies, and configuration are regenerated from the complete module selection rather than regex-edited. Generated projects contain `.env.example` placeholders, never a real `.env`. Replace development placeholders locally and never commit real secrets.

## Reference application and generated projects

This repository contains two distinct layers:

1. The reference application in `backend/` and `frontend/`, where reusable capabilities are implemented and validated.
2. Explicit assets in `templates/`, which the CLI composes into standalone generated projects.

BuildKit does not copy this repository wholesale. A generated project contains only the selected modules, their dependencies, and generator-controlled integration files.

## Hackathon workflow

1. Receive and understand the problem statement.
2. Choose the reusable modules the solution needs.
3. Generate the starter with BuildKit.
4. Implement problem-specific models, APIs, workflows, data, and UI separately.
5. Add or remove generic modules if requirements change.

## Development setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements-dev.txt
pip install -e .
```

Run the reference backend and tests:

```powershell
cd backend
uvicorn app.main:app --reload

# From the repository root:
python -m pytest backend/tests
python -m pytest cli/tests
```

Reference frontend validation:

```powershell
cd frontend
npm run build
```

## V1 boundaries

- Module selection is command-line based; there is no interactive wizard.
- Modules are BuildKit’s validated internal modules, not third-party plugins.
- Docker is represented as a foundation template and statically validated; Docker execution is not required by tests.
- Generated dependencies are declared but are not installed automatically.
- Module management requires a valid `.buildkit/project.json` in the current directory.
