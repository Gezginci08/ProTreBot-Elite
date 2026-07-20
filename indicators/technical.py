from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import ADXIndicator, EMAIndicator, MACD
from ta.volatility import AverageTrueRange, BollingerBands


@dataclass(frozen=True)
class TechnicalResult:
    symbol: str
    timeframe: str

    price: float

    ema20: float
    ema50: float
    ema200: float

    rsi: float

    macd: float
    macd_signal: float
    macd_histogram: float

    bollinger_upper: float
    bollinger_middle: float
    bollinger_lower: float

    atr: float
    adx: float

    volume: float
    average_volume: float
    volume_ratio: float

    support: float
    resistance: float

    trend: str
    momentum: str


def ohlcv_to_dataframe(ohlcv: list[list[float]]) -> pd.DataFrame:
    if len(ohlcv) < 210:
        raise ValueError(
            f"EMA200 için en az 210 mum gerekiyor. Gelen mum: {len(ohlcv)}"
        )

    dataframe = pd.DataFrame(
        ohlcv,
        columns=[
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ],
    )

    dataframe["timestamp"] = pd.to_datetime(
        dataframe["timestamp"],
        unit="ms",
        utc=True,
    )

    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]

    dataframe[numeric_columns] = dataframe[numeric_columns].astype(float)

    return dataframe


def calculate_indicators(
    symbol: str,
    timeframe: str,
    ohlcv: list[list[float]],
) -> TechnicalResult:
    dataframe = ohlcv_to_dataframe(ohlcv)

    close = dataframe["close"]
    high = dataframe["high"]
    low = dataframe["low"]
    volume = dataframe["volume"]

    dataframe["ema20"] = EMAIndicator(
        close=close,
        window=20,
    ).ema_indicator()

    dataframe["ema50"] = EMAIndicator(
        close=close,
        window=50,
    ).ema_indicator()

    dataframe["ema200"] = EMAIndicator(
        close=close,
        window=200,
    ).ema_indicator()

    dataframe["rsi"] = RSIIndicator(
        close=close,
        window=14,
    ).rsi()

    macd_indicator = MACD(
        close=close,
        window_slow=26,
        window_fast=12,
        window_sign=9,
    )

    dataframe["macd"] = macd_indicator.macd()
    dataframe["macd_signal"] = macd_indicator.macd_signal()
    dataframe["macd_histogram"] = macd_indicator.macd_diff()

    bollinger_indicator = BollingerBands(
        close=close,
        window=20,
        window_dev=2,
    )

    dataframe["bollinger_upper"] = (
        bollinger_indicator.bollinger_hband()
    )

    dataframe["bollinger_middle"] = (
        bollinger_indicator.bollinger_mavg()
    )

    dataframe["bollinger_lower"] = (
        bollinger_indicator.bollinger_lband()
    )

    atr_indicator = AverageTrueRange(
        high=high,
        low=low,
        close=close,
        window=14,
    )

    dataframe["atr"] = atr_indicator.average_true_range()

    adx_indicator = ADXIndicator(
        high=high,
        low=low,
        close=close,
        window=14,
    )

    dataframe["adx"] = adx_indicator.adx()

    dataframe["average_volume"] = volume.rolling(
        window=20
    ).mean()

    last = dataframe.iloc[-1]

    price = float(last["close"])

    ema20 = float(last["ema20"])
    ema50 = float(last["ema50"])
    ema200 = float(last["ema200"])

    rsi = float(last["rsi"])

    macd = float(last["macd"])
    macd_signal = float(last["macd_signal"])
    macd_histogram = float(last["macd_histogram"])

    bollinger_upper = float(last["bollinger_upper"])
    bollinger_middle = float(last["bollinger_middle"])
    bollinger_lower = float(last["bollinger_lower"])

    atr = float(last["atr"])
    adx = float(last["adx"])

    current_volume = float(last["volume"])
    average_volume = float(last["average_volume"])

    if average_volume > 0:
        volume_ratio = current_volume / average_volume
    else:
        volume_ratio = 0.0

    level_data = dataframe.iloc[-51:-1]

    support = float(level_data["low"].min())
    resistance = float(level_data["high"].max())

    trend = detect_trend(
        price=price,
        ema20=ema20,
        ema50=ema50,
        ema200=ema200,
    )

    momentum = detect_momentum(
        rsi=rsi,
        macd_histogram=macd_histogram,
        adx=adx,
    )

    return TechnicalResult(
        symbol=symbol,
        timeframe=timeframe,
        price=price,
        ema20=ema20,
        ema50=ema50,
        ema200=ema200,
        rsi=rsi,
        macd=macd,
        macd_signal=macd_signal,
        macd_histogram=macd_histogram,
        bollinger_upper=bollinger_upper,
        bollinger_middle=bollinger_middle,
        bollinger_lower=bollinger_lower,
        atr=atr,
        adx=adx,
        volume=current_volume,
        average_volume=average_volume,
        volume_ratio=volume_ratio,
        support=support,
        resistance=resistance,
        trend=trend,
        momentum=momentum,
    )


def detect_trend(
    price: float,
    ema20: float,
    ema50: float,
    ema200: float,
) -> str:
    if price > ema20 > ema50 > ema200:
        return "GÜÇLÜ YÜKSELİŞ"

    if price > ema50 > ema200:
        return "YÜKSELİŞ"

    if price < ema20 < ema50 < ema200:
        return "GÜÇLÜ DÜŞÜŞ"

    if price < ema50 < ema200:
        return "DÜŞÜŞ"

    return "YATAY / BELİRSİZ"


def detect_momentum(
    rsi: float,
    macd_histogram: float,
    adx: float,
) -> str:
    if (
        rsi >= 55
        and macd_histogram > 0
        and adx >= 20
    ):
        return "POZİTİF"

    if (
        rsi <= 45
        and macd_histogram < 0
        and adx >= 20
    ):
        return "NEGATİF"

    return "NÖTR"