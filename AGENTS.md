# AGENTS.md

## Scope
This file governs the entire repository.

## Conventions
- Keep implementation simple and readable; avoid unnecessary dependencies.
- Prefer typed Python and focused functions in `backend/app`.
- Run tests from `backend/` with `pytest` before finalizing changes.
- Keep frontend static and minimal unless feature scope changes.

## Common Commands
- Install: `cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- Run API: `cd backend && uvicorn app.main:app --reload --port 8000`
- Run tests: `cd backend && pytest -q`
- CLI: `cd backend && python -m app.cli ../examples/sample.pptx --output ../examples/generated.design.md --json ../examples/generated.analysis.json`
