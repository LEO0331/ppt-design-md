from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .models import DeckAnalysis


RUNS_DIR = Path(__file__).resolve().parents[1] / "runs"
RUN_ID_RE = re.compile(r"^[a-f0-9]{12}$")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def save_run(filename: str, design_md: str, analysis: DeckAnalysis) -> str:
    """Persist extraction outputs and return run id."""
    run_id = uuid4().hex[:12]
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    (run_dir / "design.md").write_text(design_md, encoding="utf-8")
    (run_dir / "analysis.json").write_text(json.dumps(analysis.model_dump(), indent=2), encoding="utf-8")
    (run_dir / "meta.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "filename": filename,
                "created_at": _now_iso(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return run_id


def save_edited_design(run_id: str, design_md: str) -> Path:
    """Save user-edited markdown for an existing run and return saved path."""
    if not RUN_ID_RE.fullmatch(run_id):
        raise FileNotFoundError(f"Run not found: {run_id}")

    run_dir = (RUNS_DIR / run_id).resolve()
    runs_root = RUNS_DIR.resolve()
    if not str(run_dir).startswith(str(runs_root)):
        raise FileNotFoundError(f"Run not found: {run_id}")
    if not run_dir.exists():
        raise FileNotFoundError(f"Run not found: {run_id}")
    target = run_dir / "design.edited.md"
    target.write_text(design_md, encoding="utf-8")
    return target
