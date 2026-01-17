"""
Signal generation for mean-reversion pairs trading.
"""
import pandas as pd
import numpy as np


def compute_zscore(
    spread: pd.Series,
    lookback: int = 60
) -> pd.DataFrame:
    """
    Compute rolling z-score of spread.
    
    Parameters
    ----------
    spread : pd.Series
        Spread time series
    lookback : int
        Rolling window for mean and std
    
    Returns
    -------
    pd.DataFrame
        Columns: spread, spread_mean, spread_std, z
    """
    df = pd.DataFrame(index=spread.index)
    df["spread"] = spread
    df["spread_mean"] = spread.rolling(lookback).mean()
    df["spread_std"] = spread.rolling(lookback).std()
    df["z"] = (spread - df["spread_mean"]) / df["spread_std"]
    
    return df.dropna()


def generate_positions(
    z: pd.Series,
    entry_threshold: float = 2.0,
    exit_threshold: float = 0.5,
    stop_threshold: float = 4.0,
    max_holding_days: int = 20
) -> pd.Series:
    """
    Generate positions from z-score with entry/exit/stop rules.
    
    Logic:
    - Enter long spread when z < -entry_threshold
    - Enter short spread when z > +entry_threshold
    - Exit when abs(z) < exit_threshold
    - Stop when abs(z) > stop_threshold
    - Force exit after max_holding_days
    
    Position encoding:
    +1 = long spread (long Y, short beta*X)
    -1 = short spread (short Y, long beta*X)
     0 = flat
    
    Parameters
    ----------
    z : pd.Series
        Z-score time series
    entry_threshold : float
        Absolute z-score to enter trade
    exit_threshold : float
        Absolute z-score to exit trade
    stop_threshold : float
        Absolute z-score to stop out
    max_holding_days : int
        Maximum days to hold position
    
    Returns
    -------
    pd.Series
        Position series (-1, 0, +1)
    """
    position = pd.Series(0, index=z.index)
    current_pos = 0
    days_held = 0
    
    for i in range(len(z)):
        z_val = z.iloc[i]
        
        # Update holding period counter
        if current_pos != 0:
            days_held += 1
        else:
            days_held = 0
        
        # Check stops and exits first
        if current_pos != 0:
            # Stop loss
            if abs(z_val) > stop_threshold:
                current_pos = 0
                days_held = 0
            # Normal exit
            elif abs(z_val) < exit_threshold:
                current_pos = 0
                days_held = 0
            # Max holding period
            elif days_held >= max_holding_days:
                current_pos = 0
                days_held = 0
        
        # Check entries (only if flat)
        if current_pos == 0:
            if z_val < -entry_threshold:
                current_pos = 1  # long spread
            elif z_val > entry_threshold:
                current_pos = -1  # short spread
        
        position.iloc[i] = current_pos
    
    return position


def position_to_trades(position: pd.Series) -> pd.DataFrame:
    """
    Convert position series to trade log.
    
    Parameters
    ----------
    position : pd.Series
        Position time series
    
    Returns
    -------
    pd.DataFrame
        Trade log with entry/exit dates and direction
    """
    trades = []
    position_changes = position.diff().fillna(0)
    
    entry_idx = None
    entry_pos = None
    
    for i in range(len(position)):
        if position_changes.iloc[i] != 0:
            # Position change occurred
            if position.iloc[i] != 0 and entry_idx is None:
                # Trade entry
                entry_idx = i
                entry_pos = position.iloc[i]
            elif position.iloc[i] == 0 and entry_idx is not None:
                # Trade exit
                trades.append({
                    "entry_date": position.index[entry_idx],
                    "exit_date": position.index[i],
                    "direction": "long" if entry_pos > 0 else "short",
                    "holding_days": i - entry_idx
                })
                entry_idx = None
                entry_pos = None
    
    return pd.DataFrame(trades)
