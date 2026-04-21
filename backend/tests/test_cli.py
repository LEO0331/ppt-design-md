from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from app import cli
from app.models import DeckAnalysis, PatternInfo, PresentationInfo, ThemeInfo


def _analysis() -> DeckAnalysis:
    return DeckAnalysis(
        presentation=PresentationInfo(slide_width_in=13.333, slide_height_in=7.5, aspect_ratio=1.778),
        theme=ThemeInfo(candidate_fonts=["Calibri"], candidate_colors=["#111111"], common_font_sizes_pt=[24.0]),
        slides=[],
        patterns=PatternInfo(),
    )


def test_write_single_writes_markdown_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "extract_pptx", lambda _: _analysis())
    monkeypatch.setattr(cli, "generate_design_md", lambda _: "# DESIGN.md\n\ncontent")

    out = tmp_path / "out.md"
    cli._write_single(tmp_path / "a.pptx", out, None, persist_run=False)

    assert out.read_text(encoding="utf-8").startswith("# DESIGN.md")


def test_write_single_writes_json_when_path_provided(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "extract_pptx", lambda _: _analysis())
    monkeypatch.setattr(cli, "generate_design_md", lambda _: "# DESIGN.md")

    out = tmp_path / "out.md"
    json_out = tmp_path / "out.json"
    cli._write_single(tmp_path / "a.pptx", out, json_out, persist_run=False)

    payload = json.loads(json_out.read_text(encoding="utf-8"))
    assert "presentation" in payload


def test_write_single_persists_run_when_enabled(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    called = {"count": 0}
    monkeypatch.setattr(cli, "extract_pptx", lambda _: _analysis())
    monkeypatch.setattr(cli, "generate_design_md", lambda _: "# DESIGN.md")

    def _save_run(filename: str, design_md: str, analysis: DeckAnalysis) -> str:
        called["count"] += 1
        assert filename == "a.pptx"
        assert design_md == "# DESIGN.md"
        return "abc123def456"

    monkeypatch.setattr(cli, "save_run", _save_run)
    cli._write_single(tmp_path / "a.pptx", tmp_path / "out.md", None, persist_run=True)

    assert called["count"] == 1


def test_run_batch_raises_when_no_pptx_found(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        cli._run_batch(tmp_path, tmp_path / "out", persist_run=False)


def test_run_batch_generates_outputs_per_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    a = tmp_path / "a.pptx"
    b = tmp_path / "b.pptx"
    a.write_bytes(b"PKfake")
    b.write_bytes(b"PKfake")
    monkeypatch.setattr(cli, "extract_pptx", lambda _: _analysis())
    monkeypatch.setattr(cli, "generate_design_md", lambda _: "# DESIGN.md")

    out_dir = tmp_path / "out"
    cli._run_batch(tmp_path, out_dir, persist_run=False)

    assert (out_dir / "a.design.md").exists()
    assert (out_dir / "a.analysis.json").exists()
    assert (out_dir / "b.design.md").exists()
    assert (out_dir / "b.analysis.json").exists()


def test_run_batch_persists_each_file_when_enabled(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    a = tmp_path / "a.pptx"
    b = tmp_path / "b.pptx"
    a.write_bytes(b"PKfake")
    b.write_bytes(b"PKfake")
    monkeypatch.setattr(cli, "extract_pptx", lambda _: _analysis())
    monkeypatch.setattr(cli, "generate_design_md", lambda _: "# DESIGN.md")

    called: list[str] = []

    def _save_run(filename: str, design_md: str, analysis: DeckAnalysis) -> str:
        called.append(filename)
        return "runid"

    monkeypatch.setattr(cli, "save_run", _save_run)
    cli._run_batch(tmp_path, tmp_path / "out", persist_run=True)

    assert called == ["a.pptx", "b.pptx"]


def test_main_uses_batch_mode_when_batch_dir_provided(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    called = {"batch": 0}

    def _run_batch(batch_dir: Path, output_dir: Path, persist_run: bool) -> None:
        called["batch"] += 1
        assert batch_dir == tmp_path

    monkeypatch.setattr(cli, "_run_batch", _run_batch)
    monkeypatch.setattr(sys, "argv", ["cli", "--batch-dir", str(tmp_path)])

    cli.main()

    assert called["batch"] == 1


def test_main_rejects_non_pptx_input(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["cli", "input.txt"])
    with pytest.raises(SystemExit):
        cli.main()
