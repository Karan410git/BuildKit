# BuildKit Architecture

## 1. Purpose

BuildKit is a reusable full-stack starter framework for hackathons and rapid software prototyping.

It provides generic infrastructure so teams can spend hackathon time implementing the actual problem statement instead of rebuilding common foundations.

BuildKit must remain domain-agnostic.

---

## 2. Core Stack

### Backend

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* PostgreSQL

### Frontend

* React-based frontend
* TypeScript
* Reusable UI components

### Infrastructure

* Docker
* Docker Compose
* Environment-based configuration

### Tooling

* CLI project generator
* Automated tests
* Developer documentation

---

## 3. High-Level Architecture

BuildKit contains two major concepts:

### A. Reference Application

A manually maintained example application that proves every generic BuildKit capability works correctly.

The reference application is the source of truth before functionality is added to the project generator.

### B. Project Generator

The generator reproduces a validated BuildKit project from templates.

The generator should only generate functionality already proven in the reference application.

Do not build generator functionality before the corresponding reference implementation is stable.

---

## 4. Planned Repository Structure

```text
BuildKit/
├── CLAUDE.md
├── README.md
├── .gitignore
├── docs/
│   ├── ARCHITECTURE.md
│   └── MILESTONES.md
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   └── tests/
│
├── frontend/
│
├── cli/
│
├── templates/
│
└── docker/
```

Directories should only be created when their milestone requires them.

Do not create empty architecture for future work purely for completeness.

---

## 5. Backend Responsibilities

### `app/core`

Cross-cutting application configuration.

Examples:

* settings
* logging
* security configuration

It should not contain business logic.

### `app/api`

HTTP route definitions.

Routes should remain thin and delegate non-trivial logic when necessary.

### `app/db`

Database infrastructure.

Examples:

* engine creation
* sessions
* base model
* database initialization

### `app/models`

SQLAlchemy database models.

The base framework may contain only generic models required by reusable infrastructure.

### `app/schemas`

Pydantic request and response schemas.

### `app/services`

Reusable application logic that does not belong directly inside routes.

Do not create service abstractions unless actual logic requires them.

---

## 6. Frontend Responsibilities

The frontend should provide reusable infrastructure and presentation components.

Allowed examples:

* layout
* navigation
* loading states
* generic forms
* authentication UI
* static chart examples
* static map examples
* generic upload UI

The base frontend must not contain domain-specific dashboards or workflows.

---

## 7. Configuration

Configuration must use environment variables.

Local secrets belong in `.env`.

Only placeholders belong in `.env.example`.

Application code should access configuration through one centralized settings system rather than reading environment variables throughout the codebase.

---

## 8. Logging

Logging should be centralized and reusable.

Initial goals:

* consistent formatting
* configurable log level
* application startup logs
* useful error reporting

Do not introduce external logging infrastructure during the initial framework.

---

## 9. API Foundation

FastAPI should initially provide:

* application creation
* health endpoint
* router registration
* centralized configuration
* basic exception handling

Problem-specific endpoints must not exist in the base framework.

---

## 10. Database

PostgreSQL is the primary database.

SQLAlchemy provides database access.

The framework should include:

* connection configuration
* session management
* declarative base
* migration support when introduced
* generic models only when required

Do not create speculative domain tables.

---

## 11. Authentication

Authentication should be generic and reusable.

Expected capabilities:

* generic user account
* secure password hashing
* login
* authentication token/session
* protected endpoint example

Authentication should not contain organization-specific roles or domain permissions unless added in a later approved milestone.

---

## 12. File Uploads

BuildKit may provide a generic upload capability.

The base implementation may:

* accept a file
* validate basic file properties
* enforce configurable limits
* use safe filenames
* return generic metadata

It must not process uploaded content according to any future problem statement.

---

## 13. Charts

Charts in BuildKit are presentation examples only.

They should use hardcoded or mock data.

No domain-specific analytics API should be pre-built.

---

## 14. Maps

Maps in BuildKit are presentation examples only.

They should use static or mock markers.

No problem-specific geospatial processing should be pre-built.

---

## 15. Docker

Docker should eventually support a consistent local development environment.

Expected services may include:

