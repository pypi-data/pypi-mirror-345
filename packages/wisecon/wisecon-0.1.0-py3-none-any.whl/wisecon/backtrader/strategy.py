import pandas as pd
from pandas import DataFrame
from wisecon.utils.logger import LoggerMixin


__all__ = ['Backtrader']


class Backtrader(LoggerMixin):
    """简易回测框架"""
    data: DataFrame
    start_date: str
    end_date: str
    slippage: float
    commission: float

    def validate_data(self):
        """"""
        if self.start_date is None:
            self.start_date = self.data["date"].min()
        if self.end_date is None:
            self.end_date = self.data["date"].max()

        data_columns = ["date", "open", "high", "low", "close", "volume"]
        if any([column not in self.data.columns for column in data_columns]):
            raise ValueError(f"Data must contain columns: {data_columns}")
        if pd.to_datetime(self.data["date"].min()) > pd.to_datetime(self.start_date):
            raise ValueError(f"Start date {self.start_date} is earlier than the earliest date in the data.")
        if pd.to_datetime(self.data["date"].max()) < pd.to_datetime(self.end_date):
            raise ValueError(f"End date {self.end_date} is later than the latest date in the data.")
        self.select_data_date()
        for column in ["open", "high", "low", "close", "volume"]:
            self.data[column] = self.data[column].astype(float)

    def select_data_date(self):
        """"""
        if "date" in self.data.columns:
            self.data["date"] = pd.to_datetime(self.data["date"])
            cond_date = self.data["date"].between(pd.to_datetime(self.start_date), pd.to_datetime(self.end_date), inclusive="both")
            self.data = self.data[cond_date]

    def data_prepare(self):
        """"""
        pass

    def strategy(self, ):
        """"""
        pass

    def backtest_strategy(self):
        """"""
        self.data['strategy_return_daily'] = self.data['change_pct'] * self.data['position']
        self.data['market_return'] = (1 + self.data['change_pct']).cumprod()
        self.data['strategy_return'] = (1 + self.data['strategy_return_daily']).cumprod()

    def run(self):
        """"""
        self.validate_data()

        self.data_prepare()
        self.backtest_strategy()
        return self.data

    def plot_echarts(self):
        """"""
        pass

    def show_validation(self):
        """"""

