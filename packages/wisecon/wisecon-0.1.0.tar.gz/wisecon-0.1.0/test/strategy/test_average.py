import unittest
from wisecon.stock.kline import *
from wisecon.backtrader import *


class TestAverageStrategy(unittest.TestCase):
    """"""
    def test_average_strategy(self):
        """"""
        data = KLine(plate_code="BK0887", period="1D", size=500).load()
        df_data = data.to_frame()
        df_data.rename(columns={"time": "date"}, inplace=True)

        strategy = AverageLineStrategy(data=df_data, start_date="2022-10-28", end_date="2024-11-19")
        df_data = strategy.run()
        print(df_data)

    def test_average_strategy_300(self):
        """"""
        data = KLine(market_code="000300", period="1D", size=800).load()
        df_data = data.to_frame()
        df_data.rename(columns={"time": "date"}, inplace=True)

        strategy = AverageLineStrategy(data=df_data)
        df_data = strategy.run()
        columns = ["date", "signal", "ma_short", "ma_long", "market_return", "strategy_return"]
        # print(df_data.loc[df_data.signal.notna(), columns])
        print(df_data.tail(10))
        print(df_data.loc[df_data.strategy_return >= 1.2, columns])
        print(df_data.strategy_return.max())
        print(df_data.market_return.max())

    def test_average_strategy_byd(self):
        """"""
        data = KLine(security_code="002594", period="1D", size=800).load()
        df_data = data.to_frame()
        df_data.rename(columns={"time": "date"}, inplace=True)

        strategy = AverageLineStrategy(data=df_data, short_ma=5, long_ma=40)
        df_data = strategy.run()
        columns = ["date", "signal", "position", "ma_short", "ma_long", "market_return", "strategy_return"]
        # print(df_data.loc[df_data.signal.notna(), columns])
        print(df_data.loc[df_data.position == 0, columns])

    def test_average_strategy_300750(self):
        """"""
        data = KLine(security_code="300750", period="1D", size=800).load()
        df_data = data.to_frame()
        df_data.rename(columns={"time": "date"}, inplace=True)

        strategy = AverageLineStrategy(data=df_data, short_ma=5, long_ma=40)
        df_data = strategy.run()
        columns = ["date", "signal", "ma_short", "ma_long", "market_return", "strategy_return"]
        print(df_data.loc[df_data.signal.notna(), columns])

    def test_average_strategy_600036(self):
        """"""
        data = KLine(security_code="000858", period="1D", size=800).load()
        df_data = data.to_frame()
        df_data.rename(columns={"time": "date"}, inplace=True)

        strategy = AverageLineStrategy(data=df_data, short_ma=5, long_ma=40)
        df_data = strategy.run()
        columns = ["date", "signal", "position", "ma_short", "ma_long", "market_return", "strategy_return"]
        print(df_data.loc[df_data.signal.notna(), columns])
        # print(df_data.loc[:, columns])

    def test_average_strategy_600900(self):
        """"""
        data = KLine(security_code="300059", period="1D", size=800).load()
        df_data = data.to_frame()
        df_data.rename(columns={"time": "date"}, inplace=True)

        strategy = AverageLineStrategy(data=df_data, short_ma=5, long_ma=120)
        df_data = strategy.run()
        columns = ["date", "signal", "ma_short", "ma_long", "market_return", "strategy_return"]
        print(df_data.loc[df_data.signal.notna(), columns])

