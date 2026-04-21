from __future__ import annotations

from types import SimpleNamespace

from app.extractor import _extract_theme_colors, _extract_theme_fonts, _is_group_shape, _resolve_font_color


class _Color:
    def __init__(self, rgb=None, theme_color=None):
        self.rgb = rgb
        self.theme_color = theme_color


class _Font:
    def __init__(self, color):
        self.color = color


def test_is_group_shape_returns_true_for_group_enum_string() -> None:
    shape = SimpleNamespace(shape_type="MSO_SHAPE_TYPE.GROUP (6)")
    assert _is_group_shape(shape) is True


def test_resolve_font_color_prefers_rgb_value() -> None:
    color = _Color(rgb="112233")
    font = _Font(color)
    assert _resolve_font_color(font, {"ACCENT1": "#FF0000"}) == "#112233"


def test_resolve_font_color_uses_theme_mapping_when_rgb_missing() -> None:
    color = _Color(rgb=None, theme_color="MSO_THEME_COLOR.ACCENT1")
    font = _Font(color)
    assert _resolve_font_color(font, {"ACCENT1": "#FF0000"}) == "#FF0000"


def test_extract_theme_fonts_reads_major_and_minor_fonts() -> None:
    prs = SimpleNamespace(
        slide_master=SimpleNamespace(
            theme=SimpleNamespace(
                font_scheme=SimpleNamespace(
                    major_font=SimpleNamespace(latin=SimpleNamespace(typeface="Aptos Display")),
                    minor_font=SimpleNamespace(latin=SimpleNamespace(typeface="Aptos")),
                )
            )
        )
    )

    fonts = _extract_theme_fonts(prs)

    assert fonts == ["Aptos Display", "Aptos"]


def test_extract_theme_colors_skips_non_rgb_entries() -> None:
    class _BadColor:
        @property
        def rgb(self):
            raise TypeError("no rgb")

    color_scheme = SimpleNamespace(
        dk1=SimpleNamespace(rgb="111111"),
        lt1=_BadColor(),
        dk2=SimpleNamespace(rgb=None),
        lt2=SimpleNamespace(rgb="FFFFFF"),
        accent1=SimpleNamespace(rgb="FF0000"),
        accent2=SimpleNamespace(rgb=None),
        accent3=SimpleNamespace(rgb=None),
        accent4=SimpleNamespace(rgb=None),
        accent5=SimpleNamespace(rgb=None),
        accent6=SimpleNamespace(rgb=None),
        hlink=SimpleNamespace(rgb=None),
        fol_hlink=SimpleNamespace(rgb=None),
    )
    prs = SimpleNamespace(slide_master=SimpleNamespace(theme=SimpleNamespace(color_scheme=color_scheme)))

    colors = _extract_theme_colors(prs)

    assert colors["DK1"] == "#111111"
    assert colors["LT2"] == "#FFFFFF"
    assert colors["ACCENT1"] == "#FF0000"
