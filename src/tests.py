"""
Statistical tests for cointegration (Engle-Granger method).
"""
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from typing import Tuple


def engle_granger(
    log_y: pd.Series,
    log_x: pd.Series
) -> dict:
    """
    Engle-Granger two-step cointegration test.
    
    Step 1: Regress log_y on log_x
    Step 2: Test residuals (spread) for stationarity using ADF
    
    Parameters
    ----------
    log_y : pd.Series
        Log prices of asset Y (dependent)
    log_x : pd.Series
        Log prices of asset X (independent)
    
    Returns
    -------
    dict with keys:
        alpha : float (intercept)
        beta : float (hedge ratio)
        spread : pd.Series (residuals)
        adf_stat : float
        adf_pval : float
        is_cointegrated : bool (p-value < 0.05)
    """
    # Step 1: OLS regression
    x_with_const = sm.add_constant(log_x)
    model = sm.OLS(log_y, x_with_const).fit()
    
    alpha = model.params["const"]
    beta = model.params[log_x.name]
    
    # Step 2: Compute spread (residuals)
    spread = log_y - (alpha + beta * log_x)
    spread.name = "spread"
    
    # Step 3: ADF test on spread
    adf_result = adfuller(spread, maxlag=1, regression="c")
    adf_stat = adf_result[0]
    adf_pval = adf_result[1]
    
    return {
        "alpha": alpha,
        "beta": beta,
        "spread": spread,
        "adf_stat": adf_stat,
        "adf_pval": adf_pval,
        "is_cointegrated": adf_pval < 0.05
    }


def rolling_beta(
    log_y: pd.Series,
    log_x: pd.Series,
    window: int = 252
) -> pd.Series:
    """
    Estimate hedge ratio (beta) on rolling windows.
    
    Useful for checking parameter stability over time.
    
    Parameters
    ----------
    log_y : pd.Series
        Log prices of asset Y
    log_x : pd.Series
        Log prices of asset X
    window : int
        Rolling window size in days
    
    Returns
    -------
    pd.Series
        Rolling beta estimates
    """
    betas = []
    idx = log_y.index[window:]
    
    for i in range(window, len(log_y)):
        y_window = log_y.iloc[i - window:i]
        x_window = sm.add_constant(log_x.iloc[i - window:i])
        
        model = sm.OLS(y_window, x_window).fit()
        betas.append(model.params[log_x.name])
    
    return pd.Series(betas, index=idx, name="rolling_beta")


def adf_test_summary(series: pd.Series) -> dict:
    """
    Run ADF test and return summary dict.
    
    Parameters
    ----------
    series : pd.Series
        Time series to test for stationarity
    
    Returns
    -------
    dict with ADF statistics
    """
    result = adfuller(series, maxlag=1, regression="c")
    
    return {
        "adf_stat": result[0],
        "pval": result[1],
        "critical_1%": result[4]["1%"],
        "critical_5%": result[4]["5%"],
        "is_stationary": result[1] < 0.05
    }
