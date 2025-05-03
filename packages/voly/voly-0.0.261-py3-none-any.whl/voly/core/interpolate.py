"""
Model interpolation module for the Voly package.

This module handles interpolating volatility model parameters across different
days to expiry, allowing for consistent volatility surfaces at arbitrary tenors.
"""

import pandas as pd
import numpy as np
import datetime as dt
from typing import List, Dict, Tuple, Optional, Union, Any
from scipy import interpolate
from voly.utils.logger import logger, catch_exception
from voly.exceptions import VolyError


@catch_exception
def interpolate_model(fit_results: pd.DataFrame,
                      list_of_days: List[str] = ['7d', '30d', '90d', '150d', '240d'],
                      method: str = 'cubic') -> pd.DataFrame:
    """
    Interpolate model parameters across different days to expiry.

    Parameters:
    - fit_results: DataFrame with model fitting results, indexed by maturity names
    - list_of_days: list of specific days to interpolate to (e.g., ['7d', '30d', '90d'])
    - method: Interpolation method ('linear', 'cubic', 'pchip', etc.)

    Returns:
    - DataFrame with interpolated model parameters for the specified days
    """

    # Check if fit_results is valid
    if fit_results is None or fit_results.empty:
        raise VolyError("Fit results DataFrame is empty or None")

    # Extract years to maturity from fit_results
    original_ytms = fit_results['t'].values

    if len(original_ytms) < 2:
        raise VolyError("Need at least two maturities in fit_results to interpolate")

    # Sort original years to maturity for proper interpolation
    sorted_indices = np.argsort(original_ytms)
    original_ytms = original_ytms[sorted_indices]

    # Parse days from strings like '7d', '30d', etc.
    target_days = []
    for day_str in list_of_days:
        if not day_str.endswith('d'):
            raise VolyError(f"Invalid day format: {day_str}. Expected format: '7d', '30d', etc.")
        try:
            days = int(day_str[:-1])
            target_days.append(days)
        except ValueError:
            raise VolyError(f"Invalid day value: {day_str}. Expected format: '7d', '30d', etc.")

    # Convert target days to years for interpolation (to match original implementation)
    target_years = [day / 365.25 for day in target_days]

    # Check if target years are within the range of original years
    min_original, max_original = np.min(original_ytms), np.max(original_ytms)
    for years in target_years:
        if years < min_original or years > max_original:
            logger.warning(
                f"Target time {years:.4f} years is outside the range of original data [{min_original:.4f}, {max_original:.4f}]. "
                "Extrapolation may give unreliable results.")

    # Columns to interpolate
    param_columns = ['a', 'b', 'm', 'rho', 'sigma', 'nu', 'psi', 'p', 'c', 'nu_tilde']

    # Create empty DataFrame for interpolated results
    interpolated_df = pd.DataFrame(index=[f"{day}d" for day in target_days])

    # Generate YTM and maturity dates for interpolated results
    interpolated_df['t'] = target_years

    # Calculate maturity dates
    now = dt.datetime.now()
    expiries = []
    for days in target_days:
        expiry = now + dt.timedelta(days=days)
        expiries.append(expiry)

    interpolated_df['expiry'] = expiries

    # Sort fit_results by ytm
    sorted_fit_results = fit_results.iloc[sorted_indices]
    recent_row = sorted_fit_results.iloc[-1]
    interpolated_df['s'] = recent_row['s']
    interpolated_df['r'] = recent_row['r']

    # Interpolate model parameters
    for param in param_columns:
        if param in fit_results.columns:
            try:
                # Create interpolation function using years to expiry
                f = interpolate.interp1d(
                    original_ytms,
                    sorted_fit_results[param].values,
                    kind=method,
                    bounds_error=False,
                    fill_value='extrapolate'
                )

                # Apply interpolation with target years
                interpolated_df[param] = f(target_years)
            except Exception as e:
                logger.error(f"Error interpolating parameter {param}: {str(e)}")
                # Fallback to nearest neighbor if sophisticated method fails
                f = interpolate.interp1d(
                    original_ytms,
                    sorted_fit_results[param].values,
                    kind='nearest',
                    bounds_error=False,
                    fill_value=(sorted_fit_results[param].iloc[0], sorted_fit_results[param].iloc[-1])
                )
                interpolated_df[param] = f(target_years)

    # Ensure consistent ordering of columns with expected structure
    expected_columns = ['s', 't', 'r', 'expiry', 'a', 'b', 'm', 'rho', 'sigma',
                        'nu', 'psi', 'p', 'c', 'nu_tilde']

    # Create final column order based on available columns
    column_order = [col for col in expected_columns if col in interpolated_df.columns]
    interpolated_df = interpolated_df[column_order]

    logger.info(f"Successfully interpolated model parameters for {len(target_days)} target days")

    return interpolated_df
