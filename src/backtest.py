"""
Backtesting engine for pairs trading strategies.
"""
import pandas as pd
import numpy as np


def backtest_pairs_strategy(
    ret_y: pd.Series,
    ret_x: pd.Series,
    position: pd.Series,
    beta: float,
    cost_bps: float = 5.0
) -> pd.DataFrame:
    """
    Backtest pairs trading strategy with transaction costs.
    
    Position interpretation:
    +1 = long spread = long Y, short beta*X
    -1 = short spread = short Y, long beta*X
    
    Parameters
    ----------
    ret_y : pd.Series
        Returns of asset Y (KO)
    ret_x : pd.Series
        Returns of asset X (PEP)
    position : pd.Series
        Position series (-1, 0, +1)
    beta : float
        Hedge ratio (from cointegration regression)
    cost_bps : float
        Transaction cost in basis points per leg
    
    Returns
    -------
    pd.DataFrame
        Columns: position, strat_ret, costs, net_ret, equity
    """
    df = pd.DataFrame(index=position.index)
    df["position"] = position
    df["ret_y"] = ret_y
    df["ret_x"] = ret_x
    
    # Strategy return (before costs)
    # Long spread: +1 * ret_y - beta * ret_x
    # Short spread: -1 * ret_y + beta * ret_x
    df["strat_ret"] = position * (ret_y - beta * ret_x)
    
    # Transaction costs (applied when position changes)
    position_change = position.diff().fillna(0).abs()
    
    # Cost = (bps / 10000) * position_change * (1 + beta) legs
    # Factor (1 + beta) accounts for both legs
    df["costs"] = (cost_bps / 10000) * position_change * (1 + abs(beta))
    
    # Net return
    df["net_ret"] = df["strat_ret"] - df["costs"]
    
    # Equity curve (starting at 1.0)
    df["equity"] = (1 + df["net_ret"]).cumprod()
    
    return df


def compute_drawdown(equity: pd.Series) -> pd.Series:
    """
    Compute drawdown series from equity curve.
    
    Parameters
    ----------
    equity : pd.Series
        Equity curve
    
    Returns
    -------
    pd.Series
        Drawdown (as negative percentage)
    """
    running_max = equity.expanding().max()
    drawdown = (equity - running_max) / running_max
    return drawdown


def backtest_summary_stats(
    df: pd.DataFrame,
    trades: pd.DataFrame = None
) -> dict:
    """
    Compute summary statistics from backtest results.
    
    Parameters
    ----------
    df : pd.DataFrame
        Backtest output (must have net_ret, equity, position)
    trades : pd.DataFrame, optional
        Trade log from position_to_trades
    
    Returns
    -------
    dict
        Performance metrics
    """
    returns = df["net_ret"]
    equity = df["equity"]
    position = df["position"]
    
    # Annualization factor (assume daily data, 252 trading days)
    n_days = len(returns)
    n_years = n_days / 252
    
    # Total return
    total_ret = equity.iloc[-1] - 1
    
    # CAGR
    cagr = (equity.iloc[-1] ** (1 / n_years)) - 1 if n_years > 0 else 0
    
    # Annualized Sharpe
    mean_ret = returns.mean()
    std_ret = returns.std()
    sharpe = (mean_ret / std_ret) * np.sqrt(252) if std_ret > 0 else 0
    
    # Max drawdown
    dd = compute_drawdown(equity)
    max_dd = dd.min()
    
    # Turnover (average absolute position change per day)
    turnover = position.diff().abs().sum() / n_days
    
    # Hit rate (if trades provided)
    hit_rate = None
    avg_holding = None
    n_trades = None
    
    if trades is not None and len(trades) > 0:
        # Compute PnL per trade (approximate)
        n_trades = len(trades)
        avg_holding = trades["holding_days"].mean()
        # For hit rate, need to compute per-trade returns (simplified here)
    
    return {
        "total_return": total_ret,
        "cagr": cagr,
        "sharpe": sharpe,
        "max_drawdown": max_dd,
        "mean_daily_ret": mean_ret,
        "vol_daily_ret": std_ret,
        "turnover": turnover,
        "n_trades": n_trades,
        "avg_holding_days": avg_holding
    }
