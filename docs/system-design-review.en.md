# pptx-design-md System Design Review (English)

## 1. System Overview
`pptx-design-md` is a split frontend/backend system that converts a `.pptx` deck into:
- `design.md` (LLM-facing design guidance)
- `analysis.json` (structured extraction output)

Primary user flow:
1. User uploads one or more `.pptx` files in web UI or CLI.
2. Backend validates file type/content and size constraints.
3. Extraction pipeline parses slides/shapes and computes heuristics.
4. Backend returns analysis + generated markdown.
5. Optional persistence saves run artifacts (`design.md`, `analysis.json`, metadata) under `backend/runs/<run_id>/`.

---

## 2. Architecture

### 2.1 High-level components
- Frontend (static): `frontend/index.html`, `frontend/app.js`, `frontend/styles.css`
- Backend API (FastAPI): `backend/app/main.py`
- Parsing + heuristics engine:
  - Parsing: `backend/app/extractor.py` (python-pptx)
  - Heuristics: `backend/app/heuristics.py`
  - Markdown synthesis: `backend/app/design_md.py`
- Data model contracts: `backend/app/models.py`
- Run storage: `backend/app/storage.py`
- CLI entry: `backend/app/cli.py`

### 2.2 Request path
1. `POST /extract` or `POST /extract/batch`
2. `_read_validated_pptx_upload` enforces:
   - extension check
   - content-type check
   - max upload size
   - ZIP signature check (`PK`)
3. file bytes written to temp `.pptx`
4. `extract_pptx(...)` builds `DeckAnalysis`
5. `generate_design_md(...)` produces LLM-facing text
6. `save_run(...)` persists artifacts and returns `run_id`

### 2.3 Persistence model
- Storage is filesystem-based for MVP simplicity.
- Directory-per-run pattern:
  - `design.md`
  - `analysis.json`
  - `meta.json`
  - optional `design.edited.md`

This intentionally avoids introducing DB infrastructure at MVP stage.

---

## 3. Data Structure Choices and Tradeoffs

### 3.1 Pydantic models for API and analysis schema
**Chosen:** nested Pydantic models (`DeckAnalysis`, `SlideAnalysis`, `ElementAnalysis`, etc.)

**Why this choice:**
- Strong shape guarantees for API responses.
- Clear contract between extractor, markdown generator, and frontend.
- Easier evolution than loose dicts; validation catches schema drift early.

**Alternatives:**
1. Plain dictionaries
   - Pros: minimal overhead, fastest to prototype
   - Cons: weak type safety, brittle refactors, inconsistent keys
2. Dataclasses only
   - Pros: lightweight, explicit fields
   - Cons: weaker runtime validation for API serialization than Pydantic

---

### 3.2 `list` for slides/elements; `Counter` for ranking
**Chosen:**
- `list` for ordered structures (`slides`, `elements`)
- `Counter` for ranked frequencies (fonts, colors, component signatures)

**Why this choice:**
- Slide order matters semantically and for UX.
- Elements are naturally iterable in sequence for layout heuristics.
- Frequency ranking is central to “dominant style” inference; `Counter` is concise and efficient for MVP scale.

**Alternatives:**
1. NumPy arrays / DataFrame-based pipeline
   - Pros: vectorized stats and clustering possibilities
   - Cons: heavier dependency/complexity; overkill for current scale
2. Tree-based index structure per slide
   - Pros: faster geometric queries
   - Cons: complexity increase with marginal benefit at current deck sizes

---

### 3.3 Bounding box as dual-unit representation (`inches` + `%`)
**Chosen:** each element stores absolute inches and relative percentages.

**Why this choice:**
- Inches preserve original PPT coordinate fidelity.
- Percentages generalize composition patterns across different slide dimensions.
- Supports both deterministic diagnostics and style guidance in markdown.

**Alternatives:**
1. Absolute only (inches)
   - Pros: simpler calculations
   - Cons: weak transferability across aspect/size changes
2. Percentage only
   - Pros: easier normalization
   - Cons: loses exact numeric references useful for debugging and expert users

---

### 3.4 Heuristic buckets via clustered float values
**Chosen:** tolerance-based clustering for margins/gaps/anchors.

**Why this choice:**
- Robust to small positional noise from manual edits in decks.
- Interpretable output for human + LLM consumers.
- Avoids heavy ML/clustering dependencies.

**Alternatives:**
1. K-means clustering
   - Pros: formalized centroid extraction
   - Cons: parameter tuning and less interpretability for non-ML users
