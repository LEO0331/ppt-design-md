from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

ElementType = Literal["text", "image", "shape", "chart_like", "group_like"]


class BoundingBox(BaseModel):
    x_in: float
    y_in: float
    w_in: float
    h_in: float
    x_pct: float
    y_pct: float
    w_pct: float
    h_pct: float


class ElementAnalysis(BaseModel):
    type: ElementType
    bbox: BoundingBox
    text_sample: str | None = None
    font_family: str | None = None
    font_size_pt: float | None = None
    font_bold: bool | None = None
    font_italic: bool | None = None
    fill_color: str | None = None
    line_color: str | None = None
    text_color: str | None = None


class SlideAnalysis(BaseModel):
    slide_index: int
    background: str | None = None
    elements: list[ElementAnalysis] = Field(default_factory=list)


class PresentationInfo(BaseModel):
    slide_width_in: float
    slide_height_in: float
    aspect_ratio: float


class ThemeInfo(BaseModel):
    candidate_fonts: list[str] = Field(default_factory=list)
    candidate_colors: list[str] = Field(default_factory=list)
    common_font_sizes_pt: list[float] = Field(default_factory=list)
    theme_fonts: list[str] = Field(default_factory=list)
    theme_colors: list[str] = Field(default_factory=list)


class TypographyRole(BaseModel):
    role: str
    rules: str
    confidence: float


class LayoutArchetype(BaseModel):
    name: str
    slide_indices: list[int]
    confidence: float


class ComponentCandidate(BaseModel):
    name: str
    signature: str
    occurrences: int
    confidence: float


class SpacingRhythm(BaseModel):
    left_margins_in: list[float] = Field(default_factory=list)
    right_margins_in: list[float] = Field(default_factory=list)
    top_offsets_in: list[float] = Field(default_factory=list)
    vertical_gaps_in: list[float] = Field(default_factory=list)
    column_gaps_in: list[float] = Field(default_factory=list)
    alignment_anchors_in: list[float] = Field(default_factory=list)


class PatternDiagnostics(BaseModel):
    scores: dict[str, float] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    evidence: dict[str, int] = Field(default_factory=dict)


class PatternInfo(BaseModel):
    dominant_layouts: list[LayoutArchetype] = Field(default_factory=list)
    typography_roles: list[TypographyRole] = Field(default_factory=list)
    component_candidates: list[ComponentCandidate] = Field(default_factory=list)
    spacing_rhythm: SpacingRhythm = Field(default_factory=SpacingRhythm)
    common_alignments: list[str] = Field(default_factory=list)
    color_roles: dict[str, list[str]] = Field(default_factory=dict)
    diagnostics: PatternDiagnostics = Field(default_factory=PatternDiagnostics)


class DeckAnalysis(BaseModel):
    presentation: PresentationInfo
    theme: ThemeInfo
    slides: list[SlideAnalysis] = Field(default_factory=list)
    patterns: PatternInfo = Field(default_factory=PatternInfo)


class ExtractResponse(BaseModel):
    design_md: str
    analysis: DeckAnalysis
    run_id: str | None = None


class BatchItemResponse(BaseModel):
    filename: str
    design_md: str
    analysis: DeckAnalysis
    run_id: str


class BatchExtractResponse(BaseModel):
    results: list[BatchItemResponse] = Field(default_factory=list)


class SaveEditedDesignRequest(BaseModel):
    run_id: str
    design_md: str


class SaveEditedDesignResponse(BaseModel):
    run_id: str
    saved_path: str
