"""
Common utility functions for probability density calculations.

This module contains shared utility functions for working with probability
densities across different domains, used by both RND and HD calculations.
"""

import numpy as np
from typing import Dict, Tuple, List, Any
from scipy import stats, interpolate
from voly.utils.logger import catch_exception
from voly.formulas import d1, d2


@catch_exception
def prepare_domains(domain_params: Tuple[float, float, int],
                    s: float) -> Dict[str, np.ndarray]:
    """
    Calculate domain arrays for different representations.

    Parameters:
    -----------
    domain_params : Tuple[float, float, int]
        (min_log_moneyness, max_log_moneyness, num_points)
    s : float
        Spot price

    Returns:
    --------
    Dict[str, np.ndarray]
        Dictionary containing arrays for different domains
    """
    # Create log-moneyness grid
    LM = np.linspace(domain_params[0], domain_params[1], domain_params[2])

    # Calculate other domains
    M = np.exp(LM)  # Moneyness
    R = M - 1  # Returns
    K = M * s  # Strike prices

    # Precompute differentials for integration
    dx = LM[1] - LM[0]

    return {
        'log_moneyness': LM,
        'moneyness': M,
        'returns': R,
        'strikes': K,
        'dx': dx
    }


@catch_exception
def normalize_density(pdf_values: np.ndarray,
                      dx: float) -> np.ndarray:
    """
    Normalize a probability density function to integrate to 1.

    Parameters:
    -----------
    pdf_values : np.ndarray
        Array of PDF values
    dx : float
        Grid spacing

    Returns:
    --------
    np.ndarray
        Normalized PDF values
    """
    total_area = np.trapz(pdf_values, dx=dx)

    if total_area <= 0:
        # If area is negative or zero, use absolute values
        total_area = np.trapz(np.abs(pdf_values), dx=dx)

    # Handle very small values to prevent division by zero
    if abs(total_area) < 1e-10:
        return np.zeros_like(pdf_values)

    return pdf_values / total_area


@catch_exception
def transform_to_domains(pdf_lm: np.ndarray,
                         domains: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    """
    Transform density from log-moneyness domain to other domains.

    Parameters:
    -----------
    pdf_lm : np.ndarray
        PDF in log-moneyness domain
    domains : Dict[str, np.ndarray]
        Domain arrays

    Returns:
    --------
    Dict[str, np.ndarray]
        Dictionary of PDFs in different domains
    """
    LM = domains['log_moneyness']
    M = domains['moneyness']
    K = domains['strikes']
    R = domains['returns']
    dx = domains['dx']

    # Transform to other domains
    pdf_m = pdf_lm / M
    pdf_k = pdf_lm / K
    pdf_r = pdf_lm / (1 + R)

    # Calculate CDF
    cdf = np.cumsum(pdf_lm * dx)
    cdf = np.minimum(cdf / cdf[-1], 1.0)  # Ensure max value is 1

    return {
        'log_moneyness': pdf_lm,
        'moneyness': pdf_m,
        'returns': pdf_r,
        'strikes': pdf_k,
        'cdf': cdf
    }


@catch_exception
def select_domain_results(pdfs: Dict[str, np.ndarray],
                          domains: Dict[str, np.ndarray],
                          return_domain: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Select results for the requested domain.

    Parameters:
    -----------
    pdfs : Dict[str, np.ndarray]
        PDFs in different domains
    domains : Dict[str, np.ndarray]
        Domain arrays
    return_domain : str
        Requested domain

    Returns:
    --------
    Tuple[np.ndarray, np.ndarray, np.ndarray]
        (pdf, cdf, x) in the requested domain
    """
    if return_domain not in domains or return_domain not in pdfs:
        valid_domains = set(domains.keys()).intersection(set(pdfs.keys()))
        raise ValueError(f"Invalid return_domain: {return_domain}. Must be one of {valid_domains}")

    x = domains[return_domain]
    pdf = pdfs[return_domain]
    cdf = pdfs['cdf']

    return pdf, cdf, x


@catch_exception
def center_distributions(pdf_surface: Dict[str, np.ndarray],
                         cdf_surface: Dict[str, np.ndarray],
                         x_surface: Dict[str, np.ndarray]) -> Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray]]:
    """
    Center distributions so their peaks (modes) are at x=0 while maintaining the same domain.

    This function shifts each distribution so that its mode (peak) is at x=0,
    without changing the domain range. It uses interpolation to recalculate
    the PDF and CDF values on the original domain.

    Parameters:
    -----------
    pdf_surface : Dict[str, np.ndarray]
        Dictionary of PDFs by maturity
    cdf_surface : Dict[str, np.ndarray]
        Dictionary of CDFs by maturity
    x_surface : Dict[str, np.ndarray]
        Dictionary of x-domains by maturity

    Returns:
    --------
    Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray]]
        (centered_pdf_surface, centered_cdf_surface)
    """
    centered_pdf_surface = {}
    centered_cdf_surface = {}

    for maturity in pdf_surface.keys():
        pdf = pdf_surface[maturity]
        cdf = cdf_surface[maturity]
        x = x_surface[maturity]

        # Find the mode (peak) of the distribution
        mode_idx = np.argmax(pdf)
        mode = x[mode_idx]

        # Create interpolation functions for the original distributions
        f_pdf = interpolate.interp1d(x, pdf, bounds_error=False, fill_value=0)
        f_cdf = interpolate.interp1d(x, cdf, bounds_error=False, fill_value=0)

        # Evaluate the centered distributions on the original domain
        # g(x) = f(x + mode) shifts the distribution so that the peak is at x=0
        centered_pdf_surface[maturity] = f_pdf(x + mode)
        centered_cdf_surface[maturity] = f_cdf(x + mode)

    return centered_pdf_surface, centered_cdf_surface
