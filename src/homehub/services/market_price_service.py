from __future__ import annotations

import json
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class MarketPriceService:
    """Fetch compact market data with stable fallbacks."""

    def __init__(self) -> None:
        self._headers = {
            "User-Agent": "home-pi-dashboard/0.1 (+https://github.com/Abdul6498/home-pi-dashboard)",
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
                    "price": f"EUR {price:,.0f}" if price >= 100 else f"EUR {price:,.2f}",
                    "change": f"{change:+.1f}%",
                    "changeColor": "#8bf15e" if change >= 0 else "#ff8f8f",
                    "priceColor": "#ffe39c",
                }
            )
        return items

    def _fetch_stock_prices(self) -> list[dict[str, str]]:
        symbols = ["AVGO"]
        items: list[dict[str, str]] = []

        for symbol in symbols:
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
            price = float(meta.get("regularMarketPrice", 0))
            previous_close = float(meta.get("chartPreviousClose", meta.get("previousClose", 0)))
            if previous_close > 0:
                change = ((price - previous_close) / previous_close) * 100
            else:
                change = 0.0

            items.append(
                {
                    "section": "STOCK",
                    "sectionColor": "#ffb870",
                    "symbol": symbol,
                    "price": f"USD {price:,.2f}",
                    "change": f"{change:+.1f}%",
                    "changeColor": "#8bf15e" if change >= 0 else "#ff8f8f",
                    "priceColor": "#ffc98b",
                }
            )
        return items

    def _fallback_crypto_prices(self) -> list[dict[str, str]]:
        return [
            {
                "section": "CRYPTO",
                "sectionColor": "#8fd8ff",
                "symbol": "BTC",
                "price": "EUR 63,200",
                "change": "+1.4%",
                "changeColor": "#8bf15e",
                "priceColor": "#ffe39c",
            },
            {
                "section": "CRYPTO",
                "sectionColor": "#8fd8ff",
                "symbol": "ETH",
                "price": "EUR 2,940",
                "change": "+0.9%",
                "changeColor": "#8bf15e",
                "priceColor": "#ffe39c",
            },
            {
                "section": "CRYPTO",
                "sectionColor": "#8fd8ff",
                "symbol": "SOL",
                "price": "EUR 131",
                "change": "-0.6%",
                "changeColor": "#ff8f8f",
                "priceColor": "#ffe39c",
            },
        ]

    def _fallback_stock_prices(self) -> list[dict[str, str]]:
        return [
            {
                "section": "STOCK",
                "sectionColor": "#ffb870",
                "symbol": "AVGO",
                "price": "USD 406.54",
                "change": "+2.0%",
                "changeColor": "#8bf15e",
                "priceColor": "#ffc98b",
            }
        ]
