"""
Main client interface for the Voly package.

This module provides the VolyClient class, which serves as the main
entry point for users to interact with the package functionality.
"""

import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
import plotly.graph_objects as go

from voly.utils.logger import logger, catch_exception, setup_file_logging
from voly.exceptions import VolyError
from voly.models import SVIModel
from voly.formulas import (
    d1, d2, bs, delta, gamma, vega, theta, rho, vanna, volga, charm, greeks, iv
)
from voly.core.data import fetch_option_chain, process_option_chain
from voly.core.fit import fit_model, get_iv_surface
from voly.core.rnd import get_rnd_surface
from voly.core.hd import get_historical_data, get_hd_surface
from voly.core.interpolate import interpolate_model
from voly.core.charts import (
    plot_all_smiles, plot_raw_parameters, plot_jw_parameters, plot_fit_performance, plot_3d_surface
)


class VolyClient:
    def __init__(self, enable_file_logging: bool = False, logs_dir: str = "logs/"):
        """
        Initialize the Voly client.

        Parameters:
        - enable_file_logging: Whether to enable file-based logging
        - logs_dir: Directory for log files if file logging is enabled
        """

        from importlib.metadata import version
        voly_version = version("voly")

        if enable_file_logging:
            setup_file_logging(logs_dir)

        logger.info(f"VolyClient (v{voly_version}) initialized")
        self._loop = None  # For async operations

    def _get_event_loop(self):
        """Get or create an event loop for async operations"""
        try:
            self._loop = asyncio.get_event_loop()
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        return self._loop

    # -------------------------------------------------------------------------
    # Data Fetching and Processing
    # -------------------------------------------------------------------------

    def get_option_chain(self, exchange: str = 'deribit',
                         currency: str = 'BTC',
                         depth: bool = False) -> pd.DataFrame:
        """
        Fetch option chain data from the specified exchange.

        Parameters:
        - exchange: Exchange to fetch data from (currently only 'deribit' is supported)
        - currency: Currency to fetch options for (e.g., 'BTC', 'ETH')
        - depth: Whether to include full order book depth

        Returns:
        - Processed option chain data as a pandas DataFrame
        """
        logger.info(f"Fetching option chain data from {exchange} for {currency}")

        loop = self._get_event_loop()

        try:
            option_chain = loop.run_until_complete(
                fetch_option_chain(exchange, currency)
            )
            return option_chain
        except VolyError as e:
            logger.error(f"Error fetching option chain: {str(e)}")
            raise

    # -------------------------------------------------------------------------
    # SVI, Black-Scholes and Greeks Calculations
    # -------------------------------------------------------------------------

    @staticmethod
    def svi(k: float, a: float, b: float, m: float, rho: float, sigma: float) -> float:
        """Calculate SVI total implied variance using raw parameterization."""
        return SVIModel.svi(k, a, b, m, rho, sigma)

    @staticmethod
    def d1(s: float, K: float, r: float, o: float, t: float,
           flag: str = 'call') -> float:
        return d1(s, K, r, o, t, flag)

    @staticmethod
    def d2(s: float, K: float, r: float, o: float, t: float,
           flag: str = 'call') -> float:
        return d2(s, K, r, o, t, flag)

    @staticmethod
    def bs(s: float, K: float, r: float, o: float, t: float,
           flag: str = 'call') -> float:
        return bs(s, K, r, o, t, flag)

    @staticmethod
    def delta(s: float, K: float, r: float, o: float, t: float,
              flag: str = 'call') -> float:
        return delta(s, K, r, o, t, flag)

    @staticmethod
    def gamma(s: float, K: float, r: float, o: float, t: float,
              flag: str = 'call') -> float:
        return gamma(s, K, r, o, t, flag)

    @staticmethod
    def vega(s: float, K: float, r: float, o: float, t: float,
             flag: str = 'call') -> float:
        return vega(s, K, r, o, t, flag)

    @staticmethod
    def theta(s: float, K: float, r: float, o: float, t: float,
              flag: str = 'call') -> float:
        return theta(s, K, r, o, t, flag)

    @staticmethod
    def rho(s: float, K: float, r: float, o: float, t: float,
            flag: str = 'call') -> float:
        return rho(s, K, r, o, t, flag)

    @staticmethod
    def vanna(s: float, K: float, r: float, o: float, t: float,
              flag: str = 'call') -> float:
        return vanna(s, K, r, o, t, flag)

    @staticmethod
    def volga(s: float, K: float, r: float, o: float, t: float,
              flag: str = 'call') -> float:
        return volga(s, K, r, o, t, flag)

    @staticmethod
    def charm(s: float, K: float, r: float, o: float, t: float,
              flag: str = 'call') -> float:
        return charm(s, K, r, o, t, flag)

    @staticmethod
    def greeks(s: float, K: float, r: float, o: float, t: float,
               flag: str = 'call') -> Dict[str, float]:
        return greeks(s, K, r, o, t, flag)

    @staticmethod
    def iv(option_price: float, s: float, K: float, r: float, t: float,
           flag: str = 'call') -> float:
        return iv(option_price, s, K, r, t, flag)

    # -------------------------------------------------------------------------
    # Model Fitting
    # -------------------------------------------------------------------------

    @staticmethod
    def fit_model(option_chain: pd.DataFrame) -> pd.DataFrame:
        """
        Fit a volatility model to market data using the improved SVI approach.

        Parameters:
        - option_chain: DataFrame with option market data

        Returns:
        - DataFrame with fit results including arbitrage checks
        """
        logger.info(f"Fitting model to market data")

        # Fit the model
        fit_results = fit_model(
            option_chain=option_chain
        )

        return fit_results

    @staticmethod
    def get_iv_surface(model_results: pd.DataFrame,
                       domain_params: Tuple[float, float, int] = (-2, 2, 500),
                       return_domain: str = 'log_moneyness',
                       ) -> Dict[str, Any]:
        """
        Generate implied volatility surface using optimized SVI parameters.

        Parameters:
            - model_results: DataFrame from fit_model() or interpolate_model()
            - domain_params: Tuple of (min, max, num_points) for the moneyness grid
            - return_domain: str Domain for x-axis values ('log_moneyness', 'moneyness', 'strikes', 'delta')

        Returns:
        - Surface. Dict composed of (iv_surface, x_surface)
        """
        # Generate the surface
        iv_surface, x_surface = get_iv_surface(
            model_results=model_results,
            domain_params=domain_params,
            return_domain=return_domain
        )

        return {
            'iv_surface': iv_surface,
            'x_surface': x_surface
        }

    @staticmethod
    def plot_model(fit_results: pd.DataFrame,
                   option_chain: pd.DataFrame = None,
                   domain_params: Tuple[float, float, int] = (-2, 2, 500),
                   return_domain: str = 'log_moneyness',
                   ) -> Dict[str, Any]:
        """
        Generate all plots for the fitted model.

        Parameters:
        - fit_results: DataFrame with fitting results from fit_model()
        - option_chain: Optional market data for comparison
        - domain_params: Grid of log-moneyness values
        - return_domain: Domain for x-axis values ('log_moneyness', 'moneyness', 'strikes', 'returns', 'delta')

        Returns:
        - Dictionary of plot figures
        """
        plots = {}

        # Generate IV surface and domain
        iv_surface, x_surface = get_iv_surface(fit_results, domain_params, return_domain)

        if not option_chain.empty:
            # Create missing domains
            option_chain['log_moneyness'] = np.log(option_chain['strikes'] / option_chain['spot_price'].iloc[0])
            option_chain['moneyness'] = np.exp(option_chain['log_moneyness'])
            option_chain['returns'] = option_chain['moneyness'] - 1

        # Plot volatility smiles
        plots['smiles'] = plot_all_smiles(
            x_surface=x_surface,
            iv_surface=iv_surface,
            option_chain=option_chain,
            return_domain=return_domain
        )

        # Plot parameters
        plots['raw_params'] = plot_raw_parameters(fit_results)
        plots['jw_params'] = plot_jw_parameters(fit_results)

        # Plot fit statistics
        plots['fit_performance'] = plot_fit_performance(fit_results)

        if return_domain != 'delta':
            # Plot 3D surface
            plots['surface_3d'] = plot_3d_surface(
                x_surface=x_surface,
                iv_surface=iv_surface,
                fit_results=fit_results,
                return_domain=return_domain
            )
        else:
            pass

        return plots

    # -------------------------------------------------------------------------
    # Interpolate
    # -------------------------------------------------------------------------

    @staticmethod
    def interpolate_model(fit_results: pd.DataFrame,
                          list_of_days=None,
                          method: str = 'cubic') -> pd.DataFrame:
        """
        Interpolate a fitted model to specific days to expiry.

        Parameters:
        - fit_results: DataFrame with fitting results from fit_model()
        - list_of_days: List of specific days to include (e.g., ['7d', '30d', '90d'])
        - method: Interpolation method ('linear', 'cubic', 'pchip', etc.)

        Returns:
        - DataFrame with interpolated model parameters for the specified days
        """
        if list_of_days is None:
            list_of_days = ['7d', '30d', '90d', '150d', '240d']
        logger.info(f"Interpolating model with {method} method")

        # Interpolate the model
        interpolated_results = interpolate_model(
            fit_results, list_of_days, method
        )

        return interpolated_results

    # -------------------------------------------------------------------------
    # Risk-Neutral Density (RND)
    # -------------------------------------------------------------------------

    @staticmethod
    def get_rnd_surface(model_results: pd.DataFrame,
                        domain_params: Tuple[float, float, int] = (-1.5, 1.5, 1000),
                        return_domain: str = 'log_moneyness',
                        method: str = 'rookley',
                        centered: bool = False) -> Dict[str, Any]:
        """
        Generate risk-neutral density surface from volatility surface parameters.

        Parameters:
        - model_results: DataFrame from fit_model() or interpolate_model()
        - domain_params: Tuple of (min_log_moneyness, max_log_moneyness, num_points)
        - return_domain: Domain for results ('log_moneyness', 'moneyness', 'returns', 'strikes')
        - method: Method for RND estimation ('rookley' or 'breeden')
        - centered: Whether to center distributions at their modes (peaks)

        Returns:
        - Dictionary with pdf_surface, cdf_surface, x_surface, and moments
        """
        logger.info("Calculating RND surface")

        return get_rnd_surface(
            model_results=model_results,
            domain_params=domain_params,
            return_domain=return_domain,
            method=method,
            centered=centered
        )

    # -------------------------------------------------------------------------
    # Historical Density (HD)
    # -------------------------------------------------------------------------

    @staticmethod
    def get_historical_data(currency: str = 'BTC',
                            lookback_days: str = '90d',
                            granularity: str = '15m',
                            exchange_name: str = 'binance') -> pd.DataFrame:
        """
        Fetch historical OHLCV data for a cryptocurrency.

        Parameters:
        - currency: The cryptocurrency to fetch data for (e.g., 'BTC', 'ETH')
        - lookback_days: The lookback period in days, formatted as '90d', '30d', etc.
        - granularity: The time interval for data points (e.g., '15m', '1h', '1d')
        - exchange_name: The exchange to fetch data from (default: 'binance')

        Returns:
        - Historical price data with OHLCV columns and datetime index
        """
        return get_historical_data(
            currency=currency,
            lookback_days=lookback_days,
            granularity=granularity,
            exchange_name=exchange_name
        )

    @staticmethod
    def get_hd_surface(model_results: pd.DataFrame,
                       df_hist: pd.DataFrame,
                       domain_params: Tuple[float, float, int] = (-1.5, 1.5, 1000),
                       return_domain: str = 'log_moneyness',
                       method: str = 'normal',
                       centered: bool = False) -> Dict[str, Any]:
        """
        Generate historical density surface using various distribution methods.

        Parameters:
        - model_results: DataFrame with model parameters and maturities
        - df_hist: DataFrame with historical price data
        - domain_params: Tuple of (min_log_moneyness, max_log_moneyness, num_points)
        - return_domain: Domain for results ('log_moneyness', 'moneyness', 'returns', 'strikes')
        - method: Method for density estimation ('normal', 'student_t', 'kde')
        - centered: Whether to center distributions at their modes (peaks)

        Returns:
        - Dictionary with pdf_surface, cdf_surface, x_surface, and moments
        """

        return get_hd_surface(
            model_results=model_results,
            df_hist=df_hist,
            domain_params=domain_params,
            return_domain=return_domain,
            method=method,
            centered=centered
        )
