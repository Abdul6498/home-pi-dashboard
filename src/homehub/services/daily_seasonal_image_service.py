from __future__ import annotations

from datetime import date
import json
from pathlib import Path
from typing import Any
from urllib.parse import quote
from urllib.request import Request, urlopen


class DailySeasonalImageService:
    """Fetch one free seasonal image per day from Wikimedia Commons."""

    def __init__(self, cache_dir: Path | None = None):
        project_root = Path(__file__).resolve().parents[3]
        self._cache_dir = cache_dir or (project_root / "assets" / "seasonal" / "daily")
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._headers = {
            "User-Agent": "home-pi-dashboard/0.1 (+https://github.com/Abdul6498/home-pi-dashboard)",
        }

    def get_daily_image_path(self, season_name: str) -> Path | None:
        today = date.today().isoformat()
        stem = f"{season_name}_{today}"
        existing = self._find_existing(stem)
        if existing is not None:
            return existing

        title = self._pick_title(season_name, today)
        if not title:
            return None

        image_info = self._fetch_image_info(title)
        if not image_info:
            return None

        image_url = image_info.get("url")
        if not image_url:
            return None

        suffix = Path(str(image_url)).suffix.lower()
        if suffix not in {".jpg", ".jpeg", ".png"}:
            suffix = ".jpg"
        image_path = self._cache_dir / f"{stem}{suffix}"

        try:
            request = Request(str(image_url), headers=self._headers)
            with urlopen(request, timeout=8) as response:
                image_path.write_bytes(response.read())
        except OSError:
            return None

        self._write_attribution_json(
            stem=stem,
            title=title,
            image_url=str(image_url),
            image_info=image_info,
        )
        return image_path

    def cache_dir(self) -> Path:
        return self._cache_dir

    def _find_existing(self, stem: str) -> Path | None:
        for candidate in self._cache_dir.glob(f"{stem}.*"):
            if candidate.suffix.lower() in {".jpg", ".jpeg", ".png"}:
                return candidate
        return None

    def _pick_title(self, season_name: str, day_key: str) -> str | None:
        search_terms = {
            "spring": "spring landscape nature",
            "summer": "summer landscape nature",
            "autumn": "autumn forest landscape",
            "winter": "winter snow landscape",
        }
        query = search_terms.get(season_name, "landscape nature")
        endpoint = (
            "https://commons.wikimedia.org/w/api.php?"
            "action=query&format=json&list=search&srnamespace=6&srlimit=30&srsearch="
            f"{quote(query + ' filetype:bitmap')}"
        )
        payload = self._get_json(endpoint)
        if payload is None:
            return None

        items = payload.get("query", {}).get("search", [])
        titles = [
            str(item.get("title", ""))
            for item in items
            if str(item.get("title", "")).lower().startswith("file:")
            and str(item.get("title", "")).lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        if not titles:
            return None

        selector = int(day_key.replace("-", ""))
        return titles[selector % len(titles)]

    def _fetch_image_info(self, title: str) -> dict[str, Any] | None:
        endpoint = (
            "https://commons.wikimedia.org/w/api.php?"
            "action=query&format=json&prop=imageinfo&iiprop=url|extmetadata"
            f"&titles={quote(title)}"
        )
        payload = self._get_json(endpoint)
        if payload is None:
            return None

        pages = payload.get("query", {}).get("pages", {})
        for _, page in pages.items():
            image_info = page.get("imageinfo", [])
            if image_info:
                return image_info[0]
        return None

    def _write_attribution_json(
        self,
        stem: str,
        title: str,
        image_url: str,
        image_info: dict[str, Any],
    ) -> None:
        metadata = image_info.get("extmetadata", {})
        data = {
            "title": title,
            "image_url": image_url,
            "description_url": image_info.get("descriptionurl"),
            "artist": self._metadata_value(metadata, "Artist"),
            "license_short_name": self._metadata_value(metadata, "LicenseShortName"),
            "license_url": self._metadata_value(metadata, "LicenseUrl"),
            "usage_terms": self._metadata_value(metadata, "UsageTerms"),
        }
        (self._cache_dir / f"{stem}.json").write_text(
            json.dumps(data, indent=2),
            encoding="utf-8",
        )

    def _metadata_value(self, metadata: dict[str, Any], key: str) -> str:
        value = metadata.get(key, {})
        if isinstance(value, dict):
            return str(value.get("value", ""))
        return ""

    def _get_json(self, url: str) -> dict[str, Any] | None:
        try:
            request = Request(url, headers=self._headers)
            with urlopen(request, timeout=8) as response:
                return json.loads(response.read().decode("utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
