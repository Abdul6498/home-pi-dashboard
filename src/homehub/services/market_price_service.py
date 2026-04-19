from __future__ import annotations

import json
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class MarketPriceService:
    """Fetch compact market data with stable fallbacks."""

    def __init__(self) -> None:
        self._headers = {
            "User-Agent": "home-pi-dashboard",
        }

    def fetch_prices(self) -> list[dict[str, str]]:
        items = self._fetch_crypto_prices()
        items.extend(self._fetch_stock_prices())
        return items

    def _fetch_crypto_prices(self) -> list[dict[str, str]]:
        params = {
            "ids": "bitcoin,ethereum,solana",
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

        mapping = [
            ("BTC", "bitcoin"),
            ("ETH", "ethereum"),
            ("SOL", "solana"),
        ]
        items: list[dict[str, str]] = []
        for symbol, key in mapping:
            item = payload.get(key, {})
            price = float(item.get("eur", 0))
            change = float(item.get("eur_24h_change", item.get("usd_24h_change", 0)))
            items.append(
                {
                    "section": "CRYPTO",
                    "sectionColor": "#8fd8ff",
                    "symbol": symbol,
                    "price": f"\u20ac{price:,.0f}" if price >= 100 else f"\u20ac{price:,.2f}",
                    "change": f"{change:+.1f}%",
                    "changeColor": "#8bf15e" if change >= 0 else "#ff8f8f",
                    "priceColor": "#ffe39c",
                }
            )
        return items

    def _fetch_stock_prices(self) -> list[dict[str, str]]:
        instruments = [
            {"symbol": "AVGO", "label": "AVGO"},
            {"symbol": "GOOGL", "label": "GOOGL"},
            {"symbol": "EWG2.SG", "label": "EUWAX"},
            {"symbol": "VVSM.DE", "label": "VANECK SEMI"},
            {"symbol": "ISLN.L", "label": "ISH SILVER"},
        ]
        items: list[dict[str, str]] = []
        usd_per_eur = self._fetch_usd_per_eur()

        for instrument in instruments:
            symbol = instrument["symbol"]
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
                    "section": "STOCK",
                    "sectionColor": "#ffb870",
                    "symbol": instrument["label"],
                    "price": f"\u20ac{price:,.2f}",
                    "change": f"{change:+.1f}%",
                    "changeColor": "#8bf15e" if change >= 0 else "#ff8f8f",
                    "priceColor": "#ffc98b",
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
        return [
            {
                "section": "CRYPTO",
                "sectionColor": "#8fd8ff",
                "symbol": "BTC",
                "price": "N/A",
                "change": "--",
                "changeColor": "#9eb3c9",
                "priceColor": "#ffe39c",
            },
            {
                "section": "CRYPTO",
                "sectionColor": "#8fd8ff",
                "symbol": "ETH",
                "price": "N/A",
                "change": "--",
                "changeColor": "#9eb3c9",
                "priceColor": "#ffe39c",
            },
            {
                "section": "CRYPTO",
                "sectionColor": "#8fd8ff",
                "symbol": "SOL",
                "price": "N/A",
                "change": "--",
                "changeColor": "#9eb3c9",
                "priceColor": "#ffe39c",
            },
        ]

    def _fallback_stock_prices(self) -> list[dict[str, str]]:
        return [
            {
                "section": "STOCK",
                "sectionColor": "#ffb870",
                "symbol": "AVGO",
                "price": "N/A",
                "change": "--",
                "changeColor": "#9eb3c9",
                "priceColor": "#ffc98b",
            },
            {
                "section": "STOCK",
                "sectionColor": "#ffb870",
                "symbol": "GOOGL",
                "price": "N/A",
                "change": "--",
                "changeColor": "#9eb3c9",
                "priceColor": "#ffc98b",
            },
            {
                "section": "STOCK",
                "sectionColor": "#ffb870",
                "symbol": "EUWAX",
                "price": "N/A",
                "change": "--",
                "changeColor": "#9eb3c9",
                "priceColor": "#ffc98b",
            },
            {
                "section": "STOCK",
                "sectionColor": "#ffb870",
                "symbol": "VANECK SEMI",
                "price": "N/A",
                "change": "--",
                "changeColor": "#9eb3c9",
                "priceColor": "#ffc98b",
            },
            {
                "section": "STOCK",
                "sectionColor": "#ffb870",
                "symbol": "ISH SILVER",
                "price": "N/A",
                "change": "--",
                "changeColor": "#9eb3c9",
                "priceColor": "#ffc98b",
            },
        ]
