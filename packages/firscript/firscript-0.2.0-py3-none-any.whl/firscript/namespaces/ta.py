from typing import Any
import pandas as pd
import talipp.indicators as ta
from ..namespaces.base import BaseNamespace


class TANamespace(BaseNamespace):
    """Technical Analysis namespace implementation."""
    key = 'ta'
    
    @staticmethod
    def alma(series: pd.Series, length: int, offset: int, sigma: int) -> float:
        """Calculate Adaptive Moving Average."""
        return ta.ALMA(period=length, offset=offset, sigma=sigma, input_values=series.to_list())
    
    @staticmethod
    def atr(df: pd.DataFrame, length: int) -> float:
        """Calculate Average True Range."""

        ohlcv_list = [
            ta.OHLCV(open=o, high=h, low=l, close=c, volume=v)
            for o, h, l, c, v in zip(
                df["open"], df["high"], df["low"], df["close"], df["volume"]
            )
        ]

        return ta.ATR(
            period=length,
            input_values=ohlcv_list
        )
        
    @staticmethod
    def barssince(series: pd.Series) -> bool:
        """Calculate the number of bars since the last true condition."""
        raise NotImplementedError
        return ta.BarsSince(input_values=series.to_list())
    
    @staticmethod
    def bb(series: pd.Series, length: int, std_dev: int) -> tuple[float, float, float]:
        """Calculate Bollinger Bands."""
        raise NotImplementedError
        return ta.BollingerBands(period=length, std_dev=std_dev, input_values=series.to_list())
    
    @staticmethod
    def bbw(series: pd.Series, length: int, std_dev: int) -> float:
        """Calculate Bollinger Band Width."""
        raise NotImplementedError
        return ta.BollingerBandWidth(period=length, std_dev=std_dev, input_values=series.to_list())
    
    @staticmethod
    def cci(series: pd.Series, length: int, constant: int) -> float:
        """Calculate Commodity Channel Index."""
        raise NotImplementedError
        return ta.CCI(period=length, constant=constant, input_values=series.to_list())
    
    @staticmethod
    def macd(series: pd.Series, fast_length: int, slow_length: int, signal_length: int) -> float:
        """Calculate Moving Average Convergence Divergence."""
        return ta.MACD(fast_period=fast_length, slow_period=slow_length, signal_period=signal_length, input_values=series.to_list())

    @staticmethod
    def sma(series: pd.Series, length: int) -> float:
        """Calculate Simple Moving Average."""
        return ta.SMA(period=length, input_values=series.to_list())

    @staticmethod
    def ema(series: pd.Series, length: int) -> float:
        """Calculate Exponential Moving Average."""
        return ta.EMA(period=length, input_values=series.to_list())

    @staticmethod
    def rsi(series: pd.Series, length: int) -> float:
        """Calculate Relative Strength Index."""
        return ta.RSI(period=length, input_values=series.to_list())

    @staticmethod
    def atr(df: pd.DataFrame, length: int) -> float:
        """Calculate Average True Range."""

        ohlcv_list = [
            ta.OHLCV(open=o, high=h, low=l, close=c, volume=v)
            for o, h, l, c, v in zip(
                df["open"], df["high"], df["low"], df["close"], df["volume"]
            )
        ]

        return ta.ATR(
            period=length,
            input_values=ohlcv_list
        )
        
    @staticmethod
    def crossover(series1: pd.Series, series2: pd.Series) -> bool:
        """Check if series1 crosses above series2."""
        if series1[-1] is None or series2[-1] is None or series1[-2] is None or series2[-2] is None:
            return False
        return series1[-1] > series2[-1] and series1[-2] <= series2[-2]
    
    @staticmethod
    def crossunder(series1: pd.Series, series2: pd.Series) -> bool:
        """Check if series1 crosses below series2."""
        if series1[-1] is None or series2[-1] is None or series1[-2] is None or series2[-2] is None:
            return False
        return series1[-1] < series2[-1] and series1[-2] >= series2[-2]