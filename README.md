# pptx-design-md

Turn an existing PowerPoint deck into a reusable design system prompt for AI slide generation.

`pptx-design-md` analyzes a `.pptx` file and produces:
- `design.md` (human- and LLM-readable style guide)
- `analysis.json` (structured extraction output)

This helps teams generate new slides that look consistent with an existing brand/template without manually reverse-engineering every slide.

## Who This Is For
- Founders and operators creating investor update decks fast
- Marketing teams reusing brand style across campaigns
- Consultants/analysts generating client-ready slides with consistent visual language
- Anyone using ChatGPT/Claude to draft slides and needing style consistency

## What You Get
- Canvas and aspect ratio guidance
- Typography hierarchy suggestions (title/body/caption roles)
- Color palette candidates (plus confidence diagnostics)
- Spacing rhythm and alignment anchors
- Recurring layout archetypes and component patterns

## Product Scope (MVP)
- Input: one or many `.pptx` files
- Output: pragmatic design abstraction, not pixel-perfect reconstruction
- Charts/SmartArt/grouped objects: treated as visual blocks where needed

## Quick Start (Local)

### 1) Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2) Frontend
```bash
cd frontend
python3 -m http.server 4173
```

Open: `http://127.0.0.1:4173`

Default API target is `http://127.0.0.1:8000`.

## API
- `GET /health`
- `POST /extract` (multipart field: `file`)
- `POST /extract/batch` (multipart repeated field: `files`)
- `POST /design/save` (save edited markdown by `run_id`)

## CLI

Single file:
```bash
cd backend
python -m app.cli ../examples/sample1.pptx --output ../examples/sample1.generated.design.md --json ../examples/sample1.generated.analysis.json --persist-run
```

Batch:
```bash
cd backend
python -m app.cli --batch-dir ../examples --output-dir ../examples/out --persist-run
```

## Deployment

### Backend (Render/Railway)
- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Recommended env vars:
- `PPTX_ALLOWED_ORIGINS=https://YOUR_FRONTEND_DOMAIN`
- `PPTX_MAX_UPLOAD_BYTES=20971520`
- `PPTX_MAX_BATCH_FILES=10`

### Frontend (Vercel/static host)
- Deploy `frontend/` as static files
- Point frontend to backend by setting `window.API_BASE_URL` before loading `app.js`, or by editing the default in `frontend/app.js`

## Quality & Testing
```bash
cd backend
source .venv/bin/activate
pytest -q
```

Current backend test coverage target is exceeded (85%+).

## Known Limitations
- Theme inheritance is partial in some decks
- SmartArt/chart semantics are approximate
- Some master-level font/color defaults may not fully resolve
- Output is guidance-oriented, not a full PPT reconstruction
