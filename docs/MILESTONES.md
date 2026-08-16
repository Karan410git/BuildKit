# BuildKit Milestones

BuildKit must be developed incrementally.

Only one milestone should be implemented at a time.

A milestone is complete only when its relevant tests pass.

---

## Phase 0 — Project Governance

### Milestone 0.1 — Repository Setup

Status: Complete

Includes:

* public Git repository
* README
* `.gitignore`

### Milestone 0.2 — Claude Development Rules

Status: Complete

Includes:

* `CLAUDE.md`
* task modes
* exploration discipline
* Git safety
* architecture boundaries

### Milestone 0.3 — Architecture Documentation

Status: Complete after `ARCHITECTURE.md` and this file are committed.

---

# Phase 1 — Backend Foundation

## Milestone 1 — Configuration

Goal:

Create the smallest centralized configuration system for the backend.

Expected scope:

* backend application package foundation
* centralized settings
* `.env.example`
* configuration tests

Must support at minimum:

* application name
* environment
* debug flag
* configurable log level

Do not implement:

* logging system
* database connection
* authentication
* Docker
* uploads

---

## Milestone 2 — Logging

Goal:

Add reusable application logging based on the configuration system.

Expected capabilities:

* configurable log level
* consistent console format
* reusable logger setup

Do not introduce external logging services.

---

## Milestone 3 — FastAPI Foundation

Goal:

Create the minimal runnable FastAPI application.

Expected capabilities:

* application startup
* configuration integration
* logging integration
* `/health` endpoint
* basic API router structure
* focused API tests

Do not implement database or authentication functionality yet.

---

## Milestone 4 — PostgreSQL Foundation

Goal:

Add generic PostgreSQL infrastructure.

Expected capabilities:

* SQLAlchemy configuration
* engine
* sessions
* declarative base
* database configuration
* database tests

No problem-specific models.

---

## Milestone 5 — Database Migrations

Goal:

Introduce a migration system for database schema evolution.

Keep migration configuration minimal.

---


## Milestone 6 — Generic Upload API

Goal:

Provide a reusable file upload foundation.

Expected capabilities:

* receive file
* validate filename/extension where appropriate
* configurable size limit
* safe handling
* generic response

No domain-specific processing.

---

## Milestone 7 — Docker Development Environment

Goal:

Provide a reproducible development environment.

Expected capabilities:

* backend container
* PostgreSQL container
* Docker Compose
* environment configuration

Frontend container may be added after frontend foundations exist.

---

## Milestone 8 — Authentication

Goal:

Add generic authentication.

Expected capabilities:

* generic User model
* password hashing
* registration
* login
* authentication token/session
* protected endpoint
* tests

No domain-specific roles or permissions.

---

# Phase 2 — Frontend Utilities

## Milestone 9 — Frontend Foundation

Goal:

Create the reusable frontend shell.

Expected capabilities:

* TypeScript
* application structure
* API configuration
* generic layout
* basic loading/error handling

---

## Milestone 10 — Static Charts

Goal:

Provide reusable chart components using mock data.

No live analytics API or domain-specific data.

---

## Milestone 11 — Static Maps

Goal:

Provide reusable map components using mock markers.

No problem-specific geospatial logic.

---

## Milestone 12 — Generic Upload UI

Goal:

Provide a simple reusable frontend for the generic upload API.

---

## Milestone 13 — Authentication UI

Goal:

Provide generic login/registration UI integrated with the backend authentication foundation.

---

# Phase 3 — BuildKit Tooling

## Milestone 14 — CLI Foundation

Goal:

Create the BuildKit CLI foundation.

Initial capabilities should support the future command structure for:

```bash
buildkit create <project-name>
buildkit add <module>
```

The initial CLI should remain small.

It must establish a clean command structure without implementing a complex plugin system.

---

## Milestone 15 — Modular Template System

Goal:

Convert proven BuildKit capabilities into independently reusable templates/modules.

Each supported module should define:

* templates/files it owns
* required dependencies
* required configuration
* dependencies on other BuildKit modules

Initial module candidates:

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

Modules must remain composable.

Do not duplicate shared infrastructure between modules.

---

## Milestone 16 — Project Generator

Goal:

Generate complete or selectively composed BuildKit projects.

Required capabilities:

### Full generation

```bash
buildkit create my-project
```

### Selective generation

Support selecting only required BuildKit modules.

Exact CLI syntax may be finalized during implementation.

### Safe composition

The generator must:

* resolve module dependencies
* avoid duplicate modules
* generate configuration placeholders
* prevent unsafe overwrites
* produce a runnable project
* provide clear completion and error output

---

## Milestone 17 — Add Module to Existing Project

Goal:

Allow individual BuildKit modules to be added safely to an existing compatible project.

Target workflow:

```bash
buildkit add <module>
```

Required capabilities:

* identify modules already present
* resolve missing dependencies
* detect conflicts
* prevent silent overwrites
* add only required files/configuration/dependencies
* report exactly what changed

This milestone must remain limited to BuildKit-compatible projects for the first version.

Do not attempt arbitrary framework migration or automatic modification of unrelated codebases.

---

## Milestone 18 — Generated Project Validation

Goal:

Automatically validate generated and composed projects.

Validation should cover:

* full BuildKit projects
* selectively generated projects
* projects where modules were added incrementally
* dependency resolution
* duplicate prevention
* expected files
* configuration loading
* backend imports
* relevant tests

# Phase 4 — Later Enhancements

These are not required for the first usable BuildKit release.

Possible future milestones:

* interactive CLI options
* optional modules
* CI templates
* richer documentation generation
* deployment helpers
* SIH problem-statement adaptation assistant

These must not be implemented unless explicitly approved.

---

# Current Milestone

**Milestone 1 — Configuration**

No later milestone is currently authorized.
