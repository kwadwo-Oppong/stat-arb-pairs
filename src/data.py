"""
Data loading and preprocessing utilities for pairs trading.
"""
import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Optional


def load_prices_yf(
    tickers: List[str],
    start: str = "2014-01-01",
    end: Optional[str] = None
) -> pd.DataFrame:
    """
    Load adjusted close prices from Yahoo Finance.
    
    Parameters
    ----------
    tickers : list of str
        Ticker symbols to download
    start : str
        Start date in YYYY-MM-DD format
    end : str or None
        End date in YYYY-MM-DD format (None = today)
    
    Returns
    -------
    pd.DataFrame
        DataFrame with adjusted close prices, aligned dates
    """
    px = yf.download(
        tickers,
        start=start,
        end=end,
        auto_adjust=False,
        progress=False
    )["Adj Close"]
    
    # Handle single ticker case
    if len(tickers) == 1:
        px = px.to_frame()
        px.columns = tickers
    
    # Clean: drop any rows with missing data
    px = px.dropna()
    
    return px


def compute_log_prices_and_returns(px: pd.DataFrame) -> pd.DataFrame:
    """
    Convert prices to log prices and returns.
    
    Parameters
    ----------
    px : pd.DataFrame
        DataFrame with price columns
    
    Returns
    -------
    pd.DataFrame
        Original prices plus log prices and returns
    """
    df = px.copy()
    
    for col in px.columns:
        df[f"log_{col}"] = np.log(df[col])
        df[f"ret_{col}"] = df[f"log_{col}"].diff()
    
    # Drop first row (NaN returns)
    df = df.dropna()
    
    return df


def train_test_split_time(
    df: pd.DataFrame,
    train_frac: float = 0.7
) -> tuple:
    """
    Split data by time (preserves temporal order).
    
    Parameters
    ----------
    df : pd.DataFrame
        Time series data
    train_frac : float
        Fraction of data for training (0 to 1)
    
    Returns
    -------
    tuple of (train_df, test_df)
    """
    split_idx = int(len(df) * train_frac)
    train = df.iloc[:split_idx]
    test = df.iloc[split_idx:]
    
    return train, test
