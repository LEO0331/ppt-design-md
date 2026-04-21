from __future__ import annotations

from app.extractor import _shape_type
from app.utils import clustered_values


class _DummyShape:
    def __init__(self, shape_type: str, has_chart: bool = False, has_text_frame: bool = False) -> None:
        self.shape_type = shape_type
        self.has_chart = has_chart
        self.has_text_frame = has_text_frame


def test_clustered_values_prefers_largest_clusters() -> None:
    values = [1.0, 1.05, 1.1, 3.0, 3.05, 8.0]
    clusters = clustered_values(values, tolerance=0.15)
    assert clusters[0] == 1.05
    assert clusters[1] == 3.02


def test_shape_type_detects_group_from_enum_string() -> None:
    shape = _DummyShape(shape_type="MSO_SHAPE_TYPE.GROUP (6)")
    assert _shape_type(shape) == "group_like"
