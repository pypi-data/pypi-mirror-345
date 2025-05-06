# QuantStats: Portfolio analytics for quants
# https://github.com/tschm/jquantstats
#
# Copyright 2019-2024 Ran Aroussi
# Copyright 2025 Thomas Schmelzer
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime as _dt
from math import ceil as _ceil
from math import sqrt as _sqrt

import numpy as _np
import pandas as _pd
import pandas as pd
from scipy.stats import linregress as _linregress
from scipy.stats import norm as _norm


def _mtd(df):
    now = _dt.datetime.now()
    return df[(df.index.month == now.month) & (df.index.year == now.year)]


def _qtd(df):
    now = _dt.datetime.now()
    quarter = (now.month - 1) // 3 + 1
    return df[((df.index.month - 1) // 3 + 1 == quarter) & (df.index.year == now.year)]


def _ytd(df):
    now = _dt.datetime.now()
    return df[(df.index.year == now.year)]


def _pandas_date(df, dates: list[pd.Timestamp]):
    # if not isinstance(dates, list):
    #    dates = [dates]
    return df[df.index.isin(dates)]


def _pandas_current_month(df):
    n = _dt.datetime.now()
    daterange = _pd.date_range(_dt.date(n.year, n.month, 1), n)
    return df[df.index.isin(daterange)]


def multi_shift(df, shift=3):
    """Get last N rows relative to another row in pandas"""
    if isinstance(df, _pd.Series):
        df = _pd.DataFrame(df)

    dfs = [df.shift(i) for i in _np.arange(shift)]
    for ix, dfi in enumerate(dfs[1:]):
        dfs[ix + 1].columns = [str(col) for col in dfi.columns + str(ix + 1)]
    return _pd.concat(dfs, axis=1, sort=True)


def log_returns(returns, rf=0.0, nperiods=None):
    """Shorthand for to_log_returns"""
    return to_log_returns(returns, rf, nperiods)


def to_log_returns(returns, rf=0.0, nperiods=None):
    """Converts returns series to log returns"""
    return _np.log(returns + 1).replace([_np.inf, -_np.inf], float("NaN"))


def exponential_stdev(returns, window=30, is_halflife=False):
    """Returns series representing exponential volatility of returns"""
    halflife = window if is_halflife else None
    return returns.ewm(com=None, span=window, halflife=halflife, min_periods=window).std()


# ======== STATS ========


def pct_rank(prices, window=60):
    """Rank prices by window"""
    rank = multi_shift(prices, window).T.rank(pct=True).T
    return rank.iloc[:, 0] * 100.0


def compsum(returns):
    """Calculates rolling compounded returns"""
    return returns.add(1).cumprod(axis=0) - 1


def comp(returns):
    """Calculates total compounded returns"""
    return returns.add(1).prod(axis=0) - 1


def distribution(returns, compounded=True):
    def get_outliers(data):
        # https://datascience.stackexchange.com/a/57199
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1  # IQR is interquartile range.
        filtered = (data >= Q1 - 1.5 * IQR) & (data <= Q3 + 1.5 * IQR)
        return {
            "values": data.loc[filtered].tolist(),
            "outliers": data.loc[~filtered].tolist(),
        }

    # if isinstance(returns, _pd.DataFrame):
    #     _warn("Pandas DataFrame was passed (Series expected). Only first column will be used.")
    #     returns = returns.copy()
    #     returns.columns = map(str.lower, returns.columns)
    #     if len(returns.columns) > 1 and "close" in returns.columns:
    #         returns = returns["close"]
    #     else:
    #         returns = returns[returns.columns[0]]

    apply_fnc = comp if compounded else _np.sum
    daily = returns.dropna()

    return {
        "Daily": get_outliers(daily),
        "Weekly": get_outliers(daily.resample("W-MON").apply(apply_fnc)),
        "Monthly": get_outliers(daily.resample("ME").apply(apply_fnc)),
        "Quarterly": get_outliers(daily.resample("QE").apply(apply_fnc)),
        "Yearly": get_outliers(daily.resample("YE").apply(apply_fnc)),
    }


def expected_return(returns):
    """
    Returns the expected return for a given period
    by calculating the geometric holding period return
    """
    return _np.prod(1 + returns, axis=0) ** (1 / len(returns)) - 1


def geometric_mean(returns):
    """Shorthand for expected_return()"""
    return expected_return(returns)


def ghpr(returns):
    """Shorthand for expected_return()"""
    return expected_return(returns)


def outliers(returns, quantile=0.95):
    """Returns series of outliers"""
    return returns[returns > returns.quantile(quantile)].dropna(how="all")


def remove_outliers(returns, quantile=0.95):
    """Returns series of returns without the outliers"""
    return returns[returns < returns.quantile(quantile)]


def best(returns):
    """Returns the best day/month/week/quarter/year's return"""
    return returns.max()


def worst(returns):
    """Returns the worst day/month/week/quarter/year's return"""
    return returns.min()


def exposure(returns):
    """Returns the market exposure time (returns != 0)"""

    def _exposure(ret):
        ex = len(ret[(~_np.isnan(ret)) & (ret != 0)]) / len(ret)
        return _ceil(ex * 100) / 100

    if isinstance(returns, _pd.DataFrame):
        return returns.apply(_exposure, axis=0)

    return _exposure(returns)


def win_rate(returns):
    """Calculates the win ratio for a period"""

    def _win_rate(series):
        try:
            return len(series[series > 0]) / len(series[series != 0])
        except ZeroDivisionError:
            return 0.0

    if isinstance(returns, _pd.DataFrame):
        _df = {}
        for col in returns.columns:
            _df[col] = _win_rate(returns[col])

        return _pd.Series(_df)

    return _win_rate(returns)


def avg_return(returns):
    """Calculates the average return/trade return for a period"""
    return returns[returns != 0].dropna().mean()


def avg_win(returns):
    """
    Calculates the average winning
    return/trade return for a period
    """
    return returns[returns > 0].dropna().mean()


def avg_loss(returns):
    """
    Calculates the average low if
    return/trade return for a period
    """
    return returns[returns < 0].dropna().mean()


def volatility(returns, periods=252, annualize=True):
    """Calculates the volatility of returns for a period"""
    std = returns.std()
    factor = _np.sqrt(periods) if annualize else 1
    return std * factor


def rolling_volatility(returns, rolling_period=126, periods_per_year=252):
    return returns.rolling(rolling_period).std() * _np.sqrt(periods_per_year)


def implied_volatility(returns, periods=252):
    """Calculates the implied volatility of returns for a period"""
    logret = log_returns(returns)
    factor = periods or 1
    return logret.std() * _np.sqrt(factor)


def autocorr_penalty(returns):
    """Metric to account for auto correlation"""
    if isinstance(returns, _pd.DataFrame):
        returns = returns[returns.columns[0]]

    num = len(returns)
    coef = _np.abs(_np.corrcoef(returns[:-1], returns[1:])[0, 1])
    corr = [((num - x) / num) * coef**x for x in range(1, num)]
    return _np.sqrt(1 + 2 * _np.sum(corr))


# ======= METRICS =======


def sharpe(returns, periods=252, smart=False):
    """
    Calculates the sharpe ratio of access returns

    If rf is non-zero, you must specify periods.
    In this case, rf is assumed to be expressed in yearly (annualized) terms

    Args:
        * returns (Series, DataFrame): Input return series
        * rf (float): Risk-free rate expressed as a yearly (annualized) return
        * periods (int): Freq. of returns (252/365 for daily, 12 for monthly)
        * annualize: return annualize sharpe?
        * smart: return smart sharpe ratio
    """
    divisor = returns.std(ddof=1)
    if smart:
        # penalize sharpe with auto correlation
        divisor = divisor * autocorr_penalty(returns)
    res = returns.mean() / divisor
    factor = periods or 1

    return res * _np.sqrt(factor)


def smart_sharpe(returns, rf=0.0, periods=252):
    return sharpe(returns, rf, periods)


def rolling_sharpe(returns, rolling_period=126, periods_per_year=252):
    res = returns.rolling(rolling_period).mean() / returns.rolling(rolling_period).std()
    factor = periods_per_year or 1
    return res * _np.sqrt(factor)


def sortino(returns, periods=252, smart=False):
    """
    Calculates the sortino ratio of access returns

    If rf is non-zero, you must specify periods.
    In this case, rf is assumed to be expressed in yearly (annualized) terms

    Calculation is based on this paper by Red Rock Capital
    http://www.redrockcapital.com/Sortino__A__Sharper__Ratio_Red_Rock_Capital.pdf
    """
    downside = _np.sqrt((returns[returns < 0] ** 2).sum() / len(returns))

    if smart:
        # penalize sortino with auto correlation
        downside = downside * autocorr_penalty(returns)

    res = returns.mean() / downside
    factor = periods or 1
    return res * _np.sqrt(factor)


def smart_sortino(returns, periods=252):
    return sortino(returns, periods=periods, smart=True)


def rolling_sortino(returns, rolling_period=126, periods_per_year=252):
    downside = returns.rolling(rolling_period).apply(lambda x: (x.values[x.values < 0] ** 2).sum()) / rolling_period

    res = returns.rolling(rolling_period).mean() / _np.sqrt(downside)
    factor = periods_per_year or 1
    return res * _np.sqrt(factor)


def adjusted_sortino(returns, periods=252, smart=False):
    """
    Jack Schwager's version of the Sortino ratio allows for
    direct comparisons to the Sharpe. See here for more info:
    https://archive.is/wip/2rwFW
    """
    data = sortino(returns, periods=periods, smart=smart)
    return data / _sqrt(2)


def probabilistic_ratio(returns, base="sharpe", periods=252, smart=False):
    if base.lower() == "sharpe":
        base = sharpe(returns, periods=periods, smart=smart)
    elif base.lower() == "sortino":
        base = sortino(returns, periods=periods, smart=smart)
    elif base.lower() == "adjusted_sortino":
        base = adjusted_sortino(returns, periods=periods, smart=smart)
    else:
        raise Exception("`metric` must be either `sharpe`, `sortino`, or `adjusted_sortino`")

    skew_no = skew(returns)
    kurtosis_no = kurtosis(returns)

    n = len(returns)

    sigma_sr = _np.sqrt((1 + (0.5 * base**2) - (skew_no * base) + (((kurtosis_no - 3) / 4) * base**2)) / (n - 1))

    ratio = base / sigma_sr
    psr = _norm.cdf(ratio)

    factor = periods or 1
    return psr * _np.sqrt(factor)


def probabilistic_sharpe_ratio(returns, periods=252, smart=False):
    return probabilistic_ratio(returns, base="sharpe", periods=periods, smart=smart)


def probabilistic_sortino_ratio(returns, periods=252, smart=False):
    return probabilistic_ratio(returns, base="sortino", periods=periods, smart=smart)


def probabilistic_adjusted_sortino_ratio(returns, periods=252, smart=False):
    return probabilistic_ratio(
        returns,
        base="adjusted_sortino",
        periods=periods,
        smart=smart,
    )


def gain_to_pain_ratio(returns, resolution="D"):
    """
    Jack Schwager's GPR. See here for more info:
    https://archive.is/wip/2rwFW
    """
    returns = returns.resample(resolution).sum()
    downside = abs(returns[returns < 0].sum())
    return returns.sum() / downside


def skew(returns):
    """
    Calculates returns' skewness
    (the degree of asymmetry of a distribution around its mean)
    """
    return returns.skew()


def kurtosis(returns):
    """
    Calculates returns' kurtosis
    (the degree to which a distribution peak compared to a normal distribution)
    """
    return returns.kurtosis()


def risk_of_ruin(returns):
    """
    Calculates the risk of ruin
    (the likelihood of losing all one's investment capital)
    """
    wins = win_rate(returns)
    return ((1 - wins) / (1 + wins)) ** len(returns)


def ror(returns):
    """Shorthand for risk_of_ruin()"""
    return risk_of_ruin(returns)


def value_at_risk(returns, sigma=1, confidence=0.95):
    """
    Calculats the daily value-at-risk
    (variance-covariance calculation with confidence n)
    """
    mu = returns.mean()
    sigma *= returns.std()

    return _norm.ppf(1 - confidence, mu, sigma)


def var(returns, sigma=1, confidence=0.95):
    """Shorthand for value_at_risk()"""
    return value_at_risk(returns, sigma, confidence)


def conditional_value_at_risk(returns, sigma=1, confidence=0.95):
    """
    Calculats the conditional daily value-at-risk (aka expected shortfall)
    quantifies the amount of tail risk an investment
    """
    var = value_at_risk(returns, sigma, confidence)
    c_var = returns[returns < var].values.mean()
    return c_var if ~_np.isnan(c_var) else var


def cvar(returns, sigma=1, confidence=0.95):
    """Shorthand for conditional_value_at_risk()"""
    return conditional_value_at_risk(returns, sigma, confidence)


def expected_shortfall(returns, sigma=1, confidence=0.95):
    """Shorthand for conditional_value_at_risk()"""
    return conditional_value_at_risk(returns, sigma, confidence)


def tail_ratio(returns, cutoff=0.95):
    """
    Measures the ratio between the right
    (95%) and left tail (5%).
    """
    return abs(returns.quantile(cutoff) / returns.quantile(1 - cutoff))


def payoff_ratio(returns):
    """Measures the payoff ratio (average win/average loss)"""
    return avg_win(returns) / abs(avg_loss(returns))


def win_loss_ratio(returns):
    """Shorthand for payoff_ratio()"""
    return payoff_ratio(returns)


def profit_ratio(returns):
    """Measures the profit ratio (win ratio / loss ratio)"""
    wins = returns[returns >= 0]
    loss = returns[returns < 0]

    win_ratio = abs(wins.mean() / wins.count())
    loss_ratio = abs(loss.mean() / loss.count())
    return win_ratio / loss_ratio


def profit_factor(returns):
    """Measures the profit ratio (wins/loss)"""
    return abs(returns[returns >= 0].sum() / returns[returns < 0].sum())


def cpc_index(returns):
    """
    Measures the cpc ratio
    (profit factor * win % * win loss ratio)
    """
    return profit_factor(returns) * win_rate(returns) * win_loss_ratio(returns)


def common_sense_ratio(returns):
    """Measures the common sense ratio (profit factor * tail ratio)"""
    return profit_factor(returns) * tail_ratio(returns)


def outlier_win_ratio(returns, quantile=0.99):
    """
    Calculates the outlier winners ratio
    99th percentile of returns / mean positive return
    """
    return returns.quantile(quantile).mean() / returns[returns >= 0].mean()


def outlier_loss_ratio(returns, quantile=0.01):
    """
    Calculates the outlier losers ratio
    1st percentile of returns / mean negative return
    """
    return returns.quantile(quantile).mean() / returns[returns < 0].mean()


def recovery_factor(returns, rf=0.0):
    """Measures how fast the strategy recovers from drawdowns"""
    total_returns = returns.sum() - rf
    max_dd = max_drawdown(returns)
    return abs(total_returns) / abs(max_dd)


def risk_return_ratio(returns):
    """
    Calculates the return / risk ratio
    (sharpe ratio without factoring in the risk-free rate)
    """
    return returns.mean() / returns.std()


def max_drawdown(prices):
    """Calculates the maximum drawdown"""
    return prices / prices.cummax().min() - 1


def drawdown_details(drawdown):
    """
    Calculates drawdown details, including start/end/valley dates,
    duration, max drawdown and max dd for 99% of the dd period
    for every drawdown period
    """

    def _drawdown_details(drawdown):
        # mark no drawdown
        no_dd = drawdown == 0

        # extract dd start dates, first date of the drawdown
        starts = ~no_dd & no_dd.shift(1)
        starts = list(starts[starts.values].index)

        # extract end dates, last date of the drawdown
        ends = no_dd & (~no_dd).shift(1)
        ends = ends.shift(-1, fill_value=False)
        ends = list(ends[ends.values].index)

        # no drawdown :)
        if not starts:
            return _pd.DataFrame(
                index=[],
                columns=(
                    "start",
                    "valley",
                    "end",
                    "days",
                    "max drawdown",
                    "99% max drawdown",
                ),
            )

        # drawdown series begins in a drawdown
        if ends and starts[0] > ends[0]:
            starts.insert(0, drawdown.index[0])

        # series ends in a drawdown fill with last date
        if not ends or starts[-1] > ends[-1]:
            ends.append(drawdown.index[-1])

        # build dataframe from results
        data = []
        for i, _ in enumerate(starts):
            dd = drawdown[starts[i] : ends[i]]
            clean_dd = -remove_outliers(-dd, 0.99)
            data.append(
                (
                    starts[i],
                    dd.idxmin(),
                    ends[i],
                    (ends[i] - starts[i]).days + 1,
                    dd.min() * 100,
                    clean_dd.min() * 100,
                )
            )

        df = _pd.DataFrame(
            data=data,
            columns=(
                "start",
                "valley",
                "end",
                "days",
                "max drawdown",
                "99% max drawdown",
            ),
        )
        df["days"] = df["days"].astype(int)
        df["max drawdown"] = df["max drawdown"].astype(float)
        df["99% max drawdown"] = df["99% max drawdown"].astype(float)

        df["start"] = df["start"].dt.strftime("%Y-%m-%d")
        df["end"] = df["end"].dt.strftime("%Y-%m-%d")
        df["valley"] = df["valley"].dt.strftime("%Y-%m-%d")

        return df

    if isinstance(drawdown, _pd.DataFrame):
        drawdown.apply(_drawdown_details, axis=0)
        _dfs = {}
        for col in drawdown.columns:
            _dfs[col] = _drawdown_details(drawdown[col])
        return _pd.concat(_dfs, axis=1)

    return _drawdown_details(drawdown)


def kelly_criterion(returns):
    """
    Calculates the recommended maximum amount of capital that
    should be allocated to the given strategy, based on the
    Kelly Criterion (http://en.wikipedia.org/wiki/Kelly_criterion)
    """
    win_loss_ratio = payoff_ratio(returns)
    win_prob = win_rate(returns)
    lose_prob = 1 - win_prob

    return ((win_loss_ratio * win_prob) - lose_prob) / win_loss_ratio


# ==== VS. BENCHMARK ====


def r_squared(returns, benchmark):
    """Measures the straight line fit of the equity curve"""
    # slope, intercept, r_val, p_val, std_err = _linregress(
    _, _, r_val, _, _ = _linregress(returns, benchmark)
    return r_val**2


def r2(returns, benchmark):
    """Shorthand for r_squared()"""
    return r_squared(returns, benchmark)


def information_ratio(returns, benchmark):
    """
    Calculates the information ratio
    (basically the risk return ratio of the net profits)
    """
    return (returns - benchmark).mean() / returns.std()


def greeks(returns, benchmark, periods=252.0):
    """Calculates alpha and beta of the portfolio"""
    # find covariance
    if not isinstance(returns, _pd.Series):
        returns = returns[returns.columns[0]]

    matrix = _np.cov(returns, benchmark)
    beta = matrix[0, 1] / matrix[1, 1]

    # calculates measures now
    alpha = returns.mean() - beta * benchmark.mean()
    alpha = alpha * periods

    return _pd.Series(
        {
            "beta": beta,
            "alpha": alpha,
            # "vol": _np.sqrt(matrix[0, 0]) * _np.sqrt(periods)
        }
    ).fillna(0)
