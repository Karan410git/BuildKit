# BuildKit

**A reusable full-stack starter framework for hackathons and rapid software prototyping.**

BuildKit is being developed to reduce the time teams spend rebuilding common software infrastructure during hackathons.

Instead of spending the first several hours setting up a backend, database, authentication, configuration, logging, Docker, charts, maps, and other common components, BuildKit aims to provide a tested generic foundation so teams can focus on the actual problem statement.

> **Build the infrastructure once. Spend the hackathon building the solution.**

---

## The Idea

During a hackathon, many software projects begin with the same repetitive work:

* Setting up the backend
* Configuring environment variables
* Connecting a database
* Creating authentication
* Setting up logging
* Creating a frontend structure
* Adding file uploads
* Configuring charts and maps
* Setting up Docker
* Writing basic project configuration

Most of this work is not unique to the problem being solved.

BuildKit aims to make this reusable.

The eventual workflow will look something like:

```bash
buildkit create my-project
```

BuildKit will generate a ready-to-develop project containing the selected generic infrastructure.

The team can then immediately begin implementing the functionality specific to their hackathon problem statement.

---

## Core Principle

BuildKit is **domain-agnostic**.

It provides infrastructure, not pre-built hackathon solutions.

### BuildKit can provide

* Project configuration
* Logging
* FastAPI backend
* PostgreSQL integration
* Database migrations
* Authentication
* Generic file uploads
* Frontend foundation
* Static/mock charts
* Static/mock maps
* Docker development environment
* CLI project generation
* Testing infrastructure

### BuildKit deliberately does NOT provide

* Problem-specific database schemas
* Problem-specific APIs
* Pre-built ML models for a problem
* Domain datasets
* Domain-specific dashboards
* Government/problem-specific workflows
* Pre-built business logic

Those components are meant to be created **after the actual problem statement is selected**.

---

## Planned Architecture

```text
                    BuildKit CLI
                         │
                         ▼
                  Project Generator
                         │
                         ▼
              ┌─────────────────────┐
              │ Generated Project   │
              └─────────┬───────────┘
                        │
          ┌─────────────┴─────────────┐
          ▼                           ▼
      Frontend                     Backend
                                  FastAPI
                                     │
                          ┌──────────┼──────────┐
                          ▼          ▼          ▼
                       Config     Logging   PostgreSQL
                                     │
                               Generic APIs
```

The reference implementation is built and tested first.

Only proven components will later become generator templates.

---

## Development Progress

### Foundation

* [x] Repository architecture and development rules
* [x] Centralized configuration
* [x] Reusable logging
* [x] FastAPI foundation
* [x] Health API
* [x] PostgreSQL foundation

### Backend Infrastructure

* [ ] Database migrations
* [ ] Generic file upload API
* [ ] Docker development environment
* [ ] Authentication

### Frontend

* [ ] Frontend foundation
* [ ] Static chart components
* [ ] Static map components
* [ ] Generic upload UI
* [ ] Authentication UI

### BuildKit Tooling

* [ ] CLI
* [ ] Template system
* [ ] Project generator
* [ ] Generated-project validation

---

## Current Backend

The current BuildKit backend includes:

```text
backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── health.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   │
│   ├── db/
│   │   └── database.py
│   │
│   └── main.py
│
└── tests/
```

The backend currently provides centralized environment configuration, reusable console logging, a minimal FastAPI application, a health endpoint, and the initial SQLAlchemy/PostgreSQL infrastructure.

---

## Configuration

BuildKit uses environment-based configuration.

Example:

```env
APP_NAME=BuildKit
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/buildkit
```

Real credentials and secrets should never be committed.

Use `.env.example` as the configuration reference and create a local `.env` when required.

---

## Running the Backend

Create and activate a virtual environment.

### Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r backend\requirements-dev.txt
```

Start the backend:

```powershell
cd backend
uvicorn app.main:app --reload
```

The API will then be available locally.

Health check:

```text
GET /health
```

Expected response:

```json
{
  "status": "ok"
}
```

---

## Running Tests

From the `backend` directory:

```powershell
pytest
```

Individual infrastructure areas can also be tested separately:

```powershell
pytest tests/test_config.py
pytest tests/test_logging.py
pytest tests/test_main.py
pytest tests/test_database.py
```

---

## Development Philosophy

BuildKit follows a few important rules:

**Keep it simple.**
This is a hackathon accelerator, not an enterprise platform.

**Build incrementally.**
Every capability is implemented and tested before becoming part of the generator.

**Avoid premature abstraction.**
No unnecessary microservices, plugin architectures, message brokers, or complex infrastructure.

**Stay domain-agnostic.**
BuildKit provides extension points. The actual solution is built during the hackathon.

**Test before templating.**
The reference implementation is validated before it becomes part of generated projects.

---

## Planned BuildKit Experience

The long-term goal is a workflow similar to:

```bash
buildkit create my-project
```

Potential interactive setup:

```text
Creating project: my-project

Select components:

[✓] FastAPI Backend
[✓] PostgreSQL
[✓] Authentication
[✓] File Uploads
[✓] Charts
[✓] Maps
[✓] Docker

Generating project...

✓ Backend created
✓ Frontend created
✓ Database configured
✓ Authentication configured
✓ Environment template created
✓ Docker configured

Project ready.
```

The generated application will then act as the starting point for the actual hackathon solution.

---

## Why BuildKit?

Hackathon time should be spent answering questions like:

> How do we solve this problem?

not:

> How do we configure FastAPI again?

BuildKit is an attempt to move repetitive engineering work **before the hackathon**, while keeping the actual problem-specific innovation for the event itself.

---

## Status

**BuildKit is currently under active development.**

The current repository is the reference implementation used to build, test, and validate each reusable component before the CLI and project generator are created.

It is not yet a finished project generator.
