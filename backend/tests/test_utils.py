from __future__ import annotations

from app.extractor import _shape_type
from app.utils import EMU_PER_INCH, clustered_values, emu_to_inches, rgb_to_hex, safe_round, to_pct, top_n_counts


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


def test_emu_to_inches_returns_zero_for_none() -> None:
    assert emu_to_inches(None) == 0.0


def test_emu_to_inches_converts_known_constant() -> None:
    assert emu_to_inches(EMU_PER_INCH) == 1.0


def test_safe_round_and_pct_helpers() -> None:
    assert safe_round(1.23456, 2) == 1.23
    assert to_pct(2.5, 10.0) == 25.0


def test_to_pct_returns_zero_when_total_not_positive() -> None:
    assert to_pct(5.0, 0.0) == 0.0


def test_rgb_to_hex_returns_none_for_invalid_input() -> None:
    assert rgb_to_hex("FFF") is None


def test_top_n_counts_returns_most_common_values() -> None:
    items = top_n_counts(["a", "b", "a", None, "c", "a", "b"], n=2)
    assert items == ["a", "b"]
