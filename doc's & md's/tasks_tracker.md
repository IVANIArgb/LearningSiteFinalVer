# Backend Tasks Tracker

Project: Flask Backend for Existing Frontend

Legend: [ ] pending, [x] done, [-] blocked, [~] in progress

## Milestones

1. Foundations
   - [x] Create Flask project structure (`backend/`, `backend/app.py`, `backend/__init__.py`, `backend/wsgi.py`)
   - [x] Configure logging with rotating file handler (`backend/logs/`)
   - [x] Add healthcheck endpoint `/healthz`

2. Static Routing for Existing Frontend
   - [x] Root redirect `/ -> /main-pg/`
   - [x] Trailing slash redirects `/<page> -> /<page>/`
   - [x] Serve `index.html` per page `/<page>/`
   - [x] Serve page assets `/<page>/<path>`

3. Error Handling & Diagnostics
   - [x] 404 handler (HTML/JSON)
   - [x] 500 handler with traceback (in TESTING)
   - [x] Request-aware logging format

4. Automated Tests
   - [x] Set up `unittest`
   - [x] Tests for redirects and asset serving
   - [x] Tests for error handlers (404/500)

5. Ops & Docs
   - [x] Requirements file (`backend/requirements.txt`)
   - [x] README with run/test instructions
   - [x] Task tracker document (`tasks_tracker.md`)
   - [x] Bug analysis template (`docs/BUG_REPORT_5_WHYS.md`)

6. Deployment
   - [x] WSGI guidance for Gunicorn/uWSGI
   - [ ] Production config example (env vars)

## Task Details

### Foundations
- Create minimal Flask app factory with logging and error handlers.

### Static Routing
- Map exactly to existing frontend directories without modifying frontend files.

### Error Handling
- JSON vs HTML based on `Accept` header.

### Testing
- Use Flask test client to verify routes and assets.

### Deployment
- Provide Gunicorn/uWSGI examples and Windows note for `waitress` (optional).

## How to use this tracker

- Mark tasks as completed by changing `[ ]` to `[x]`.
- If blocked, use `[-]` and note the blocker below.
- Use `[~]` for in-progress tasks.

## Blockers

- None at the moment.

## Changelog

- v1: Initial backend skeleton, routing, tests, diagnostics.

# Backend Task Tracker

This document tracks the backend implementation work for the existing frontend. Update the status checkbox as work progresses. Add dates, owners, and notes as needed.

## Legend
- [ ] = not started
- [~] = in progress
- [x] = completed

## Tasks and Subtasks

1. Project Setup
   - [x] Create Flask app factory in `backend/__init__.py`
   - [x] Configuration classes in `backend/config.py`
   - [x] Logging setup with rotating files
   - [x] Error handlers in `backend/errors.py`
   - [x] Utilities for request correlation IDs
   - [x] Local run entry points (`run.py`, `backend/wsgi.py`)

2. Routes and Static Serving
   - [x] Map existing frontend directories to routes
   - [x] Root redirect to main page
   - [x] Serve per-page `index.html`
   - [x] Serve static assets under each page directory
   - [x] Compatibility redirects for `*-pg` paths

3. Testing
   - [x] Add unittest test suite in `tests/`
   - [ ] Expand tests for all known pages and sample assets
   - [ ] Add negative tests for path traversal prevention

4. Quality and Diagnostics
   - [x] Structured JSON error responses with `request_id`
   - [x] Exception logging
   - [ ] Add access logging middleware (optional)
   - [ ] Add environment-specific configuration docs

5. CI and Automation (optional)
   - [ ] Add GitHub Actions workflow for tests
   - [ ] Add code style checks (flake8/black) without enforcing third-party runtime deps

6. Deployment
   - [ ] Document production run commands (Gunicorn/Waitress/Uvicorn + WSGI)
   - [ ] Configure environment variables (`SECRET_KEY`, `LOG_LEVEL`)
   - [ ] Containerize (optional)

7. Bug Management
   - [x] Add 5 Whys bug analysis template
   - [ ] For each bug, document root cause and corrective action

## How to Use This Tracker
1. Update each item as you work: change `[ ]` to `[~]` when started, `[x]` when done.
2. Add new tasks as they arise. Keep tasks small and actionable.
3. For bugs, copy the template from `docs/BUG_REPORT_5_WHYS.md` and fill it in per issue.

# Backend Task Tracker

Status legend: [ ] not started, [~] in progress, [x] done

## Milestones

- [~] M1: Backend project scaffold
  - [x] Create Flask app factory and routing to frontend pages
  - [x] Error handlers and JSON logging
  - [x] Basic configuration
- [~] M2: Testing and QA
  - [x] Unit tests for core routes
  - [ ] Add negative tests and edge cases
  - [ ] Test logs and error responses
- [ ] M3: Observability and diagnostics
  - [ ] Enrich structured logs with request IDs
  - [ ] Add request timing metrics (middleware)
- [ ] M4: Deployment readiness
  - [ ] Production WSGI entrypoint (gunicorn/uwsgi) docs
  - [ ] Environment configuration instructions
- [ ] M5: Documentation
  - [x] How to run and test locally
  - [x] Bug analysis template (5 Whys)
  - [ ] Maintenance guide

## Tasks

- [x] Implement `backend/app.py` with routes:
  - `/` redirect to `/main-pg/`
  - `/<page>/` serve that page's `index.html`
  - `/<page>/<path>` serve static file within page dir
- [x] Implement error handling in `backend/errors.py`
- [x] Implement JSON logging in `backend/utils/logging_config.py`
- [x] Tests in `backend/tests/test_app.py`
- [x] Provide run/test instructions in `README-backend.md`
- [x] Provide bug analysis template in `bug_analysis_template.md`
- [ ] Add request ID middleware and include in logs
- [ ] Expand test coverage to 90%+
- [ ] CI-ready test command (documented)

## How to use this tracker

- Update the markers [ ], [~], [x] as you progress.
- Add new tasks under appropriate milestone.
- Keep items atomic and verifiable.


