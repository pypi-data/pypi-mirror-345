import unittest
import pandas as pd
from wisecon.stock.kline import *
from wisecon.backtrader import *


class TestValidate(unittest.TestCase):
    def test_win_rate(self):
        """"""
        data = KLine(security_code="002594", period="1D", size=800).load()
        df_data = data.to_frame()
        df_data.rename(columns={"time": "date"}, inplace=True)

        strategy = AverageLineStrategy(data=df_data, short_ma=5, long_ma=40)
        df_data = strategy.run()
        columns = ["date", "signal", "position", "ma_short", "ma_long", "market_return", "strategy_return"]
        print(df_data.loc[df_data.signal.notna(), columns])

        print(win_rate(data=df_data))
        print(maximum_drawdown(data=df_data))

