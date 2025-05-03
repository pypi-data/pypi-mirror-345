from pandas import DataFrame
from typing import Optional, Callable
from .strategy import *


__all__ = [
    "AverageLineStrategy"
]


class AverageLineStrategy(Backtrader):
    """"""

    def __init__(
            self,
            data: DataFrame,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
            short_ma: int = 5,
            long_ma: int = 20,
            slippage: float = 0.0,
            commission: float = 0.0,
            logger: Optional[Callable] = None,
            verbose: Optional[bool] = False,
    ):
        """均线策略

        Args:
            data: K线数据
            start_date: 回测开始日期
            end_date: 回测结束日期
            short_ma: 短期均线
            long_ma: 长期均线
            slippage: 滑点
            commission: 手续费
            logger: 日志
            verbose: 是否打印日志
        """
        self.data = data
        self.start_date = start_date
        self.end_date = end_date
        self.short_ma = short_ma
        self.long_ma = long_ma
        self.slippage = slippage
        self.commission = commission
        self.logger = logger
        self.verbose = verbose

    def data_prepare(self):
        """"""
        # 计算单日涨跌幅
        self.data['change_pct'] = self.data['close'].pct_change()

        # 计算短期和长期均线
        self.data['ma_short'] = self.data['close'].rolling(self.short_ma).mean()
        self.data['ma_long'] = self.data['close'].rolling(self.long_ma).mean()

        # 填充空值
        self.data['ma_short'] = self.data["ma_short"].fillna(value=self.data['close'].expanding().mean())
        self.data['ma_long'] = self.data["ma_long"].fillna(value=self.data['close'].expanding().mean())

        # 计算均线交叉信号 - Buy
        cond_buy = (self.data['ma_short'] >= self.data['ma_long']) & \
            (self.data['ma_short'].shift(1) < self.data['ma_long'].shift(1))
        self.data.loc[cond_buy, 'signal'] = 1

        # 计算均线交叉信号 - Sell
        cond_sell = (self.data['ma_short'] <= self.data['ma_long']) & \
            (self.data['ma_short'].shift(1) > self.data['ma_long'].shift(1))
        self.data.loc[cond_sell, 'signal'] = 0

        # 计算每日仓位: 将交易信号下移一格，表示第二天买入，1表示满仓，0表示空仓
        self.data['position'] = self.data['signal'].shift()
        self.data['position'] =self.data['position'].ffill()
        self.data['position'] = self.data['position'].fillna(value=0)

        # 排除当天开盘就涨跌停导致无法交易的情况
        # 1. 找出开盘涨停的日期：即今天的开盘价相对于昨天的收盘价上涨了9.7%以上，此处不用10%是因为由于4舍5入，涨停不一定就是10%
        cond_cannot_buy = self.data['open'] > self.data['close'].shift(1) * 1.097
        # 将开盘涨停且当前position为1时的position设为空值
        self.data.loc[cond_cannot_buy & (self.data['position'] == 1), "position"] = None
        # 找出开盘跌停的日期，即今天的开盘价相对于昨天的收盘价跌了9.7%（1-0.097=0.903）
        cond_cannot_sell = self.data['open'] < self.data['close'].shift(1) * 0.903
        # 将开盘跌停且当前position为0时的position设为空值
        self.data.loc[cond_cannot_sell & (self.data['position'] == 0), 'position'] = None
        # position为空的日期表示不能买卖。position仓位只能和前一个交易日保持一致
        self.data["position"] = self.data["position"].ffill()
