from __future__ import annotations

from app.heuristics import (
    infer_color_roles,
    infer_common_alignments,
    infer_component_candidates,
    infer_layout_archetypes,
    infer_pattern_diagnostics,
)
from app.models import BoundingBox, ElementAnalysis, SlideAnalysis, TypographyRole


def _el(el_type: str, x: float, y: float, w: float, h: float) -> ElementAnalysis:
    return ElementAnalysis(
        type=el_type,
        bbox=BoundingBox(
            x_in=x,
            y_in=y,
            w_in=w,
            h_in=h,
            x_pct=x,
            y_pct=y,
            w_pct=w,
            h_pct=h,
        ),
    )


def test_infer_layout_archetypes_includes_two_column_pattern() -> None:
    slide = SlideAnalysis(
        slide_index=1,
        elements=[
            _el("text", 10, 10, 20, 20),
            _el("text", 15, 30, 20, 20),
            _el("text", 60, 10, 20, 20),
            _el("text", 62, 45, 18, 18),
            _el("shape", 65, 35, 20, 20),
        ],
    )

    layouts = infer_layout_archetypes([slide])

    assert layouts[0].name == "title + two-column"


def test_infer_common_alignments_detects_centered_elements() -> None:
    slide = SlideAnalysis(
        slide_index=1,
        elements=[
            _el("shape", 40, 10, 20, 20),
            _el("shape", 42, 40, 16, 20),
        ],
    )

    alignments = infer_common_alignments([slide])

    assert "centered" in alignments


def test_infer_component_candidates_finds_repeated_shape_signature() -> None:
    slides = [
        SlideAnalysis(slide_index=1, elements=[_el("shape", 10, 10, 30, 20)]),
        SlideAnalysis(slide_index=2, elements=[_el("shape", 12, 15, 31, 19)]),
        SlideAnalysis(slide_index=3, elements=[_el("shape", 9, 20, 30, 20)]),
    ]

    components = infer_component_candidates(slides)

    assert any(c.name == "metric card" for c in components)


def test_infer_color_roles_splits_neutral_primary_and_accent() -> None:
    roles = infer_color_roles(["#FFFFFF", "#120066", "#AA2211"])

    assert "#FFFFFF" in roles["neutrals"]
    assert "#120066" in roles["primary"]
    assert "#AA2211" in roles["accents"]


def test_infer_pattern_diagnostics_adds_warnings_for_sparse_data() -> None:
    slide = SlideAnalysis(slide_index=1, elements=[_el("shape", 10, 10, 20, 20)])
    diagnostics = infer_pattern_diagnostics(
        slides=[slide],
        typography_roles=[TypographyRole(role="body", rules="r", confidence=0.5)],
        dominant_layouts=[],
        component_candidates=[],
        color_count=1,
    )

    assert diagnostics.warnings
    assert diagnostics.scores["overall"] >= 0
