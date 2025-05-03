import numpy as np
from pandas import DataFrame


__all__ = [
    "strategy_return",
    "annualized_return",
    "sharpe_ratio",
    "maximum_drawdown",
    "sortino_ratio",
    "win_rate",
]


def strategy_return(data: DataFrame) -> float:
    """累计策略收益率

    Args:
        data: 包含策略收益的DataFrame

    Returns:
        累计策略收益率
    """
    if "strategy_return" in data.columns:
        return (data["strategy_return"].iloc[-1] - 1) * 100
    else:
        return np.nan


def annualized_return(
        data: DataFrame,
        periods_per_year: int = 252
) -> float:
    """年化收益率

    Args:
        data: 包含策略收益的DataFrame
        periods_per_year: 每个交易年的天数，默认为252

    Returns:
        年化收益率
    """
    return_value = strategy_return(data)
    if np.isnan(return_value):
        return np.nan
    else:
        n_years = len(data) / periods_per_year
        return (1 + return_value / 100) ** (1 / n_years) - 1


def annualized_volatility(
        data: DataFrame,
        periods_per_year: int = 252
) -> float:
    """年化波动率

    Args:
        data: 包含策略收益的DataFrame
        periods_per_year: 每个交易年的天数，默认为252

    Returns:
        年化波动率
    """
    if "strategy_return" in data.columns:
        daily_returns = data['strategy_return'].dropna()
        return daily_returns.std() * np.sqrt(periods_per_year)
    else:
        return np.nan


def sharpe_ratio(
        data,
        risk_free_rate: float = 0.01,
        periods_per_year: float = 252,
) -> float:
    """计算 夏普比率

    Args:
        data: 包含策略收益的DataFrame
        risk_free_rate: 无风险利率，默认为0.01
        periods_per_year: 每个交易年的天数，默认为252

    Returns:
        夏普比率
    """
    if "strategy_return" in data.columns:
        daily_returns = data["strategy_return"].dropna()
        excess_returns = daily_returns - risk_free_rate / periods_per_year
        return (excess_returns.mean() / excess_returns.std()) * np.sqrt(periods_per_year)
    else:
        return np.nan


def maximum_drawdown(
        data: DataFrame
) -> float:
    """计算最大回撤
    TODO: 分析发生最大回撤的交易过程

    Args:
        data: 包含策略收益的DataFrame

    Returns:
        最大回撤
    """
    df_data = data.copy()
    if "strategy_return" in data.columns:
        df_data["peak"] = df_data["strategy_return"].cummax()
        df_data["drawdown"] = (df_data["strategy_return"] - df_data["peak"]) / df_data["peak"]
        return df_data.drawdown.min()
    else:
        return np.nan


def sortino_ratio(data, risk_free_rate=0.01, periods_per_year=252):
    """ 计算Sortino比率

    Args:
        data:
        risk_free_rate:
        periods_per_year:

    Returns:

    """
    daily_returns = data['Strategy Return'].dropna()
    downside_returns = daily_returns[daily_returns < 0]
    expected_return = daily_returns.mean() - risk_free_rate / periods_per_year
    downside_deviation = downside_returns.std()
    if downside_deviation == 0:
        return np.nan
    return expected_return / downside_deviation


def win_rate(data):
    """计算策略的胜率

    Args:
        data: 策略收益的DataFrame

    Returns:
        胜率
    """
    def return_value(row):
        """"""
        start = row["strategy_return"].tolist()[1]
        end = row["strategy_return"].tolist()[-1]
        if end > start:
            return 1
        return 0

    df_data_group = data.copy()
    df_data_group['group'] = (df_data_group['position'].diff() != 0).cumsum()
    df_data_group['group'] = df_data_group['group'].where(df_data_group['position'] == 1)
    df_data_group['group'] = df_data_group['group'].ffill()
    df_data_group = df_data_group[df_data_group.position != 0]
    return df_data_group.groupby("group").apply(return_value, include_groups=False).mean()
