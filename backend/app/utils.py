from __future__ import annotations

from collections import Counter
from typing import Iterable

EMU_PER_INCH = 914400


def emu_to_inches(value: int | None) -> float:
    if not value:
        return 0.0
    return round(value / EMU_PER_INCH, 3)


def safe_round(value: float, digits: int = 3) -> float:
    return round(value, digits)


def to_pct(value_in: float, total_in: float) -> float:
    if total_in <= 0:
        return 0.0
    return safe_round((value_in / total_in) * 100.0, 2)


def rgb_to_hex(rgb: object | None) -> str | None:
    """Convert python-pptx RGBColor-like value to #RRGGBB."""
    if rgb is None:
        return None
    text = str(rgb)
    if len(text) == 6:
        return f"#{text.upper()}"
    return None


def top_n_counts(items: Iterable[object], n: int = 8) -> list[object]:
    counter = Counter(x for x in items if x is not None)
    return [item for item, _ in counter.most_common(n)]


def clustered_values(values: list[float], tolerance: float = 0.2, limit: int = 6) -> list[float]:
    if not values:
        return []
    ordered = sorted(values)
    clusters: list[list[float]] = [[ordered[0]]]
    for value in ordered[1:]:
        if abs(value - clusters[-1][-1]) <= tolerance:
            clusters[-1].append(value)
        else:
            clusters.append([value])
    ranked = sorted(
        ((len(cluster), round(sum(cluster) / len(cluster), 2)) for cluster in clusters),
        key=lambda item: item[0],
        reverse=True,
    )
    return [mean for _, mean in ranked[:limit]]
