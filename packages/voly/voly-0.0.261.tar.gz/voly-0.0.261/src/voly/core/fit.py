"""
Model fitting and calibration module for the Voly package.

This module handles fitting volatility models to market data, calculating fitting statistics,
and generating visualizations.
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Optional, Union, Any
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from voly.utils.logger import logger, catch_exception
from voly.formulas import get_domain
from voly.exceptions import VolyError
from voly.models import SVIModel
from concurrent.futures import ThreadPoolExecutor
import warnings
import time

warnings.filterwarnings("ignore")


class SVICalibrator:
    """Handles the SVI calibration process"""

    def __init__(self, option_chain, currency, num_points=2000):
        self.option_chain = option_chain
        self.currency = currency
        self.s = option_chain['spot_price'].iloc[0]
        self.r = option_chain['interest_rate'].iloc[0] if 'interest_rate' in option_chain else 0.0
        self.groups = option_chain.groupby('expiry')
        self.params_dict = {}
        self.results_data = {}
        self.num_points = num_points

        # Initialize results data template
        self.field_names = [
            's', 't', 'r', 'expiry', 'maturity', 'a', 'b', 'm', 'rho', 'sigma',
            'nu', 'psi', 'p', 'c', 'nu_tilde', 'log_min_strike', 'usd_min_strike',
            'fit_success', 'butterfly_arbitrage_free', 'calendar_arbitrage_free',
            'rmse', 'mae', 'r2', 'max_error', 'loss', 'n_points'
        ]

        # Create empty lists for each field
        for field in self.field_names:
            self.results_data[field] = []

    def failed_calibration(self, expiry, maturity, t, n_points):
        """Create an empty result for failed calibration"""
        return {
            's': float(self.s),
            't': float(t),
            'r': float(self.r),
            'expiry': expiry,
            'maturity': maturity,
            'fit_success': False,
            'calendar_arbitrage_free': True,  # Updated later
            'loss': float(np.inf),
            'n_points': int(n_points),
            'a': np.nan, 'b': np.nan, 'm': np.nan, 'rho': np.nan, 'sigma': np.nan,
            'nu': np.nan, 'psi': np.nan, 'p': np.nan, 'c': np.nan, 'nu_tilde': np.nan,
            'log_min_strike': np.nan, 'usd_min_strike': np.nan,
            'butterfly_arbitrage_free': False,
            'rmse': np.nan, 'mae': np.nan, 'r2': np.nan, 'max_error': np.nan
        }

    def filter_market_data(self, group):
        """Filter and prepare market data"""
        # Filter for call options only
        group = group[group['flag'] == 'C']
        group['log_moneyness'] = np.log(group['strikes'] / group['spot_price'].iloc[0])

        # Handle duplicated IVs by keeping the row closest to log_moneyness=0
        duplicated_iv = group[group.duplicated('mark_iv', keep=False)]
        if not duplicated_iv.empty:
            cleaned_dupes = duplicated_iv.groupby('mark_iv').apply(
                lambda g: g.loc[[g['log_moneyness'].abs().idxmin()]]
            ).reset_index(drop=True)

            # Combine cleaned duplicates with unique rows
            unique_iv = group.drop_duplicates('mark_iv', keep=False)
            group = pd.concat([unique_iv, cleaned_dupes])

        # Extract basic data
        maturity = group['maturity'].iloc[0]
        t = group['t'].iloc[0]
        K = group['strikes'].values
        iv = group['mark_iv'].values
        vega = group['vega'].values if 'vega' in group.columns else np.ones_like(iv)
        k = np.log(K / self.s)

        # Filter out invalid data
        w = (iv ** 2) * t
        mask = ~np.isnan(w) & ~np.isnan(vega) & ~np.isnan(k) & (iv >= 0)
        k, w, vega, iv, K = k[mask], w[mask], vega[mask], iv[mask], K[mask]

        return maturity, t, k, w, vega, iv, K

    def calculate_model_stats(self, params, t, k, iv):
        """Calculate all model statistics from parameters"""
        a, b, m, rho, sigma = params
        a_scaled, b_scaled = a * t, b * t

        # Jump-Wing parameters
        jw_params = SVIModel.raw_to_jw_params(a_scaled, b_scaled, m, rho, sigma, t)

        # Fit statistics
        w_model = np.array([SVIModel.svi(x, a_scaled, b_scaled, m, rho, sigma) for x in k])
        iv_model = np.sqrt(w_model / t)
        rmse = np.sqrt(mean_squared_error(iv, iv_model))
        mae = mean_absolute_error(iv, iv_model)
        r2 = r2_score(iv, iv_model)
        max_error = np.max(np.abs(iv - iv_model))

        # Minimum strike
        log_min_strike = SVIModel.svi_min_strike(sigma, rho, m)
        usd_min_strike = np.exp(log_min_strike) * self.s

        # Butterfly arbitrage check
        k_range = np.linspace(min(k), max(k), self.num_points)
        butterfly_arbitrage_free = SVIModel.check_butterfly_arbitrage(a_scaled, b_scaled, m, rho, sigma, k_range)

        return {
            'a': float(a_scaled),
            'b': float(b_scaled),
            'm': float(m),
            'rho': float(rho),
            'sigma': float(sigma),
            'nu': float(jw_params[0]),
            'psi': float(jw_params[1]),
            'p': float(jw_params[2]),
            'c': float(jw_params[3]),
            'nu_tilde': float(jw_params[4]),
            'log_min_strike': float(log_min_strike),
            'usd_min_strike': float(usd_min_strike),
            'butterfly_arbitrage_free': butterfly_arbitrage_free,
            'rmse': float(rmse),
            'mae': float(mae),
            'r2': float(r2),
            'max_error': float(max_error)
        }

    def process_maturity(self, expiry, group):
        """Process single maturity for SVI calibration"""
        # Clean and prepare market data
        maturity, t, k, w, vega, iv, K = self.filter_market_data(group)

        # Not enough data points for fitting
        if len(k) <= 5:
            result = self.failed_calibration(expiry, maturity, t, len(k))
            logger.error(f'\033[31mFAILED\033[0m for {maturity} (insufficient data points)')
            self.update_results(result)
            return expiry

        # Perform SVI fitting
        params, loss = SVIModel.fit(tiv=w, vega=vega, k=k, tau=t)

        # If fitting failed
        if np.isnan(params[0]):
            result = self.failed_calibration(expiry, maturity, t, len(k))
            logger.error(f'\033[31mFAILED\033[0m for {maturity}')
            self.update_results(result)
            return expiry

        # Successful fitting
        self.params_dict[expiry] = (t, params)

        # Calculate all model statistics
        stats = self.calculate_model_stats(params, t, k, iv)

        # Create result dictionary
        result = {
            's': float(self.s),
            't': float(t),
            'r': float(self.r),
            'expiry': expiry,
            'maturity': maturity,
            'fit_success': True,
            'calendar_arbitrage_free': True,  # Updated later
            'loss': float(loss),
            'n_points': int(len(k)),
            **stats
        }

        logger.info(f'\033[32mSUCCESS\033[0m for {maturity}')

        self.update_results(result)
        return expiry

    def update_results(self, result_row):
        """Update results data dictionary"""
        for key, value in result_row.items():
            if key in self.results_data:
                self.results_data[key].append(value)

    def fit_model(self):
        """Execute full SVI calibration process"""
        start_time = time.time()
        logger.info(f"Calibrating {self.currency} option chain data...")
        logger.info("=================================================================")

        # Process all maturities in parallel
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.process_maturity, expiry, group)
                for expiry, group in self.groups
            ]
            for future in futures:
                future.result()

        # Create results DataFrame and mapping for updates
        fit_results = pd.DataFrame(self.results_data, index=self.results_data['maturity'])
        fit_results = fit_results.sort_values(by='t')
        maturities_dict = {row['expiry']: idx for idx, row in fit_results.iterrows()}

        # Check for calendar arbitrage
        sorted_maturities = sorted(self.params_dict.keys(), key=lambda x: self.params_dict[x][0])
        calendar_arbitrage_free = SVIModel.check_calendar_arbitrage(
            sorted_maturities, self.params_dict, self.groups, self.s, self.num_points
        )

        # Update calendar arbitrage status
        for mat in sorted_maturities:
            mat_name = maturities_dict[mat]
            fit_results.at[mat_name, 'calendar_arbitrage_free'] = calendar_arbitrage_free

        # Correct calendar arbitrage violations
        self.correct_calendar_arbitrage(sorted_maturities, fit_results, maturities_dict)

        # Clean up results and report execution time
        fit_results = fit_results.drop(columns='maturity')
        end_time = time.time()
        logger.info(f"Total model execution time: {end_time - start_time:.4f} seconds")

        return fit_results

    def correct_calendar_arbitrage(self, sorted_maturities, fit_results, maturities_dict):
        """Handle calendar arbitrage corrections"""
        for i in range(1, len(sorted_maturities)):
            mat2 = sorted_maturities[i]
            mat1 = sorted_maturities[i - 1]
            t2, params2 = self.params_dict[mat2]
            t1, params1 = self.params_dict[mat1]

            if np.any(np.isnan(params2)) or np.any(np.isnan(params1)):
                continue

            # Get clean data for correction
            _, _, k, w, vega, iv, _ = self.filter_market_data(self.groups.get_group(mat2))

            # Apply correction
            k_constraint = np.unique(np.concatenate([k, np.linspace(min(k), max(k), self.num_points)]))
            new_params = SVIModel.correct_calendar_arbitrage(
                params=params2, t=t2, tiv=w, vega=vega, k=k,
                prev_params=params1, prev_t=t1, k_constraint=k_constraint
            )

            # Update params dictionary
            self.params_dict[mat2] = (t2, new_params)

            # Calculate new stats and update results
            stats = self.calculate_model_stats(new_params, t2, k, iv)
            mat2_name = maturities_dict[mat2]

            # Update all stats at once
            for key, value in stats.items():
                fit_results.at[mat2_name, key] = value
            fit_results.at[mat2_name, 'fit_success'] = True

        # Final calendar arbitrage check
        calendar_arbitrage_free = SVIModel.check_calendar_arbitrage(
            sorted_maturities, self.params_dict, self.groups, self.s, self.num_points
        )

        # Update final status
        for mat in sorted_maturities:
            mat_name = maturities_dict[mat]
            fit_results.at[mat_name, 'calendar_arbitrage_free'] = calendar_arbitrage_free


@catch_exception
def fit_model(option_chain: pd.DataFrame, num_points: int = 2000) -> pd.DataFrame:
    """
    Fit a volatility model to market data with parallel processing.

    Parameters:
    - option_chain: DataFrame with market data
    - num_points: Number of points for k_grid and plotting

    Returns:
    - fit_results: DataFrame with all fit results and performance metrics as columns, maturities as index
    """
    currency = option_chain['currency'].iloc[0] if 'currency' in option_chain.columns else 'Unknown'

    # Instantiate the calibrator and run the fitting
    calibrator = SVICalibrator(option_chain, currency, num_points)
    fit_results = calibrator.fit_model()

    return fit_results


@catch_exception
def get_iv_surface(model_results: pd.DataFrame,
                   domain_params: Tuple[float, float, int] = (-1.5, 1.5, 1000),
                   return_domain: str = 'log_moneyness') -> Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray]]:
    """
    Generate implied volatility surface using optimized SVI parameters.

    Works with both regular fit_results and interpolated_results dataframes.

    Parameters:
    - model_results: DataFrame from fit_model() or interpolate_model(). Maturity names or DTM as Index
    - domain_params: Tuple of (min, max, num_points) for the log-moneyness array
    - return_domain: Domain for x-axis values ('log_moneyness', 'moneyness', 'returns', 'strikes', 'delta')

    Returns:
    - Tuple of (iv_surface, x_surface)
      iv_surface: Dictionary mapping maturity to IV arrays
      x_surface: Dictionary mapping maturity to requested x domain arrays
    """
    # Check if required columns are present
    required_columns = ['a', 'b', 'm', 'rho', 'sigma', 't', 's']
    missing_columns = [col for col in required_columns if col not in model_results.columns]
    if missing_columns:
        raise VolyError(f"Required columns missing in model_results: {missing_columns}")

    # Generate implied volatility surface in log-moneyness domain
    LM = np.linspace(domain_params[0], domain_params[1], domain_params[2])

    iv_surface = {}
    x_surface = {}

    # Process each maturity/dtm
    for i in model_results.index:
        # Calculate SVI total implied variance and convert to IV
        params = [
            model_results.loc[i, 'a'],
            model_results.loc[i, 'b'],
            model_results.loc[i, 'm'],
            model_results.loc[i, 'rho'],
            model_results.loc[i, 'sigma']
        ]
        s = model_results.loc[i, 's']
        t = model_results.loc[i, 't']
        r = model_results.loc[i, 'r'] if 'r' in model_results.columns else 0

        # Calculate implied volatility
        w = np.array([SVIModel.svi(x, *params) for x in LM])
        o = np.sqrt(w / t)
        iv_surface[i] = o

        # Calculate x domain for this maturity/dtm
        x = get_domain(domain_params, s, r, o, t, return_domain)
        x_surface[i] = x

    return iv_surface, x_surface
