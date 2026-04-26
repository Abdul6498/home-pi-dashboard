from __future__ import annotations

import json
from collections import OrderedDict
from dataclasses import dataclass
from datetime import date, datetime
from typing import Callable, Iterable, Mapping, MutableMapping, Optional
from urllib import error, parse, request

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None  # type: ignore[assignment]


ALADHAN_BASE_URL = "https://api.aladhan.com/v1"
PRAYER_ORDER = (
    "Imsak",
    "Fajr",
    "Sunrise",
    "Dhuhr",
    "Asr",
    "Sunset",
    "Maghrib",
    "Isha",
    "Midnight",
    "Firstthird",
    "Lastthird",
)


class AladhanAPIError(RuntimeError):
    pass


@dataclass(frozen=True)
class LocationQuery:
    city: str
    country: str
    state: Optional[str] = None

    def to_params(self) -> MutableMapping[str, str]:
        params: MutableMapping[str, str] = {"city": self.city, "country": self.country}
        if self.state:
            params["state"] = self.state
        return params


@dataclass(frozen=True)
class PrayerMeta:
    timezone: str
    latitude: float
    longitude: float
    method: str
    school: str
    latitude_adjustment_method: str


@dataclass(frozen=True)
class PrayerSchedule:
    date: date
    readable_date: str
    gregorian_date: str
    hijri_date: str
    hijri_month_name: str
    hijri_year: str
    timings: Mapping[str, datetime]
    meta: PrayerMeta


def _clean_time_string(value: str) -> str:
    return value.split("(")[0].strip()


def _parse_time(value: str, day: date) -> datetime:
    cleaned = _clean_time_string(value)
    parsed_time = None
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            parsed_time = datetime.strptime(cleaned, fmt).time()
            break
        except ValueError:
            continue
    if parsed_time is None:
        raise ValueError(f"Could not parse timing '{value}'")
    return datetime.combine(day, parsed_time)


class AladhanAPIClient:
    def __init__(
        self,
        base_url: str = ALADHAN_BASE_URL,
        opener: Optional[Callable[[str], object]] = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._opener = opener or request.urlopen

    def timings_by_city(
        self,
        *,
        location: LocationQuery,
        calculation_method: int = 2,
        school: int = 0,
        target_date: Optional[date] = None,
    ) -> PrayerSchedule:
        params = location.to_params()
        params["method"] = str(calculation_method)
        params["school"] = str(school)
        if target_date:
            params["date"] = target_date.strftime("%d-%m-%Y")
        payload = self._call("/timingsByCity", params)
        return self._build_schedule(payload["data"])

    def timings(
        self,
        *,
        latitude: float,
        longitude: float,
        calculation_method: int = 2,
        school: int = 0,
        target_date: Optional[date] = None,
    ) -> PrayerSchedule:
        params: MutableMapping[str, str] = {
            "latitude": str(latitude),
            "longitude": str(longitude),
            "method": str(calculation_method),
            "school": str(school),
        }
        if target_date:
            params["date"] = target_date.strftime("%d-%m-%Y")
        payload = self._call("/timings", params)
        return self._build_schedule(payload["data"])

    def monthly_calendar(
        self,
        *,
        location: LocationQuery,
        month: int,
        year: int,
        calculation_method: int = 2,
        school: int = 0,
    ) -> Iterable[PrayerSchedule]:
        params = location.to_params()
        params["method"] = str(calculation_method)
        params["school"] = str(school)
        params["month"] = str(month)
        params["year"] = str(year)
        payload = self._call("/calendarByCity", params)
        for entry in payload["data"]:
            yield self._build_schedule(entry)

    def _call(
        self, endpoint: str, params: Optional[MutableMapping[str, str]] = None
    ) -> Mapping[str, object]:
        query = parse.urlencode(params or {})
        url = f"{self._base_url}{endpoint}"
        if query:
            url = f"{url}?{query}"
        try:
            response = self._opener(url)
            data = json.load(response)
        except error.URLError as exc:
            raise AladhanAPIError(f"Failed to reach Aladhan API: {exc}") from exc
        if data.get("code") != 200:
            raise AladhanAPIError(f"Aladhan API error: {data.get('status')}")
        return data

    def _build_schedule(self, data: Mapping[str, object]) -> PrayerSchedule:
        timings_block: Mapping[str, str] = data["timings"]  # type: ignore[assignment]
        date_block: Mapping[str, object] = data["date"]  # type: ignore[assignment]
        meta_block: Mapping[str, object] = data["meta"]  # type: ignore[assignment]

        gregorian_date = date_block["gregorian"]["date"]  # type: ignore[index]
        readable_date = date_block["readable"]  # type: ignore[index]
        hijri_date = date_block["hijri"]["date"]  # type: ignore[index]
        hijri_month_name = date_block["hijri"]["month"]["en"]  # type: ignore[index]
        hijri_year = date_block["hijri"]["year"]  # type: ignore[index]
        day = datetime.strptime(gregorian_date, "%d-%m-%Y").date()

        timezone_name = str(meta_block.get("timezone", "UTC"))
        tzinfo = None
        if ZoneInfo is not None:
            try:
                tzinfo = ZoneInfo(timezone_name)
            except Exception:
                tzinfo = None

        ordered_timings: "OrderedDict[str, datetime]" = OrderedDict()
        seen = set()
        for key in PRAYER_ORDER:
            if key in timings_block:
                moment = _parse_time(timings_block[key], day)
                if tzinfo is not None:
                    moment = moment.replace(tzinfo=tzinfo)
                ordered_timings[key] = moment
                seen.add(key)

        for key, value in timings_block.items():
            if key not in seen:
                moment = _parse_time(value, day)
                if tzinfo is not None:
                    moment = moment.replace(tzinfo=tzinfo)
                ordered_timings[key] = moment

        meta = PrayerMeta(
            timezone=timezone_name,
            latitude=float(meta_block.get("latitude", 0)),
            longitude=float(meta_block.get("longitude", 0)),
            method=meta_block.get("method", {}).get("name", "Unknown"),  # type: ignore[union-attr]
            school=meta_block.get("school", "Standard"),  # type: ignore[arg-type]
            latitude_adjustment_method=meta_block.get(
                "latitudeAdjustmentMethod", "Middle of the Night"
            ),  # type: ignore[arg-type]
        )
        return PrayerSchedule(
            date=day,
            readable_date=readable_date,
            gregorian_date=gregorian_date,
            hijri_date=hijri_date,
            hijri_month_name=hijri_month_name,
            hijri_year=hijri_year,
            timings=ordered_timings,
            meta=meta,
        )


class AzanTimeService:
    def __init__(self, client: Optional[AladhanAPIClient] = None) -> None:
        self._client = client or AladhanAPIClient()

    def daily_prayer_schedule(
        self,
        *,
        city: str,
        country: str,
        state: Optional[str] = None,
        calculation_method: int = 2,
        school: int = 0,
        target_date: Optional[date] = None,
    ) -> PrayerSchedule:
        location = LocationQuery(city=city, country=country, state=state)
        return self._client.timings_by_city(
            location=location,
            calculation_method=calculation_method,
            school=school,
            target_date=target_date,
        )

    def daily_prayer_schedule_by_coordinates(
        self,
        *,
        latitude: float,
        longitude: float,
        calculation_method: int = 2,
        school: int = 0,
        target_date: Optional[date] = None,
    ) -> PrayerSchedule:
        return self._client.timings(
            latitude=latitude,
            longitude=longitude,
            calculation_method=calculation_method,
            school=school,
            target_date=target_date,
        )
