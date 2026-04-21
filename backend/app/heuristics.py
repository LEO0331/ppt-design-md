from __future__ import annotations

from collections import Counter, defaultdict

from .models import (
    ComponentCandidate,
    ElementAnalysis,
    LayoutArchetype,
    PatternDiagnostics,
    SlideAnalysis,
    SpacingRhythm,
    TypographyRole,
)
from .utils import clustered_values


def infer_typography_roles(slides: list[SlideAnalysis], slide_height_in: float) -> list[TypographyRole]:
    text_elements: list[ElementAnalysis] = []
    for slide in slides:
        text_elements.extend([e for e in slide.elements if e.type == "text" and e.font_size_pt])

    if not text_elements:
        return []

    sizes = sorted([e.font_size_pt for e in text_elements if e.font_size_pt])
    if not sizes:
        return []

    p90 = sizes[min(len(sizes) - 1, int(len(sizes) * 0.9))]
    p70 = sizes[min(len(sizes) - 1, int(len(sizes) * 0.7))]
    p40 = sizes[min(len(sizes) - 1, int(len(sizes) * 0.4))]
    top_text = [e for e in text_elements if e.bbox.y_in <= slide_height_in * 0.35]
    bottom_text = [e for e in text_elements if e.bbox.y_in >= slide_height_in * 0.8]

    title_conf = min(0.9, round(0.45 + (len(top_text) / max(1, len(text_elements))), 2))
    caption_conf = min(0.85, round(0.4 + (len(bottom_text) / max(1, len(text_elements))), 2))

    roles: list[TypographyRole] = []
    roles.append(
        TypographyRole(
            role="title",
            rules=f"Text >= {p90:.1f}pt and mostly in top 35% of slide",
            confidence=title_conf,
        )
    )
    roles.append(
        TypographyRole(
            role="subtitle",
            rules=f"Text around {p70:.1f}-{p90:.1f}pt near title region",
            confidence=0.6,
        )
    )
    roles.append(
        TypographyRole(
            role="section header",
            rules=f"Text around {p70:.1f}pt with wider boxes and upper-half placement",
            confidence=0.56,
        )
    )
    roles.append(
        TypographyRole(
            role="body",
            rules=f"Text around {p40:.1f}-{p70:.1f}pt in middle/lower regions",
            confidence=min(0.9, round(0.5 + (len(text_elements) / 20), 2)),
        )
    )
    roles.append(
        TypographyRole(
            role="caption / footnote",
            rules=f"Small text <= {p40:.1f}pt near bottom 20% of slide",
            confidence=caption_conf,
        )
    )

    return roles


def _slide_signature(slide: SlideAnalysis) -> str:
    text_count = len([e for e in slide.elements if e.type == "text"])
    image_count = len([e for e in slide.elements if e.type == "image"])
    shape_count = len([e for e in slide.elements if e.type in {"shape", "group_like", "chart_like"}])

    left = len([e for e in slide.elements if e.bbox.x_pct < 35])
    right = len([e for e in slide.elements if e.bbox.x_pct > 55])

    if text_count <= 2 and image_count == 0 and shape_count <= 2:
        return "cover slide"
    if text_count <= 3 and shape_count <= 1 and image_count == 0:
        return "section divider"
    if left >= 2 and right >= 2:
        return "title + two-column"
    if image_count >= 1 and text_count >= 1:
        return "image + text"
    if shape_count >= 4:
        return "metrics/cards"
    return "title + body"


def infer_layout_archetypes(slides: list[SlideAnalysis]) -> list[LayoutArchetype]:
    buckets: dict[str, list[int]] = defaultdict(list)
    for slide in slides:
        buckets[_slide_signature(slide)].append(slide.slide_index)

    archetypes: list[LayoutArchetype] = []
    total = max(len(slides), 1)
    for name, indices in sorted(buckets.items(), key=lambda x: len(x[1]), reverse=True):
        confidence = min(0.9, round(0.4 + (len(indices) / total), 2))
        archetypes.append(LayoutArchetype(name=name, slide_indices=indices, confidence=confidence))
    return archetypes


def infer_spacing_rhythm(slides: list[SlideAnalysis], slide_width_in: float, slide_height_in: float) -> SpacingRhythm:
    lefts: list[float] = []
    rights: list[float] = []
    tops: list[float] = []
    v_gaps: list[float] = []
    col_gaps: list[float] = []
    anchors: list[float] = []

    for slide in slides:
        elements = sorted(slide.elements, key=lambda e: (e.bbox.y_in, e.bbox.x_in))
        for idx, el in enumerate(elements):
            lefts.append(el.bbox.x_in)
            rights.append(max(0.0, slide_width_in - (el.bbox.x_in + el.bbox.w_in)))
            tops.append(el.bbox.y_in)
            anchors.append(el.bbox.x_in)
            if idx > 0:
                prev = elements[idx - 1]
                gap = el.bbox.y_in - (prev.bbox.y_in + prev.bbox.h_in)
                if 0 <= gap <= slide_height_in:
                    v_gaps.append(gap)
        row = sorted(slide.elements, key=lambda e: e.bbox.x_in)
        for idx in range(1, len(row)):
            prev = row[idx - 1]
            gap = row[idx].bbox.x_in - (prev.bbox.x_in + prev.bbox.w_in)
            if 0 <= gap <= slide_width_in:
                col_gaps.append(gap)

    return SpacingRhythm(
        left_margins_in=clustered_values(lefts),
        right_margins_in=clustered_values(rights),
        top_offsets_in=clustered_values(tops),
        vertical_gaps_in=clustered_values(v_gaps),
        column_gaps_in=clustered_values(col_gaps),
        alignment_anchors_in=clustered_values(anchors),
    )