2. Raw histogram bins
   - Pros: very simple
   - Cons: brittle boundaries; less stable semantic anchors

---

### 3.5 Filesystem run storage instead of database
**Chosen:** local directory storage under `backend/runs/`.

**Why this choice:**
- Fastest path to production MVP.
- Easy to inspect/debug artifacts manually.
- No DB ops burden during early iteration.

**Alternatives:**
1. Relational DB + object storage
   - Pros: better queryability, multi-tenant scaling
   - Cons: significantly more setup, schema lifecycle burden
2. Redis cache only
   - Pros: fast retrieval
   - Cons: volatile and not ideal for long-lived artifact retention

---

## 4. Architectural Tradeoffs

### 4.1 Strengths
- Clear module boundaries: API / extraction / heuristics / synthesis / storage.
- Good safety baseline for file uploads (size/type/signature checks).
- Deterministic, explainable heuristics (better auditability than opaque ML).
- Coverage-backed backend with strong regression tests.

### 4.2 Current limitations
- Single-process extraction workload; CPU-bound parsing can bottleneck under concurrent uploads.
- Local filesystem persistence is not ideal for multi-instance deployments.
- Heuristics can underfit complex decks (theme inheritance, SmartArt semantics, nested groups).
- Error granularity is intentionally sanitized for security, reducing debug detail at API edge.

### 4.3 Why this is acceptable for MVP
- Product goal prioritizes reliable abstraction over full PPT fidelity.
- Controlled complexity enables faster iteration and easier debugging.
- Design provides clear migration paths without rewriting core contracts.

---

## 5. Future-ready Extension Points
1. Async job queue for extraction (Celery/RQ + worker pool).
2. Replace local run storage with S3-compatible object store + metadata DB.
3. Add feature flags for alternative heuristic strategies.
4. Introduce optional “explainability blocks” per inferred rule (evidence snippets).
5. Add per-slide visual thumbnails and layout overlays for human QA.

---

## 6. Deep Dive Question Prep (with Answer Direction)

### Q1. Why not use ML for role/layout inference?
**Answer direction:**
- MVP needs deterministic and explainable behavior.
- Heuristics are auditable, low-latency, and dependency-light.
- ML can be layered later as optional scoring enhancer.

### Q2. How does the design avoid schema drift?
**Answer direction:**
- Pydantic model contracts centralize schema.
- Shared model usage across API, extractor, and markdown generation.
- Tests validate serialization paths.

### Q3. What are concurrency risks under high upload traffic?
**Answer direction:**
- Parsing is CPU/memory intensive and synchronous.
- Current mitigation: upload limits and batch caps.
- Scale path: queue workers + rate limits + autoscaling.

### Q4. Why save both `analysis.json` and `design.md`?
**Answer direction:**
- `analysis.json`: machine-friendly reproducibility and downstream tooling.
- `design.md`: human + LLM promptable artifact.
- Dual outputs support observability and product utility.

### Q5. Why store both inches and percentages in bounding boxes?
**Answer direction:**
- Inches for precise diagnostics/debugging.
- Percentages for generalized style transfer and cross-canvas guidance.

### Q6. How would you support enterprise governance requirements?
**Answer direction:**
- Add authn/authz, tenant isolation, encrypted object storage.
- Add audit logs and retention policies.
- Convert filesystem runs to managed storage with signed access.

### Q7. How do you reason about correctness without pixel-perfect reconstruction?
**Answer direction:**
- Objective is design abstraction quality, not full rendering parity.
- Evaluate by consistency of inferred tokens/layout patterns and output usefulness in slide generation tasks.

### Q8. What is the biggest data-structure bottleneck today?
**Answer direction:**
- Flat element lists require repeated scans for some heuristics.
- Possible upgrade: precomputed spatial index per slide when deck size/concurrency grows.

### Q9. If you had to support 1000 decks/hour, first three changes?
**Answer direction:**
1. Queue-based extraction workers.
2. External artifact storage + metadata DB.
3. Operational telemetry (p95 parse time, failure taxonomy, queue lag).

### Q10. Why this architecture is maintainable for a small team?
**Answer direction:**
- Minimal dependencies.
- Explicit module boundaries.
- Test-backed behavior locks.
- Incremental replacement path for each subsystem.

---

## 7. Suggested Deep Dive Drill Topics
- Walkthrough of one `/extract` request from upload to persisted run.
- Live critique of heuristics confidence diagnostics and failure cases.
- Migration design from local filesystem to cloud object storage.
- Backward-compatible schema evolution strategy for `analysis` payload.
