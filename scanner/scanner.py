from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import ccxt


@dataclass(frozen=True)
class MarketResult:
    symbol: str
    last_price: float
    change_percent: float
    quote_volume: float


class BinanceScanner:
    """Binance spot piyasasından USDT paritelerini hızlıca tarar."""

    def __init__(self) -> None:
        self.exchange = ccxt.binance(
            {
                "enableRateLimit": True,
                "options": {
                    "defaultType": "spot",
                },
                "timeout": 20_000,
            }
        )

    def load_usdt_symbols(self) -> list[str]:
        """Aktif spot USDT paritelerini getirir."""
        markets = self.exchange.load_markets()

        symbols: list[str] = []

        for symbol, market in markets.items():
            if (
                market.get("active", True)
                and market.get("spot", False)
                and market.get("quote") == "USDT"
            ):
                symbols.append(symbol)

        return symbols

    def scan(self, limit: int = 30) -> list[MarketResult]:
        """
        Tüm ticker verilerini tek toplu istekte alır.
        Sonuçları USDT işlem hacmine göre sıralar.
        """
        start_time = time.perf_counter()

        usdt_symbols = set(self.load_usdt_symbols())
        tickers: dict[str, dict[str, Any]] = self.exchange.fetch_tickers()

        results: list[MarketResult] = []

        for symbol, ticker in tickers.items():
            if symbol not in usdt_symbols:
                continue

            last_price = self._to_float(ticker.get("last"))
            change_percent = self._to_float(ticker.get("percentage"))
            quote_volume = self._to_float(ticker.get("quoteVolume"))

            if last_price <= 0 or quote_volume <= 0:
                continue

            results.append(
                MarketResult(
                    symbol=symbol,
                    last_price=last_price,
                    change_percent=change_percent,
                    quote_volume=quote_volume,
                )
            )

        results.sort(key=lambda item: item.quote_volume, reverse=True)

        elapsed = time.perf_counter() - start_time

        print(f"\nTarama tamamlandı: {len(results)} USDT paritesi")
        print(f"Tarama süresi: {elapsed:.2f} saniye\n")

        return results[:limit]

    @staticmethod
    def _to_float(value: Any) -> float:
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return 0.0


def print_results(results: list[MarketResult]) -> None:
    print("=" * 76)
    print(
        f"{'SIRA':<6}"
        f"{'COIN':<18}"
        f"{'FİYAT':>16}"
        f"{'24S DEĞİŞİM':>16}"
        f"{'USDT HACİM':>20}"
    )
    print("=" * 76)

    for index, result in enumerate(results, start=1):
        print(
            f"{index:<6}"
            f"{result.symbol:<18}"
            f"{result.last_price:>16,.8f}"
            f"{result.change_percent:>15.2f}%"
            f"{result.quote_volume:>20,.0f}"
        )

    print("=" * 76)


def main() -> None:
    try:
        scanner = BinanceScanner()
        results = scanner.scan(limit=30)
        print_results(results)

    except ccxt.NetworkError as exc:
        print(f"İnternet veya Binance bağlantı hatası: {exc}")

    except ccxt.ExchangeError as exc:
        print(f"Binance API hatası: {exc}")

    except Exception as exc:
        print(f"Beklenmeyen hata: {exc}")


if __name__ == "__main__":
    main()