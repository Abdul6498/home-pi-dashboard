from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SeasonalStyle:
    name: str
    title: str
    accent_color: str
    decorative_strip: str
    decorative_color: str
    background_asset: str


def season_for_now(now: datetime | None = None) -> SeasonalStyle:
    current = now or datetime.now()
    month = current.month

    if month in {3, 4, 5}:
        return SeasonalStyle(
            name="spring",
            title="SPRING",
            accent_color="#7de57a",
            decorative_strip="🌱 🌿 🌼 🌷 🍃 🌼 🌿 🌱",
            decorative_color="#88ef84",
            background_asset="spring.jpg",
        )
    if month in {6, 7, 8}:
        return SeasonalStyle(
            name="summer",
            title="SUMMER",
            accent_color="#ffd860",
            decorative_strip="☀ ☀ 🌿 🌼 ☀ 🌿 🌼 ☀",
            decorative_color="#ffe16f",
            background_asset="summer.jpg",
        )
    if month in {9, 10, 11}:
        return SeasonalStyle(
            name="autumn",
            title="AUTUMN",
            accent_color="#ffb067",
            decorative_strip="🍁 🍂 🍃 🍁 🍂 🍃 🍁 🍂",
            decorative_color="#ffb981",
            background_asset="autumn.jpg",
        )
    return SeasonalStyle(
        name="winter",
        title="WINTER",
        accent_color="#9fd9ff",
        decorative_strip="❄ ❄ ✧ ❄ ❄ ✧ ❄ ❄",
        decorative_color="#b4e2ff",
        background_asset="winter.jpg",
    )
