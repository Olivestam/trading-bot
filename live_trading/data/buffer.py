from collections import deque
from typing import Dict
import pandas as pd

class StockDataBuffer:
    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self.buffers: Dict[str, deque] = {}

    def add(self, symbol: str, bar: Dict):
        if symbol not in self.buffers:
            self.buffers[symbol] = deque(maxlen=self.window_size)
        self.buffers[symbol].append(bar)

    def get_df(self, symbol: str) -> pd.DataFrame:
        if symbol not in self.buffers:
            return pd.DataFrame()
        return pd.DataFrame(list(self.buffers[symbol]))