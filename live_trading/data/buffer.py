from collections import deque
from typing import Dict
from alpaca.data.models.bars import Bar
import pandas as pd

""" 
StockDataBuffer
- This class is used to hold stock data over last 20 minutes since which is needed when creating features for the prediction.

"""

class StockDataBuffer:
    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self.buffers: Dict[str, deque] = {}

    def add(self, symbol: str, bar: Bar):
        # Convert Bar to a Dict object for easier handling
        bar = bar.model_dump()
        if symbol not in self.buffers:
            self.buffers[symbol] = deque(maxlen=self.window_size)
        self.buffers[symbol].append(bar)

    def get_df(self, symbol: str) -> pd.DataFrame:
        if symbol not in self.buffers:
            return pd.DataFrame()
        return pd.DataFrame(list(self.buffers[symbol]))