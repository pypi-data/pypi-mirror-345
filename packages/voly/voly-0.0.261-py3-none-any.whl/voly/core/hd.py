"""
This module handles calculating historical densities from time series of prices
and converting them to probability distributions.
"""

import ccxt
import numpy as np
import pandas as pd
import datetime as dt
from typing import Dict, Tuple, Any, Optional, List
from scipy import stats
from scipy.stats import t as student_t
from voly.utils.logger import logger, catch_exception
from voly.exceptions import VolyError
from voly.core.rnd import get_all_moments
from voly.utils.density import (
    prepare_domains,
    normalize_density,
    transform_to_domains,
    select_domain_results,
    center_distributions
)


@catch_exception
def get_historical_data(currency: str,
                        lookback_days: str,
                        granularity: str,
                        exchange_name: str) -> pd.DataFrame:
    """
    Fetch historical OHLCV data for a cryptocurrency.

    Parameters:
    -----------
    currency : str
        The cryptocurrency to fetch data for (e.g., 'BTC', 'ETH')
    lookback_days : str
        The lookback period in days, formatted as '90d', '30d', etc.
    granularity : str
        The time interval for data points (e.g., '15m', '1h', '1d')
    exchange_name : str
        The exchange to fetch data from (default: 'binance')

    Returns:
    --------
    pd.DataFrame
        Historical price data with OHLCV columns and datetime index
    """
    # Validate inputs
    if not lookback_days.endswith('d'):
        raise VolyError("lookback_days should be in format '90d', '30d', etc.")

    try:
        # Get the exchange class from ccxt
        exchange_class = getattr(ccxt, exchange_name.lower())
        exchange = exchange_class({'enableRateLimit': True})
    except (AttributeError, TypeError):
        raise VolyError(f"Exchange '{exchange_name}' not found in ccxt. Please check the exchange name.")

    # Form the trading pair symbol
    symbol = f"{currency}/USDT"

    # Convert lookback_days to timestamp
    days_ago = int(lookback_days[:-1])
    date_start = (dt.datetime.now() - dt.timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
    from_ts = exchange.parse8601(date_start)

    ohlcv_list = []
    ohlcv = exchange.fetch_ohlcv(symbol, granularity, since=from_ts, limit=1000)
    ohlcv_list.append(ohlcv)

    while True:
        from_ts = ohlcv[-1][0]
        new_ohlcv = exchange.fetch_ohlcv(symbol, granularity, since=from_ts, limit=1000)
        if len(new_ohlcv) <= 1:  # No new data or just one overlapping candle
            break
        ohlcv.extend(new_ohlcv[1:])  # Skip the first one to avoid duplicates
        if len(new_ohlcv) != 1000:
            break

    # Convert to DataFrame
    df_hist = pd.DataFrame(ohlcv, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    df_hist['date'] = pd.to_datetime(df_hist['date'], unit='ms')
    df_hist.set_index('date', inplace=True)
    df_hist = df_hist.sort_index(ascending=True)
    df_hist = df_hist[~df_hist.index.duplicated(keep='last')].sort_index()

    logger.info(f"Data fetched successfully: {len(df_hist)} rows from {df_hist.index[0]} to {df_hist.index[-1]}")

    return df_hist


@catch_exception
def calculate_historical_returns(df_hist: pd.DataFrame, n_periods: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate historical returns and scale them appropriately.

    Parameters:
    -----------
    df_hist : pd.DataFrame
        Historical price data
    n_periods : int
        Number of periods to scale returns

    Returns:
    --------
    Tuple[np.ndarray, np.ndarray]
        (scaled_returns, raw_returns) tuple
    """
    # Calculate log returns
    raw_returns = np.log(df_hist['close'] / df_hist['close'].shift(1)).dropna().values

    # Filter historical data based on n_periods
    if len(raw_returns) < n_periods:
        logger.warning(f"Not enough historical data, using all {len(raw_returns)} points available")
        dte_returns = raw_returns
    else:
        dte_returns = raw_returns[-n_periods:]

    # Calculate scaling factor
    scaling_factor = np.sqrt(n_periods)

    # Scale returns for the maturity
    scaled_returns = dte_returns * scaling_factor

    return scaled_returns, dte_returns


@catch_exception
def calculate_normal_hd(df_hist: pd.DataFrame,
                        t: float,
                        n_periods: int,
                        domains: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    """
    Calculate historical density using a normal distribution based on historical returns.

    Parameters:
    -----------
    df_hist : pd.DataFrame
        Historical price data
    n_periods : int
        Number of periods to scale returns
    domains : Dict[str, np.ndarray]
        Domain arrays

    Returns:
    --------
    Dict[str, np.ndarray]
        Dictionary of PDFs in different domains
    """
    # Extract log-moneyness domain
    LM = domains['log_moneyness']
    dx = domains['dx']

    # Get scaled returns
    scaled_returns, dte_returns = calculate_historical_returns(df_hist, n_periods)

    # Calculate parameters for normal distribution
    mu_scaled = np.mean(scaled_returns)
    sigma_scaled = np.std(scaled_returns)

    # Calculate PDF using normal distribution in log-moneyness domain
    pdf_lm = stats.norm.pdf(LM, loc=mu_scaled, scale=sigma_scaled)

    # Normalize the PDF
    pdf_lm = normalize_density(pdf_lm, dx)

    # Transform to other domains
    pdfs = transform_to_domains(pdf_lm, domains)

    return pdfs


@catch_exception
def calculate_student_t_hd(df_hist: pd.DataFrame,
                           t: float,
                           n_periods: int,
                           domains: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    """
    Calculate historical density using Student's t-distribution based on historical returns.

    Parameters:
    -----------
    df_hist : pd.DataFrame
        Historical price data
    n_periods : int
        Number of periods to scale returns
    domains : Dict[str, np.ndarray]
        Domain arrays

    Returns:
    --------
    Dict[str, np.ndarray]
        Dictionary of PDFs in different domains
    """
    # Extract log-moneyness domain
    LM = domains['log_moneyness']
    dx = domains['dx']

    # Get scaled returns
    scaled_returns, dte_returns = calculate_historical_returns(df_hist, n_periods)

    # Calculate parameters for t-distribution
    mu_scaled = np.mean(scaled_returns)
    sigma_scaled = np.std(scaled_returns)

    # Estimate excess kurtosis and calculate degrees of freedom
    kurtosis = stats.kurtosis(dte_returns, fisher=True)

    # Convert kurtosis to degrees of freedom (df)
    # For t-distribution: kurtosis = 6/(df-4) for df > 4
    # Solve for df: df = 6/kurtosis + 4
    if kurtosis > 0:
        df = min(max(6 / kurtosis + 4, 3), 30)  # Bound between 3 and 30
    else:
        df = 5  # Default value if kurtosis calculation fails

    # Scale parameter for t-distribution
    # In scipy's t-distribution, the scale parameter is different from normal std
    # For t-distribution: variance = (df/(df-2)) * scale^2
    # So: scale = sqrt(variance * (df-2)/df)
    scale = sigma_scaled * np.sqrt((df - 2) / df) if df > 2 else sigma_scaled

    # Calculate PDF using t-distribution in log-moneyness domain
    pdf_lm = student_t.pdf(LM, df=df, loc=mu_scaled, scale=scale)

    # Normalize the PDF
    pdf_lm = normalize_density(pdf_lm, dx)

    # Transform to other domains
    pdfs = transform_to_domains(pdf_lm, domains)

    return pdfs


@catch_exception
def calculate_kde_hd(df_hist: pd.DataFrame,
                     t: float,
                     n_periods: int,
                     domains: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    """
    Calculate historical density using Kernel Density Estimation (KDE) based on historical returns.

    Parameters:
    -----------
    df_hist : pd.DataFrame
        Historical price data
    t : float
        Time to maturity in years
    n_periods : int
        Number of periods to scale returns
    domains : Dict[str, np.ndarray]
        Domain arrays

    Returns:
    --------
    Dict[str, np.ndarray]
        Dictionary of PDFs in different domains
    """
    # Extract log-moneyness domain
    LM = domains['log_moneyness']
    dx = domains['dx']

    # Get scaled returns
    scaled_returns, dte_returns = calculate_historical_returns(df_hist, n_periods)
    vol = np.sqrt(scaled_returns.std()) ** t
    scaled_returns = scaled_returns / vol

    # Fit KDE model using scipy's gaussian_kde with Scott's rule for bandwidth
    kde = stats.gaussian_kde(scaled_returns, bw_method='scott')

    # Evaluate KDE at points in log-moneyness domain
    pdf_lm = kde(LM)

    # Normalize the PDF
    pdf_lm = normalize_density(pdf_lm, dx)

    # Transform to other domains
    pdfs = transform_to_domains(pdf_lm, domains)

    return pdfs


@catch_exception
def get_hd_surface(model_results: pd.DataFrame,
                   df_hist: pd.DataFrame,
                   domain_params: Tuple[float, float, int] = (-1.5, 1.5, 1000),
                   return_domain: str = 'log_moneyness',
                   method: str = 'normal',
                   centered: bool = False) -> Dict[str, Any]:
    """
    Generate historical density surface using various distribution methods.

    Parameters:
    -----------
    model_results : pd.DataFrame
        DataFrame with model parameters and maturities
    df_hist : pd.DataFrame
        DataFrame with historical price data
    domain_params : Tuple[float, float, int]
        (min_log_moneyness, max_log_moneyness, num_points)
    return_domain : str
        Domain for results ('log_moneyness', 'moneyness', 'returns', 'strikes')
    method : str
        Method for estimating density ('normal', 'student_t', 'kde')
    centered : bool
        Whether to center distributions at their modes (peaks)

    Returns:
    --------
    Dict[str, Any]
        Dictionary with pdf_surface, cdf_surface, x_surface, and moments
    """
    # Validate inputs
    required_columns = ['s', 't']
    missing_columns = [col for col in required_columns if col not in model_results.columns]
    if missing_columns:
        raise VolyError(f"Required columns missing in model_results: {missing_columns}")

    if len(df_hist) < 2:
        raise VolyError("Not enough data points in df_hist")

    # Validate return domain
    valid_domains = ['log_moneyness', 'moneyness', 'returns', 'strikes']
    if return_domain not in valid_domains:
        raise VolyError(f"Invalid return_domain: {return_domain}. Must be one of {valid_domains}")

    # Validate method
    valid_methods = ['normal', 'student_t', 'kde']
    if method not in valid_methods:
        raise VolyError(f"Invalid method: {method}. Must be one of {valid_methods}")

    # Select calculation function based on method
    if method == 'student_t':
        calculate_hd = calculate_student_t_hd
        logger.info("Using Student's t-distribution for historical density")
    elif method == 'kde':
        calculate_hd = calculate_kde_hd
        logger.info("Using Kernel Density Estimation (KDE) for historical density")
    else:  # default to normal
        calculate_hd = calculate_normal_hd
        logger.info("Using Normal distribution for historical density")

    # Determine granularity from data (minutes between data points)
    time_diff = (df_hist.index[1] - df_hist.index[0]).total_seconds() / 60
    minutes_per_period = max(1, int(time_diff))

    # Initialize result containers
    pdf_surface = {}
    cdf_surface = {}
    x_surface = {}
    all_moments = {}

    # Process each maturity
    for i in model_results.index:
        try:
            # Get parameters for this maturity
            s = model_results.loc[i, 's']  # Spot price
            t = model_results.loc[i, 't']  # Time to maturity in years

            # Calculate relevant periods for this maturity
            dte = t * 365.25  # Days to expiry
            n_periods = max(1, int(dte * 24 * 60 / minutes_per_period))

            # Prepare domains
            domains = prepare_domains(domain_params, s)

            # Calculate density using the selected method
            pdfs = calculate_hd(
                df_hist=df_hist,
                t = t,
                n_periods=n_periods,
                domains=domains
            )

            # Select results for the requested domain
            pdf, cdf, x = select_domain_results(pdfs, domains, return_domain)

            # Calculate moments
            moments = get_all_moments(x, pdf)

            # Store results
            pdf_surface[i] = pdf
            cdf_surface[i] = cdf
            x_surface[i] = x
            all_moments[i] = moments

        except Exception as e:
            logger.warning(f"Failed to calculate HD for maturity {i} using {method} method: {str(e)}")

    # Check if we have any valid results
    if not pdf_surface:
        raise VolyError(f"No valid densities could be calculated using {method} method. Check your input data.")

    # Center distributions if requested
    if centered:
        pdf_surface, cdf_surface = center_distributions(pdf_surface, cdf_surface, x_surface)
        logger.info("Distributions have been centered at their modes")

    # Create DataFrame with moments
    moments = pd.DataFrame(all_moments).T

    logger.info(f"Historical density calculation complete using {method} distribution")

    return {
        'pdf_surface': pdf_surface,
        'cdf_surface': cdf_surface,
        'x_surface': x_surface,
        'moments': moments
    }
