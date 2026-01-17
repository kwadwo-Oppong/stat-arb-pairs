"""
Standalone performance metrics functions.
"""
import pandas as pd
import numpy as np


def sharpe_ratio(returns: pd.Series, periods_per_year: int = 252) -> float:
    """
    Compute annualized Sharpe ratio.
    
    Parameters
    ----------
    returns : pd.Series
        Period returns (e.g., daily)
    periods_per_year : int
        Periods per year (252 for daily, 12 for monthly)
    
    Returns
    -------
    float
        Annualized Sharpe ratio
    """
    mean_ret = returns.mean()
    std_ret = returns.std()
    
    if std_ret == 0:
        return 0.0
    
    sharpe = (mean_ret / std_ret) * np.sqrt(periods_per_year)
    return sharpe


def max_drawdown(equity: pd.Series) -> float:
    """
    Compute maximum drawdown.
    
    Parameters
    ----------
    equity : pd.Series
        Equity curve
    
    Returns
    -------
    float
        Maximum drawdown (negative value)
    """
    running_max = equity.expanding().max()
    drawdown = (equity - running_max) / running_max
    return drawdown.min()


def cagr(equity: pd.Series, periods_per_year: int = 252) -> float:
    """
    Compute Compound Annual Growth Rate.
    
    Parameters
    ----------
    equity : pd.Series
        Equity curve (starting at 1.0)
    periods_per_year : int
        Trading periods per year
    
    Returns
    -------
    float
        CAGR
    """
    n_periods = len(equity)
    n_years = n_periods / periods_per_year
    
    if n_years == 0:
        return 0.0
    
    total_return = equity.iloc[-1] / equity.iloc[0]
    cagr_val = (total_return ** (1 / n_years)) - 1
    
    return cagr_val


def hit_rate(trades_df: pd.DataFrame, pnl_col: str = "pnl") -> float:
    """
    Compute win rate from trades.
    
    Parameters
    ----------
    trades_df : pd.DataFrame
        Trade log with PnL column
    pnl_col : str
        Column name for trade PnL
    
    Returns
    -------
    float
        Win rate (0 to 1)
    """
    if len(trades_df) == 0:
        return 0.0
    
    winners = (trades_df[pnl_col] > 0).sum()
    return winners / len(trades_df)


def turnover(position: pd.Series) -> float:
    """
    Compute average daily turnover.
    
    Parameters
    ----------
    position : pd.Series
        Position time series
    
    Returns
    -------
    float
        Average absolute position change per period
    """
    return position.diff().abs().mean()


def sortino_ratio(
    returns: pd.Series,
    periods_per_year: int = 252,
    target_return: float = 0.0
) -> float:
    """
    Compute annualized Sortino ratio (downside deviation).
    
    Parameters
    ----------
    returns : pd.Series
        Period returns
    periods_per_year : int
        Periods per year for annualization
    target_return : float
        Minimum acceptable return (default 0)
    
    Returns
    -------
    float
        Annualized Sortino ratio
    """
    excess = returns - target_return
    downside = excess[excess < 0]
    
    if len(downside) == 0:
        return 0.0
    
    downside_std = downside.std()
    
    if downside_std == 0:
        return 0.0
    
    sortino = (returns.mean() / downside_std) * np.sqrt(periods_per_year)
    return sortino


def calmar_ratio(equity: pd.Series, periods_per_year: int = 252) -> float:
    """
    Compute Calmar ratio (CAGR / abs(max drawdown)).
    
    Parameters
    ----------
    equity : pd.Series
        Equity curve
    periods_per_year : int
        Periods per year
    
    Returns
    -------
    float
        Calmar ratio
    """
    cagr_val = cagr(equity, periods_per_year)
    max_dd = abs(max_drawdown(equity))
    
    if max_dd == 0:
        return 0.0
    
    return cagr_val / max_dd
