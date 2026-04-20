from __future__ import annotations

import json
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class MarketPriceService:
    """Fetch compact market data with stable fallbacks."""

    def __init__(self) -> None:
        self._headers = {
            "User-Agent": "home-pi-dashboard",
        }
        self._market_config = self._load_market_config()

    def fetch_prices(self) -> list[dict[str, str]]:
        items = self._fetch_crypto_prices()
        items.extend(self._fetch_stock_prices())
        return items

    def _fetch_crypto_prices(self) -> list[dict[str, str]]:
        crypto_definitions = self._crypto_definitions()
        params = {
            "ids": ",".join(item["provider_id"] for item in crypto_definitions),
            "vs_currencies": "eur",
            "include_24hr_change": "true",
        }
        url = f"https://api.coingecko.com/api/v3/simple/price?{urlencode(params)}"

        try:
            request = Request(url, headers=self._headers)
            with urlopen(request, timeout=6) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (URLError, TimeoutError, OSError, json.JSONDecodeError):
            return self._fallback_crypto_prices()

        items: list[dict[str, str]] = []
        for definition in crypto_definitions:
            symbol = definition["symbol"]
            key = definition["provider_id"]
            item = payload.get(key, {})
            price = float(item.get("eur", 0))
            change = float(item.get("eur_24h_change", item.get("usd_24h_change", 0)))
            items.append(
                {
                    "section": definition["section"],
                    "sectionColor": definition["sectionColor"],
                    "symbol": symbol,
                    "price": f"\u20ac{price:,.0f}" if price >= 100 else f"\u20ac{price:,.2f}",
                    "change": f"{change:+.1f}%",
                    "changeColor": "#8bf15e" if change >= 0 else "#ff8f8f",
                    "priceColor": definition["priceColor"],
                }
            )
        return items

    def _fetch_stock_prices(self) -> list[dict[str, str]]:
        instruments = self._stock_definitions()
        items: list[dict[str, str]] = []
        usd_per_eur = self._fetch_usd_per_eur()

        for instrument in instruments:
            symbol = instrument["provider_id"]
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1d&interval=1d"
            try:
                request = Request(url, headers=self._headers)
                with urlopen(request, timeout=6) as response:
                    payload = json.loads(response.read().decode("utf-8"))
            except (URLError, TimeoutError, OSError, json.JSONDecodeError):
                return self._fallback_stock_prices()

            result = payload.get("chart", {}).get("result") or []
            if not result:
                return self._fallback_stock_prices()

            meta = result[0].get("meta", {})
            currency = str(meta.get("currency", "USD")).upper()
            price_usd = float(meta.get("regularMarketPrice", 0))
            previous_close_usd = float(
                meta.get("chartPreviousClose", meta.get("previousClose", 0))
            )
            if currency == "EUR":
                price = price_usd
                previous_close = previous_close_usd
            elif currency == "USD" and usd_per_eur > 0:
                price = price_usd / usd_per_eur
                previous_close = previous_close_usd / usd_per_eur
            else:
                price = price_usd
                previous_close = previous_close_usd
            if previous_close > 0:
                change = ((price - previous_close) / previous_close) * 100
            else:
                change = 0.0

            items.append(
                {
                    "section": instrument["section"],
                    "sectionColor": instrument["sectionColor"],
                    "symbol": instrument["symbol"],
                    "price": f"\u20ac{price:,.2f}",
                    "change": f"{change:+.1f}%",
                    "changeColor": "#8bf15e" if change >= 0 else "#ff8f8f",
                    "priceColor": instrument["priceColor"],
                }
            )
        return items

    def _fetch_usd_per_eur(self) -> float:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/EURUSD=X?range=1d&interval=1d"
        try:
            request = Request(url, headers=self._headers)
            with urlopen(request, timeout=6) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (URLError, TimeoutError, OSError, json.JSONDecodeError):
            return 1.09

        result = payload.get("chart", {}).get("result") or []
        if not result:
            return 1.09

        meta = result[0].get("meta", {})
        return float(meta.get("regularMarketPrice", 1.09))

    def _fallback_crypto_prices(self) -> list[dict[str, str]]:
        return [self._fallback_item(definition) for definition in self._crypto_definitions()]

    def _fallback_stock_prices(self) -> list[dict[str, str]]:
        return [self._fallback_item(definition) for definition in self._stock_definitions()]

    def _fallback_item(self, definition: dict[str, str]) -> dict[str, str]:
        return {
            "section": definition["section"],
            "sectionColor": definition["sectionColor"],
            "symbol": definition["symbol"],
            "price": "N/A",
            "change": "--",
            "changeColor": "#9eb3c9",
            "priceColor": definition["priceColor"],
        }

    def _load_market_config(self) -> dict[str, list[dict[str, str]]]:
        config_path = Path(__file__).resolve().parents[1] / "assets" / "markets.json"
        with config_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return {
            "crypto": [dict(item) for item in payload.get("crypto", [])],
            "stocks": [dict(item) for item in payload.get("stocks", [])],
        }

    def _crypto_definitions(self) -> list[dict[str, str]]:
        return list(self._market_config.get("crypto", []))

    def _stock_definitions(self) -> list[dict[str, str]]:
        return list(self._market_config.get("stocks", []))
