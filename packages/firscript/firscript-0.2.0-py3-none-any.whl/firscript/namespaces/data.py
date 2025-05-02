from typing import Any, Optional
import pandas as pd
from firscript.namespaces.base import BaseNamespace

class HistoricalSeries:
    def __init__(self, series):
        self.series = series

    def __getitem__(self, idx):
        # Reverse index: 0 = last, 1 = second last, etc.
        if idx < 0 or idx >= len(self.series):
            return None
        return self.series.iloc[-(idx + 1)]

    def __repr__(self):
        return str(self[0])

class DataNamespace(BaseNamespace):
    key = 'data'
    
    def __init__(self, shared: dict[str, Any], column_mapping: dict[str, str] = None):
        super().__init__(shared)
        
        self.column_mapping = column_mapping
        self.__raw_all: pd.DataFrame = None
        self.__all: pd.DataFrame = None
        self.__current_bar: pd.Series = None

    def set_current_bar(self, bar: pd.Series):
        self.__current_bar = bar
        self.shared.setdefault(self.key, {})['current'] = bar
        
    def set_all_bar(self, bars: pd.DataFrame):
        self.__raw_all = bars
        self.shared.setdefault(self.key, {})['raw_all'] = self.__raw_all
        self.__all = self.rename_columns(bars)
        self.shared.setdefault(self.key, {})['all'] = self.__all

    def rename_columns(self, df: pd.DataFrame):
        if not self.column_mapping:
            return df
        return df.rename(columns=self.column_mapping)
    
    @property
    def current(self):
        return self.__current_bar

    @property
    def all(self):
        return self.__all
    
    @property
    def raw_all(self):
        return self.__raw_all
    
    # This provides pinescript like access pattern.
    # - data.close will return the last item, data.close[1] will return the second last item
    @property
    def timestamp(self):
        if 'timestamp' not in self.__all.columns:
            return None
        return HistoricalSeries(self.__all['timestamp'])
    
    @property
    def open(self):
        if 'open' not in self.__all.columns:
            return None 
        return HistoricalSeries(self.__all['open'])
    
    @property
    def close(self):
        if 'close' not in self.__all.columns:
            return None
        return HistoricalSeries(self.__all['close'])
    
    @property
    def high(self):
        if 'high' not in self.__all.columns:
            return None
        return HistoricalSeries(self.__all['high'])
    
    @property
    def low(self):
        if 'low' not in self.__all.columns:
            return None
        return HistoricalSeries(self.__all['low'])
    
    @property
    def volume(self):
        if 'volume' not in self.__all.columns:
            return None
        return HistoricalSeries(self.__all['volume'])