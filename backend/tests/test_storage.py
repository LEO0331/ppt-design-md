from __future__ import annotations

from pathlib import Path

import pytest

from app import storage
from app.models import DeckAnalysis, PatternInfo, PresentationInfo, ThemeInfo


def _analysis() -> DeckAnalysis:
    return DeckAnalysis(
        presentation=PresentationInfo(slide_width_in=13.333, slide_height_in=7.5, aspect_ratio=1.778),
        theme=ThemeInfo(),
        slides=[],
        patterns=PatternInfo(),
    )


def test_save_run_creates_expected_artifacts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(storage, "RUNS_DIR", tmp_path)

    run_id = storage.save_run("sample.pptx", "# DESIGN.md", _analysis())

    run_dir = tmp_path / run_id
    assert (run_dir / "design.md").exists()
    assert (run_dir / "analysis.json").exists()
    assert (run_dir / "meta.json").exists()


def test_save_edited_design_rejects_missing_run_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(storage, "RUNS_DIR", tmp_path)

    with pytest.raises(FileNotFoundError):
        storage.save_edited_design("abcdef123456", "# DESIGN.md")


def test_save_edited_design_writes_file_for_existing_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(storage, "RUNS_DIR", tmp_path)
    run_dir = tmp_path / "abcdef123456"
    run_dir.mkdir()

    saved = storage.save_edited_design("abcdef123456", "# DESIGN.md")

    assert saved == run_dir / "design.edited.md"
    assert saved.read_text(encoding="utf-8") == "# DESIGN.md"
