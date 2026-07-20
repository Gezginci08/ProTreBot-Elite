import ccxt

from indicators.technical import calculate_indicators


def main() -> None:
    exchange = ccxt.binance(
        {
            "enableRateLimit": True,
            "options": {
                "defaultType": "spot",
            },
        }
    )

    symbol = "BTC/USDT"
    timeframe = "15m"

    print(f"{symbol} verileri çekiliyor...")

    ohlcv = exchange.fetch_ohlcv(
        symbol=symbol,
        timeframe=timeframe,
        limit=250,
    )

    result = calculate_indicators(
        symbol=symbol,
        timeframe=timeframe,
        ohlcv=ohlcv,
    )

    print("\n" + "=" * 55)
    print("PROTREBOT ELITE — İLK TEKNİK ANALİZ")
    print("=" * 55)

    print(f"Coin              : {result.symbol}")
    print(f"Zaman dilimi      : {result.timeframe}")
    print(f"Fiyat             : {result.price:,.2f}")

    print(f"\nTrend             : {result.trend}")
    print(f"Momentum          : {result.momentum}")

    print(f"\nEMA20             : {result.ema20:,.2f}")
    print(f"EMA50             : {result.ema50:,.2f}")
    print(f"EMA200            : {result.ema200:,.2f}")

    print(f"\nRSI               : {result.rsi:.2f}")
    print(f"MACD Histogram    : {result.macd_histogram:.4f}")
    print(f"ADX               : {result.adx:.2f}")
    print(f"ATR               : {result.atr:,.2f}")

    print(f"\nHacim oranı       : {result.volume_ratio:.2f}x")
    print(f"Destek            : {result.support:,.2f}")
    print(f"Direnç            : {result.resistance:,.2f}")

    print(f"\nBollinger üst     : {result.bollinger_upper:,.2f}")
    print(f"Bollinger orta    : {result.bollinger_middle:,.2f}")
    print(f"Bollinger alt     : {result.bollinger_lower:,.2f}")

    print("=" * 55)


if __name__ == "__main__":
    main()