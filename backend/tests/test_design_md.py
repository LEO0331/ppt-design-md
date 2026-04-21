from __future__ import annotations

from app.design_md import generate_design_md
from app.models import (
    DeckAnalysis,
    LayoutArchetype,
    PatternInfo,
    PresentationInfo,
    SlideAnalysis,
    ThemeInfo,
    TypographyRole,
)


def test_generate_design_md_sections_present() -> None:
    analysis = DeckAnalysis(
        presentation=PresentationInfo(slide_width_in=13.333, slide_height_in=7.5, aspect_ratio=1.778),
        theme=ThemeInfo(
            candidate_fonts=["Calibri", "Arial"],
            candidate_colors=["#FFFFFF", "#111111", "#0A84FF"],
            common_font_sizes_pt=[36.0, 24.0, 16.0],
        ),
        slides=[SlideAnalysis(slide_index=1, elements=[])],
        patterns=PatternInfo(
            dominant_layouts=[LayoutArchetype(name="title + body", slide_indices=[1], confidence=0.8)],
            typography_roles=[
                TypographyRole(role="title", rules="largest text on top", confidence=0.7),
            ],
            color_roles={"neutrals": ["#FFFFFF"], "primary": ["#111111"], "accents": ["#0A84FF"]},
        ),
    )

    output = generate_design_md(analysis)

    assert "# DESIGN.md" in output
    assert "## Color System" in output
    assert "## AI Generation Guidance" in output
    assert "Calibri" in output