def infer_component_candidates(slides: list[SlideAnalysis]) -> list[ComponentCandidate]:
    signature_counter: Counter[str] = Counter()
    for slide in slides:
        for el in slide.elements:
            width_bucket = round(el.bbox.w_pct / 10) * 10
            height_bucket = round(el.bbox.h_pct / 10) * 10
            signature = f"{el.type}:{width_bucket}x{height_bucket}"
            signature_counter[signature] += 1

    candidates: list[ComponentCandidate] = []
    for signature, count in signature_counter.most_common(12):
        if count < 3:
            continue
        if signature.startswith("text"):
            name = "title block" if "30x" in signature or "40x" in signature else "footer note"
        elif signature.startswith("image"):
            name = "image frame"
        elif signature.startswith("shape"):
            name = "metric card"
        else:
            name = "callout"
        confidence = min(0.88, round(0.42 + (count / max(8, len(slides) * 2)), 2))
        candidates.append(ComponentCandidate(name=name, signature=signature, occurrences=count, confidence=confidence))
    return candidates


def infer_common_alignments(slides: list[SlideAnalysis]) -> list[str]:
    anchors = Counter()
    for slide in slides:
        for el in slide.elements:
            if abs(el.bbox.x_pct - 0) < 5:
                anchors["flush-left"] += 1
            if abs((el.bbox.x_pct + el.bbox.w_pct) - 100) < 5:
                anchors["flush-right"] += 1
            center = el.bbox.x_pct + (el.bbox.w_pct / 2)
            if abs(center - 50) < 5:
                anchors["centered"] += 1

    return [name for name, count in anchors.most_common(4) if count >= 2]


def infer_color_roles(colors: list[str]) -> dict[str, list[str]]:
    neutrals: list[str] = []
    primary: list[str] = []
    accents: list[str] = []

    for color in colors:
        if color in {"#000000", "#FFFFFF", "#F2F2F2", "#333333", "#666666", "#999999"}:
            neutrals.append(color)
        elif color.endswith(("00", "33", "66")):
            primary.append(color)
        else:
            accents.append(color)

    def uniq(values: list[str]) -> list[str]:
        seen = set()
        output = []
        for v in values:
            if v not in seen:
                seen.add(v)
                output.append(v)
        return output

    return {
        "neutrals": uniq(neutrals)[:6],
        "primary": uniq(primary)[:6],
        "accents": uniq(accents)[:6],
    }


def infer_pattern_diagnostics(
    slides: list[SlideAnalysis],
    typography_roles: list[TypographyRole],
    dominant_layouts: list[LayoutArchetype],
    component_candidates: list[ComponentCandidate],
    color_count: int,
) -> PatternDiagnostics:
    text_elements = sum(1 for slide in slides for e in slide.elements if e.type == "text")
    total_elements = sum(len(slide.elements) for slide in slides)
    slide_count = len(slides)

    typography_score = round(min(1.0, (len(typography_roles) / 5) * (text_elements / max(1, slide_count * 2))), 2)
    layout_score = round(min(1.0, len(dominant_layouts) / max(1, slide_count / 2)), 2)
    component_score = round(min(1.0, len(component_candidates) / 4), 2)
    color_score = round(min(1.0, color_count / 6), 2)
    coverage_score = round(min(1.0, total_elements / max(1, slide_count * 4)), 2)
    overall_score = round(
        (typography_score * 0.25)
        + (layout_score * 0.25)
        + (component_score * 0.2)
        + (color_score * 0.15)
        + (coverage_score * 0.15),
        2,
    )

    warnings: list[str] = []
    if slide_count < 3:
        warnings.append("Low slide count reduces archetype confidence.")
    if text_elements < slide_count:
        warnings.append("Sparse text elements reduce typography-role confidence.")
    if color_count < 3:
        warnings.append("Limited explicit colors found; theme inheritance may be partial.")
    if not component_candidates:
        warnings.append("No repeating component signatures crossed threshold.")

    evidence = {
        "slides": slide_count,
        "elements": total_elements,
        "text_elements": text_elements,
        "color_tokens": color_count,
        "layout_clusters": len(dominant_layouts),
        "component_candidates": len(component_candidates),
    }
    scores = {
        "typography": typography_score,
        "layout": layout_score,
        "components": component_score,
        "color": color_score,
        "coverage": coverage_score,
        "overall": overall_score,
    }
    return PatternDiagnostics(scores=scores, warnings=warnings, evidence=evidence)
