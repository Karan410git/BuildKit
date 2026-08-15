# BuildKit — Claude Code Instructions

## 1. Project Purpose

BuildKit is a reusable full-stack starter framework for hackathons and rapid software prototyping.

Its purpose is to provide generic infrastructure that can be reused across projects while leaving problem-specific functionality to be implemented after the actual problem statement is known.

BuildKit must remain domain-agnostic.

Do not introduce problem-specific models, APIs, datasets, workflows, ML pipelines, dashboards, or business logic into the base framework.

---

## 2. Core Development Principle

Make the smallest correct change required for the current task.

Do not:

* implement future milestones
* refactor unrelated working code
* rename files, classes, functions, or directories without necessity
* introduce abstractions for hypothetical future requirements
* add dependencies unless the current milestone requires them
* redesign architecture while implementing a small task
* modify unrelated files because they could be "improved"
* perform repository-wide exploration for small tasks

Every changed line should be explainable by the current approved milestone.

---

## 3. Task Modes

Every development request should operate in one of three modes.

### TINY

Used for:

* small bug fixes
* one-file changes
* configuration adjustments
* minor test fixes

Rules:

* Inspect the named file first.
* Inspect directly related dependencies only when necessary.
* Do not explore the entire repository.
* Prefer modifying the minimum number of files.
* Do not refactor surrounding code.

### MILESTONE

Used when implementing one approved BuildKit capability.

Examples:

* configuration
* logging
* FastAPI foundation
* PostgreSQL integration
* authentication

Rules:

1. Read the relevant architecture/milestone documentation.
2. Inspect only files related to the milestone.
3. State the expected files to modify before coding.
4. Implement only the approved milestone.
5. Add or update relevant tests.
6. Run the narrowest relevant tests first.
7. Do not begin the next milestone.

### AUDIT

Used only when explicitly requested.

Repository-wide inspection is allowed.

Rules:

* Do not modify files unless explicitly instructed.
* Report findings before proposing changes.
* Separate confirmed problems from optional improvements.

If no mode is specified, treat a clearly scoped implementation request as MILESTONE and a small fix as TINY.

Do not automatically treat requests as AUDIT.

---

## 4. Architecture Authority

`docs/ARCHITECTURE.md` is the architectural source of truth.

Do not redesign documented architecture during implementation.

If a requested change conflicts with the architecture:

1. Stop before implementing the conflicting portion.
2. Explain the conflict briefly.
3. Ask for approval before changing architectural decisions.

Do not silently alter architecture.

---

## 5. Milestone Authority

`docs/MILESTONES.md` defines the intended implementation sequence.

Only implement the currently approved milestone.

Future milestones may be considered for compatibility, but must not be implemented early.

---

## 6. Exploration Discipline

Repository exploration consumes time and context.

Before searching broadly, ask whether the information is actually required to complete the current task.

For TINY tasks:

* begin with explicitly referenced files
* follow imports/dependencies only when required
* avoid directory-wide reading

For MILESTONE tasks:

* inspect architecture documentation
* inspect the relevant module
* inspect relevant tests
* expand exploration only when necessary

Do not repeatedly reread large files during the same task unless they changed or specific information is needed.

---

## 7. Implementation Discipline

Prefer:

* simple code
* explicit behavior
* existing project patterns
* small functions
* clear interfaces
* minimal dependencies

Avoid:

* premature abstraction
* unnecessary factories
* unnecessary inheritance
* unnecessary repository/service layers
* microservices
* plugin systems before they are required
* speculative extensibility
* duplicated implementations

BuildKit should remain understandable during a time-constrained hackathon.

---

## 8. Testing Discipline

Tests are part of the milestone.

Use this order where applicable:

1. Run tests directly related to changed code.
2. Fix failures caused by the milestone.
3. Run the broader relevant test group.
4. Run the full suite only when appropriate.

Do not repeatedly run the entire test suite after trivial edits when a focused test can validate the change.

Never modify a test merely to hide a legitimate implementation failure.

---

## 9. Dependency Discipline

Before adding a dependency:

1. Confirm the standard library or an existing dependency cannot reasonably solve the requirement.
2. Confirm the dependency is required by the current milestone.
3. Prefer mature, commonly used libraries.

Do not install packages for future milestones.

---

## 10. Security

Never commit:

* API keys
* passwords
* access tokens
* database credentials
* private certificates
* `.env` files containing secrets

Use `.env.example` for documented configuration placeholders.

File uploads, authentication, database access, and generated projects must use safe defaults.

---

## 11. Git Safety

Do not:

* commit unless explicitly instructed
* push unless explicitly instructed
* force push
* rewrite history
* delete branches
* modify `.git`
* perform destructive Git operations

Before a requested commit, report the files changed and relevant test results.

---

## 12. Completion Report

Keep completion reports concise.

Report:

* what changed
* files changed
* tests run and their result
* blockers or important decisions, if any

Do not provide a long walkthrough unless requested.

Do not suggest implementing the next milestone unless asked.

---

## 13. BuildKit Boundary

Generic infrastructure is allowed.

Examples:

* configuration
* logging
* FastAPI setup
* PostgreSQL integration
* authentication foundation
* generic file uploads
* static chart components
* static map components
* Docker
* CLI/project generation
* testing infrastructure

Problem-specific functionality is not part of the base framework.

Examples that must NOT be pre-built:

* healthcare schemas
* crop prediction systems
* traffic analytics
* sports assessment models
* disaster prediction models
* government-specific workflows
* problem-specific ML inference
* problem-specific database tables
* problem-specific dashboards

Such functionality must only be created after a problem statement explicitly requires it.

---

## 14. Primary Rule

When uncertain between a larger solution and a smaller solution that fully satisfies the approved milestone, choose the smaller solution.

Correctness, clarity, and reliability are more important than the amount of code produced.

Once scope, required files, and implementation approach are clear, proceed directly. Do not spend extended reasoning time restating documentation or reconfirming already established repository facts.