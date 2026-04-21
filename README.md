# pptx-design-md

`pptx-design-md` is a production-oriented MVP that extracts a PowerPoint deck's visual system and generates a `design.md` file for LLM-guided slide generation.

## What It Does
- Accepts a `.pptx` file via API, CLI, or minimal web UI.
- Supports batch `.pptx` extraction via API/CLI.
- Parses slide geometry and shape/text blocks with `python-pptx`.
- Extracts reusable design tokens and recurring patterns:
  - canvas size and aspect ratio
  - colors, fonts, font sizes
  - text element roles (heuristic)
  - layout archetypes
  - spacing rhythm and alignments
  - repeating component signatures
  - extraction confidence diagnostics
- Produces:
  - `design.md` (LLM-friendly guidance)
  - optional `analysis.json` structured output
  - persisted run artifacts under `backend/runs/<run_id>/`

## Scope and Limitations
This MVP intentionally favors robust heuristics over full PPT reverse engineering.

Known limitations:
- Theme inheritance is partial; inherited defaults may be missing.
- Grouped objects are not fully flattened.
- Charts are handled as `chart_like` blocks, not semantic chart specs.
- SmartArt is treated approximately as visual blocks.
- Font/color values inherited from masters/themes may not always resolve perfectly.

## Repository Structure
```text
pptx-design-md/
├─ backend/
│  ├─ app/
│  │  ├─ __init__.py
│  │  ├─ main.py
│  │  ├─ extractor.py
│  │  ├─ design_md.py
│  │  ├─ heuristics.py
│  │  ├─ models.py
│  │  ├─ cli.py
│  │  └─ utils.py
│  ├─ tests/
│  │  ├─ conftest.py
│  │  ├─ test_design_md.py
│  │  ├─ test_extractor.py
│  │  └─ test_api.py
│  ├─ requirements.txt
│  └─ pyproject.toml
├─ frontend/
│  ├─ index.html
│  ├─ app.js
│  └─ styles.css
├─ examples/
│  ├─ README.md
│  └─ sample-output.design.md
├─ .gitignore
├─ README.md
└─ AGENTS.md
```

## Local Setup
### 1) Backend setup
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Run backend
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

API endpoints:
- `GET /health`
- `POST /extract` (multipart `file=.pptx`)
- `POST /extract/batch` (multipart repeated `files=.pptx`)
- `POST /design/save` (save edited markdown for a prior run)

Security-related environment variables:
- `PPTX_ALLOWED_ORIGINS` (comma-separated CORS allowlist; default local frontend origins only)
- `PPTX_MAX_UPLOAD_BYTES` (default `20971520`, i.e. 20MB per file)
- `PPTX_MAX_BATCH_FILES` (default `10`)

### 3) Run frontend
Serve `frontend/` with any static server, e.g.:
```bash
cd frontend
python3 -m http.server 4173
```
Then open `http://127.0.0.1:4173`.

By default frontend calls `http://127.0.0.1:8000`.
Frontend supports single/batch upload, inline `design.md` editing, and save-back to persisted run storage.

## CLI Usage
```bash
cd backend
python -m app.cli ../examples/sample.pptx --output ../design.md --json ../analysis.json
```

Batch mode:
```bash
cd backend
python -m app.cli --batch-dir ../examples --output-dir ../examples/out --persist-run
```

## Tests
```bash
cd backend
pytest -q
```

Included tests:
- markdown generation from mocked analysis
- extraction smoke test from generated PPTX
- API smoke test (`/health`, `/extract`)

## Heuristics Implemented
- Typography role inference (`title`, `subtitle`, `section header`, `body`, `caption/footnote`) using size distribution and position hints.
- Ranked color palette from text/fill/line colors with weighting and role bucketing (neutrals/primary/accents).
- Theme-aware font/color fallback from slide master theme where available.
- Recursive group-shape traversal (group contents contribute to analysis).
- Layout archetype inference from per-slide shape distribution (`cover`, `section divider`, `title + two-column`, `image + text`, `metrics/cards`, `title + body`).
- Spacing rhythm clustering for margins, offsets, vertical/column gaps, and alignment anchors.
- Component candidates from repeated type/size signatures across slides.
- Pattern diagnostics with score breakdown and evidence counts.

## Deployment Notes
### Frontend on Vercel + backend elsewhere
- Deploy `frontend/` as static site on Vercel.
- Point frontend API base to your deployed backend domain.
- Ensure CORS is allowed on backend.

### Backend on Railway/Render/etc.
- Deploy `backend/` as Python service.
- Install `requirements.txt`.
- Start command example:
  - `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