* backend
* frontend
* PostgreSQL

Docker should be introduced only after the individual services work independently.

---

## 16. CLI

The BuildKit CLI will eventually provide commands such as:

```text
buildkit create <project-name>
```

Potential later commands:

```text
buildkit validate
buildkit info
```

The initial CLI should remain small.

Do not build a large plugin architecture.

---

## 17. Project Generator

The generator should create a project from validated templates.

Core responsibilities:

1. Validate project name and destination.
2. Prevent unsafe overwrites.
3. Copy/render templates.
4. Generate configuration placeholders.
5. Produce a runnable project.
6. Report clear errors.

The generator must not invent domain-specific functionality.

---

## 18. Testing Strategy

Each capability should have focused tests.

Testing layers may include:

* unit tests
* API tests
* database tests
* generator tests
* generated-project validation

The reference application must be validated before its implementation becomes part of the generator templates.

---

## 19. Architectural Constraints

BuildKit should prefer a modular monolith.

Do not introduce:

* microservices
* message brokers
* Kubernetes
* distributed systems
* complex event architectures
* plugin frameworks
* unnecessary repository patterns
* unnecessary abstraction layers

unless a future requirement clearly justifies them.

---

## 20. Extension Philosophy

BuildKit provides extension points, not pre-built solutions.

After a hackathon problem statement is selected, teams may add:

* new database models
* new APIs
* ML models
* external integrations
* dashboards
* domain workflows
* datasets
* domain validation

These additions should happen outside the generic BuildKit foundation.

---

## 21. Primary Architectural Rule

Build the smallest reusable foundation that reliably saves development time during a hackathon.

Do not optimize BuildKit for hypothetical future complexity.

## Modular Generation

BuildKit must support both complete project generation and individual reusable modules.

The goal is to avoid forcing every generated project to include infrastructure it does not need.

### Full Project Generation

BuildKit should support generating a standard complete starter project.

Example:

```bash
buildkit create my-project
```

This may include the default recommended BuildKit stack.

A later interactive flow may allow the user to select which components are included.

---

### Selective Project Generation

BuildKit should support creating a new project with only selected capabilities.

Examples:

```bash
buildkit create my-project --only fastapi
```

```bash
buildkit create my-project --only fastapi,postgres
```

The exact CLI syntax may change during the CLI milestone, but selective generation is a required capability.

---

### Adding Modules to Existing Projects

BuildKit should eventually support adding an individual BuildKit capability to an existing compatible project.

Examples:

```bash
buildkit add logging
buildkit add postgres
buildkit add auth
buildkit add upload
buildkit add charts
buildkit add maps
```

A module must not silently overwrite existing project code.

Before applying a module, BuildKit should:

1. inspect only the files required to determine compatibility
2. detect conflicting files or configuration
3. refuse unsafe overwrites
4. report required dependencies
5. apply only the selected module
6. report exactly what changed

---

### Module Independence

Where practical, BuildKit capabilities should be represented as independently reusable modules.

Examples include:

* config
* logging
* fastapi
* postgres
* migrations
* upload
* authentication
* frontend
* charts
* maps
* docker

Modules may declare dependencies on other BuildKit modules.

For example:

```text
logging -> config

fastapi -> config + logging

postgres -> config

migrations -> postgres

authentication -> fastapi + postgres + migrations

upload -> fastapi
```

BuildKit should automatically resolve required dependencies rather than duplicating their implementation.

---

### Dependency Rules

Module dependencies must remain explicit.

If the user requests:

```bash
buildkit add auth
```

and authentication requires FastAPI, PostgreSQL, migrations, and configuration, BuildKit should determine which prerequisites already exist and add only the missing compatible components.

It must not duplicate modules already present.

---

### Module Manifest

The template/generator system should eventually maintain lightweight metadata describing each module.

A module may define:

* name
* description
* dependencies
* files/templates
* required packages
* configuration variables
* compatibility requirements

Do not build a complex plugin architecture.

The module manifest should remain simple and exist only to support safe composition of BuildKit's own modules.

---

### Primary Modular Design Rule

BuildKit should allow a team to use only the infrastructure required by its project.

The full starter is a convenient combination of modules, not a mandatory architecture.
