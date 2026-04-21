from __future__ import annotations

from .models import DeckAnalysis


def _fmt_list(values: list[object], fallback: str = "Not enough evidence") -> str:
    if not values:
        return fallback
    return ", ".join(str(v) for v in values)


def generate_design_md(analysis: DeckAnalysis) -> str:
    """Generate LLM-friendly design guidance from structured analysis."""
    p = analysis.presentation
    t = analysis.theme
    patterns = analysis.patterns

    dominant_layouts = patterns.dominant_layouts[:5]
    top_layout_names = [f"{l.name} (slides: {','.join(map(str, l.slide_indices[:5]))})" for l in dominant_layouts]

    roles_lines = [f"- {r.role}: {r.rules} (confidence: {r.confidence:.2f})" for r in patterns.typography_roles]
    components_lines = [
        f"- {c.name}: signature `{c.signature}`, occurrences={c.occurrences}, confidence={c.confidence:.2f}"
        for c in patterns.component_candidates[:8]
    ]

    spacing = patterns.spacing_rhythm
    low_confidence = []
    if len(t.candidate_fonts) < 2:
        low_confidence.append("Font inference is limited because few explicit run-level font declarations were found.")
    if len(t.candidate_colors) < 3:
        low_confidence.append("Color extraction confidence is limited due to sparse explicit color values.")
    if len(analysis.slides) < 3:
        low_confidence.append("Layout/archetype confidence is limited because the deck has fewer than 3 slides.")
    for warning in patterns.diagnostics.warnings:
        if warning not in low_confidence:
            low_confidence.append(warning)

    return f"""# DESIGN.md

## Design Intent
Use this guide to create new slides that preserve the source deck's visual language. Favor consistency in hierarchy, spacing, and composition over exact pixel replication.

## Canvas
- Slide size: {p.slide_width_in}in x {p.slide_height_in}in
- Aspect ratio: {p.aspect_ratio}
- Coordinate strategy: place major blocks on inferred anchors and preserve margin rhythm.

## Color System
- Candidate palette (ranked): {_fmt_list(t.candidate_colors)}
- Theme-declared colors: {_fmt_list(t.theme_colors)}
- Neutrals: {_fmt_list(patterns.color_roles.get('neutrals', []))}
- Primary colors: {_fmt_list(patterns.color_roles.get('primary', []))}
- Accent colors: {_fmt_list(patterns.color_roles.get('accents', []))}
- Guidance: use neutrals for backgrounds/body text, primary for structural emphasis, accents sparingly for highlights.

## Typography
- Candidate font families: {_fmt_list(t.candidate_fonts)}
- Theme-declared fonts: {_fmt_list(t.theme_fonts)}
- Common font sizes (pt): {_fmt_list(t.common_font_sizes_pt)}
- Inferred text roles:
{chr(10).join(roles_lines) if roles_lines else '- No strong role evidence found.'}

## Spacing
- Left margins (in): {_fmt_list(spacing.left_margins_in)}
- Right margins (in): {_fmt_list(spacing.right_margins_in)}
- Top offsets (in): {_fmt_list(spacing.top_offsets_in)}
- Vertical gaps (in): {_fmt_list(spacing.vertical_gaps_in)}
- Column gaps (in): {_fmt_list(spacing.column_gaps_in)}
- Alignment anchors (in): {_fmt_list(spacing.alignment_anchors_in)}

## Shapes and Components
{chr(10).join(components_lines) if components_lines else '- No repeated component signatures crossed threshold.'}
- Charts/SmartArt/grouped objects: treat as visual blocks in MVP; preserve container placement and proportion.

## Layout Archetypes
- Dominant layouts: {_fmt_list(top_layout_names)}
- Common alignments: {_fmt_list(patterns.common_alignments)}

## Composition Rules
- Preserve top-level structure first: title zone, content zone, support zone.
- Keep repeated components at consistent dimensions and anchors.
- Maintain margin and gap rhythm before adjusting decorative shape details.
- Use no more than 1-2 accent colors per slide.

## AI Generation Guidance
- Generate slides by selecting one inferred archetype, then fill with content while preserving spacing and typographic hierarchy.
- If uncertain about theme-inherited values, prefer explicitly observed fonts/colors from this file.
- Avoid introducing new component styles unless required by content.
- When chart details are unknown, emulate chart-like block style and relative placement only.

## Confidence and Gaps
{chr(10).join(f'- {item}' for item in low_confidence) if low_confidence else '- Confidence is moderate; extraction found recurring tokens and layouts.'}
- Diagnostic scores: {patterns.diagnostics.scores}
- Evidence counts: {patterns.diagnostics.evidence}
"""
