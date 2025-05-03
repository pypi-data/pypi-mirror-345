"""
This module handles calculating risk-neutral densities from
fitted volatility models and converting to probability functions.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
from voly.utils.logger import logger, catch_exception
from voly.exceptions import VolyError
from voly.models import SVIModel
from voly.formulas import bs, d1, d2
from scipy import stats
from voly.utils.density import (
    prepare_domains,
    normalize_density,
    transform_to_domains,
    select_domain_results,
    center_distributions
)


@catch_exception
def breeden(domain_params, s, r, o, t, return_domain):
    """
    Breeden-Litzenberger method for RND estimation.

    Parameters:
    -----------
    domain_params : tuple
        (min_log_moneyness, max_log_moneyness, num_points)
    s : float
        Spot price
    r : float
        Risk-free rate
    o : ndarray
        Implied volatility array
    t : float
        Time to expiry in years
    return_domain : str
        Domain for results ('log_moneyness', 'moneyness', 'returns', 'strikes')

    Returns:
    --------
    tuple
        (pdf, cdf, x, moments)
    """
    # Prepare domain arrays
    domains = prepare_domains(domain_params, s)
    K = domains['strikes']
    dx = domains['dx']

    # Calculate option prices and derivatives
    c = [bs(s, strike, r, vol, t, flag='call') for strike, vol in zip(K, o)]
    c1 = np.gradient(c, K)
    c2 = np.gradient(c1, K)

    # Calculate RND in strike domain and apply discount factor
    rnd_k = np.maximum(np.exp(r * t) * c2, 0)

    # Transform to log-moneyness domain first
    rnd_lm = rnd_k * K  # Convert to log-moneyness domain
    pdf_lm = normalize_density(rnd_lm, dx)

    # Transform to other domains
    pdfs = transform_to_domains(pdf_lm, domains)

    # Return results for requested domain
    pdf, cdf, x = select_domain_results(pdfs, domains, return_domain)

    # Calculate moments
    moments = get_all_moments(x, pdf)

    return pdf, cdf, x, moments


@catch_exception
def rookley(domain_params, s, r, o, t, return_domain):
    """
    Rookley method for RND estimation, using volatility smile derivatives.

    Parameters:
    -----------
    domain_params : tuple
        (min_log_moneyness, max_log_moneyness, num_points)
    s : float
        Spot price
    r : float
        Risk-free rate
    o : ndarray
        Implied volatility array
    t : float
        Time to expiry in years
    return_domain : str
        Domain for results ('log_moneyness', 'moneyness', 'returns', 'strikes')

    Returns:
    --------
    tuple
        (pdf, cdf, x, moments)
    """
    # Prepare domain arrays
    domains = prepare_domains(domain_params, s)
    M = domains['moneyness']
    K = domains['strikes']
    dx = domains['dx']

    # Calculate volatility derivatives with respect to moneyness
    o1 = np.gradient(o, M)
    o2 = np.gradient(o1, M)

    # Precompute common terms
    st = np.sqrt(t)
    rt = r * t
    ert = np.exp(rt)

    # Calculate Black-Scholes d1 and d2 terms
    n_d1 = (np.log(M) + (r + 0.5 * o ** 2) * t) / (o * st)
    n_d2 = n_d1 - o * st

    # Calculate various derivatives needed for the density
    del_d1_M = 1 / (M * o * st)
    del_d2_M = del_d1_M
    del_d1_o = -(np.log(M) + rt) / (o ** 2 * st) + st / 2
    del_d2_o = -(np.log(M) + rt) / (o ** 2 * st) - st / 2

    d_d1_M = del_d1_M + del_d1_o * o1
    d_d2_M = del_d2_M + del_d2_o * o1

    # Complex second derivatives
    dd_d1_M = (
            -(1 / (M * o * st)) * (1 / M + o1 / o)
            + o2 * (st / 2 - (np.log(M) + rt) / (o ** 2 * st))
            + o1 * (2 * o1 * (np.log(M) + rt) / (o ** 3 * st) - 1 / (M * o ** 2 * st))
    )

    dd_d2_M = (
            -(1 / (M * o * st)) * (1 / M + o1 / o)
            - o2 * (st / 2 + (np.log(M) + rt) / (o ** 2 * st))
            + o1 * (2 * o1 * (np.log(M) + rt) / (o ** 3 * st) - 1 / (M * o ** 2 * st))
    )

    # Call price derivatives with respect to moneyness
    d_c_M = (
            stats.norm.pdf(n_d1) * d_d1_M
            - (1 / ert) * stats.norm.pdf(n_d2) / M * d_d2_M
            + (1 / ert) * stats.norm.cdf(n_d2) / (M ** 2)
    )

    dd_c_M = (
            stats.norm.pdf(n_d1) * (dd_d1_M - n_d1 * d_d1_M ** 2)
            - stats.norm.pdf(n_d2) / (ert * M) * (dd_d2_M - 2 / M * d_d2_M - n_d2 * d_d2_M ** 2)
            - 2 * stats.norm.cdf(n_d2) / (ert * M ** 3)
    )

    # Convert from moneyness to strike derivatives
    dd_c_K = dd_c_M * (M / K) ** 2 + 2 * d_c_M * (M / K ** 2)

    # Calculate RND in strike domain and apply discount factor
    rnd_k = np.maximum(ert * s * dd_c_K, 0)

    # Transform to log-moneyness domain first
    rnd_lm = rnd_k * K  # Convert to log-moneyness domain
    pdf_lm = normalize_density(rnd_lm, dx)

    # Transform to other domains
    pdfs = transform_to_domains(pdf_lm, domains)

    # Return results for requested domain
    pdf, cdf, x = select_domain_results(pdfs, domains, return_domain)

    # Calculate moments
    moments = get_all_moments(x, pdf)

    return pdf, cdf, x, moments


@catch_exception
def get_all_moments(x, pdf, model_params=None):
    """
    Calculate statistical moments and other distributional properties.

    Parameters:
    -----------
    x : ndarray
        Domain values
    pdf : ndarray
        Probability density values
    model_params : dict, optional
        Additional model parameters to include in the results

    Returns:
    --------
    dict
        Dictionary of calculated moments and properties
    """
    # Skip calculation for invalid inputs
    if len(x) != len(pdf) or len(x) < 3:
        logger.warning("Invalid inputs for moment calculation")
        return {}

    # Compute dx for integration
    dx = np.diff(x, prepend=x[0])

    # Ensure the PDF integrates to 1
    pdf_normalized = pdf / np.trapz(pdf, x)

    # Raw Moments (μ_k = E[X^k])
    raw_moments = {
        'raw_0': np.trapz(pdf_normalized, x),  # Zeroth (~1)
        'raw_1': np.trapz(x * pdf_normalized, x),  # First (mean)
        'raw_2': np.trapz(x ** 2 * pdf_normalized, x),  # Second
        'raw_3': np.trapz(x ** 3 * pdf_normalized, x),  # Third
        'raw_4': np.trapz(x ** 4 * pdf_normalized, x),  # Fourth
        'raw_5': np.trapz(x ** 5 * pdf_normalized, x),  # Fifth
        'raw_6': np.trapz(x ** 6 * pdf_normalized, x),  # Sixth
    }

    # Derived statistics
    mean = raw_moments['raw_1']
    variance = np.trapz((x - mean) ** 2 * pdf_normalized, x)
    std_dev = np.sqrt(max(variance, 1e-10))  # Prevent division by zero

    # Central Moments (m_k = E[(X - μ)^k])
    cent_moments = {
        'cent_1': 0,  # Theoretically zero
        'cent_2': variance,  # Second (variance)
        'cent_3': np.trapz((x - mean) ** 3 * pdf_normalized, x),  # Third
        'cent_4': np.trapz((x - mean) ** 4 * pdf_normalized, x),  # Fourth
        'cent_5': np.trapz((x - mean) ** 5 * pdf_normalized, x),  # Fifth
        'cent_6': np.trapz((x - mean) ** 6 * pdf_normalized, x),  # Sixth
    }

    # Standardized Moments (m̄_k = E[((X - μ)/σ)^k])
    z = (x - mean) / std_dev
    std_moments = {
        'std_3': np.trapz(z ** 3 * pdf_normalized, x),  # Skewness
        'std_4': np.trapz(z ** 4 * pdf_normalized, x),  # Kurtosis
        'std_5': np.trapz(z ** 5 * pdf_normalized, x),  # Fifth
        'std_6': np.trapz(z ** 6 * pdf_normalized, x),  # Sixth
    }

    # Calculate CDF for quantiles
    cdf = np.cumsum(pdf_normalized * dx)
    cdf = cdf / cdf[-1]  # Normalize

    # Quantiles and other statistics
    mode_idx = np.argmax(pdf)
    mode = x[mode_idx] if 0 <= mode_idx < len(x) else mean

    # Find percentiles
    q25_idx = np.searchsorted(cdf, 0.25)
    q50_idx = np.searchsorted(cdf, 0.50)
    q75_idx = np.searchsorted(cdf, 0.75)

    q25 = x[q25_idx] if 0 <= q25_idx < len(x) else np.nan
    median = x[q50_idx] if 0 <= q50_idx < len(x) else np.nan
    q75 = x[q75_idx] if 0 <= q75_idx < len(x) else np.nan
    iqr = q75 - q25

    # Information theory measures
    entropy = -np.trapz(pdf_normalized * np.log(pdf_normalized + 1e-10), x)

    # Z-score areas (probability mass in standard deviation regions)
    z_areas = {
        'o1p': np.sum(pdf_normalized[(z > 0) & (z < 1)] * dx[(z > 0) & (z < 1)]),
        'o2p': np.sum(pdf_normalized[(z >= 1) & (z < 2)] * dx[(z >= 1) & (z < 2)]),
        'o3p': np.sum(pdf_normalized[(z >= 2) & (z < 3)] * dx[(z >= 2) & (z < 3)]),
        'o4p': np.sum(pdf_normalized[z >= 3] * dx[z >= 3]),
        'o1n': np.sum(pdf_normalized[(z < 0) & (z > -1)] * dx[(z < 0) & (z > -1)]),
        'o2n': np.sum(pdf_normalized[(z <= -1) & (z > -2)] * dx[(z <= -1) & (z > -2)]),
        'o3n': np.sum(pdf_normalized[(z <= -2) & (z > -3)] * dx[(z <= -2) & (z > -3)]),
        'o4n': np.sum(pdf_normalized[z <= -3] * dx[z <= -3]),
    }

    # Common statistic names
    common_stats = {
        'mean': mean,
        'variance': variance,
        'std_dev': std_dev,
        'skewness': std_moments['std_3'],
        'kurtosis': std_moments['std_4'],
        'excess_kurtosis': std_moments['std_4'] - 3,
        'median': median,
        'mode': mode,
        'q25': q25,
        'q75': q75,
        'iqr': iqr,
        'entropy': entropy,
    }

    # Combine all statistics
    moments = {**raw_moments, **cent_moments, **std_moments, **z_areas, **common_stats}

    # Add model parameters if provided
    if model_params is not None:
        moments.update(model_params)

    return moments


@catch_exception
def get_rnd_surface(model_results: pd.DataFrame,
                    domain_params: Tuple[float, float, int] = (-1.5, 1.5, 1000),
                    return_domain: str = 'log_moneyness',
                    method: str = 'rookley',
                    centered: bool = False) -> Dict[str, Any]:
    """
    Generate risk-neutral density surface from volatility surface parameters.

    Parameters:
    -----------
    model_results : pd.DataFrame
        DataFrame from fit_model() or interpolate_model() with SVI parameters
    domain_params : tuple
        (min_log_moneyness, max_log_moneyness, num_points)
    return_domain : str
        Domain for results ('log_moneyness', 'moneyness', 'returns', 'strikes')
    method : str
        Method for RND estimation ('rookley' or 'breeden')
    centered : bool
        Whether to center distributions at their modes (peaks)

    Returns:
    --------
    dict
        Dictionary containing pdf_surface, cdf_surface, x_surface, and moments
    """
    # Validate inputs
    required_columns = ['s', 't', 'r', 'a', 'b', 'm', 'm', 'sigma']
    missing_columns = [col for col in required_columns if col not in model_results.columns]
    if missing_columns:
        raise VolyError(f"Required columns missing in model_results: {missing_columns}")

    # Validate method
    if method not in ['rookley', 'breeden']:
        raise VolyError(f"Invalid method: {method}. Must be 'rookley' or 'breeden'")

    # Validate return_domain
    valid_domains = ['log_moneyness', 'moneyness', 'returns', 'strikes']
    if return_domain not in valid_domains:
        raise VolyError(f"Invalid return_domain: {return_domain}. Must be one of {valid_domains}")

    # Select method function
    rnd_method = rookley if method == 'rookley' else breeden

    # Initialize result containers
    pdf_surface = {}
    cdf_surface = {}
    x_surface = {}
    all_moments = {}

    # Process each maturity/expiry
    for i in model_results.index:
        try:
            # Extract SVI parameters for this maturity
            params = [
                model_results.loc[i, 'a'],
                model_results.loc[i, 'b'],
                model_results.loc[i, 'm'],
                model_results.loc[i, 'rho'],
                model_results.loc[i, 'sigma']
            ]
            s = model_results.loc[i, 's']
            r = model_results.loc[i, 'r']
            t = model_results.loc[i, 't']

            # Calculate implied volatility surface from SVI parameters
            LM = np.linspace(domain_params[0], domain_params[1], domain_params[2])
            w = SVIModel.svi(LM, *params)
            o = np.sqrt(w / t)

            # Calculate RND using the selected method
            pdf, cdf, x, moments = rnd_method(domain_params, s, r, o, t, return_domain)

            # Store results
            pdf_surface[i] = pdf
            cdf_surface[i] = cdf
            x_surface[i] = x
            all_moments[i] = moments

        except Exception as e:
            logger.warning(f"Failed to calculate RND for maturity {i}: {str(e)}")

    # Check if we have any valid results
    if not pdf_surface:
        raise VolyError("No valid densities could be calculated. Check your input data.")

    # Center distributions if requested
    if centered:
        pdf_surface, cdf_surface = center_distributions(pdf_surface, cdf_surface, x_surface)
        logger.info("Distributions have been centered at their modes")

    # Create DataFrame with moments
    moments = pd.DataFrame(all_moments).T

    logger.info(f"RND surface calculation complete using {method} method")

    return {
        'pdf_surface': pdf_surface,
        'cdf_surface': cdf_surface,
        'x_surface': x_surface,
        'moments': moments
    }
