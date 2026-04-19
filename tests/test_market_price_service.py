from homehub.services.market_price_service import MarketPriceService


def test_fallback_prices_shape() -> None:
    service = MarketPriceService()

    crypto_items = service._fallback_crypto_prices()
    stock_items = service._fallback_stock_prices()

    assert [item["symbol"] for item in crypto_items] == ["BTC", "ETH", "SOL"]
    assert [item["symbol"] for item in stock_items] == ["AVGO"]

    for item in crypto_items:
        assert item["price"].startswith("EUR ")
        assert item["section"] in {"CRYPTO", "STOCK"}
        assert item["priceColor"].startswith("#")
        assert item["change"].endswith("%")
        assert item["changeColor"].startswith("#")

    for item in stock_items:
        assert item["price"].startswith("USD ")
        assert item["section"] in {"CRYPTO", "STOCK"}
        assert item["priceColor"].startswith("#")
        assert item["change"].endswith("%")
        assert item["changeColor"].startswith("#")
