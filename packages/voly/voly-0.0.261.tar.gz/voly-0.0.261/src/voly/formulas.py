"""
Option pricing formulas and general calculations.
"""

import pandas as pd
import numpy as np
from scipy.stats import norm
from py_vollib.black_scholes.implied_volatility import implied_volatility
from typing import Tuple, Dict, Union, List, Optional
from voly.utils.logger import catch_exception
from voly.exceptions import VolyError
from functools import wraps


@catch_exception
def vectorize_inputs(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Extract input argument names from the function
        arg_names = func.__code__.co_varnames[:func.__code__.co_argcount]
        input_dict = dict(zip(arg_names, args))
        input_dict.update(kwargs)

        values = list(input_dict.values())

        n_vectors = sum(isinstance(v, (list, np.ndarray, pd.Series)) for v in values)
        n_scalars = sum(not isinstance(v, (list, np.ndarray, pd.Series)) for v in values)

        if n_vectors > 0 and n_scalars > 0:
            raise VolyError("Cannot mix scalar and vector inputs. Pass all as vectors or all as scalars.")

        if n_vectors > 0:
            # All inputs are vectors, make sure they're same length
            lengths = [len(v) for v in values]
            if len(set(lengths)) != 1:
                raise VolyError("All vectorized inputs must have the same length.")

            # Apply vectorized logic
            return [
                func(*[input_dict[name][i] for name in arg_names])
                for i in range(lengths[0])
            ]

        # All inputs are scalars
        return func(*args, **kwargs)

    return wrapper


@catch_exception
@vectorize_inputs
def d1(s: float, K: float, r: float, o: float, t: float, flag: str = 'call') -> float:
    # flag is ignored in this function but included for compatibility
    return (np.log(s / K) + (r + o ** 2 / 2) * t) / (o * np.sqrt(t))


@catch_exception
@vectorize_inputs
def d2(s: float, K: float, r: float, o: float, t: float, flag: str = 'call') -> float:
    # flag is ignored in this function but included for compatibility
    return d1(s, K, r, o, t, flag) - o * np.sqrt(t)


@catch_exception
@vectorize_inputs
def bs(s: float, K: float, r: float, o: float, t: float, flag: str = 'call') -> float:
    d1_val = d1(s, K, r, o, t)
    d2_val = d2(s, K, r, o, t)

    if flag.lower() in ["call", "c"]:
        return s * norm.cdf(d1_val) - K * np.exp(-r * t) * norm.cdf(d2_val)
    else:  # put
        return K * np.exp(-r * t) * norm.cdf(-d2_val) - s * norm.cdf(-d1_val)


@catch_exception
@vectorize_inputs
def delta(s: float, K: float, r: float, o: float, t: float, flag: str = 'call') -> float:
    d1_val = d1(s, K, r, o, t)

    if flag.lower() in ["call", "c"]:
        return norm.cdf(d1_val)
    else:  # put
        return norm.cdf(d1_val) - 1.0


@catch_exception
@vectorize_inputs
def gamma(s: float, K: float, r: float, o: float, t: float, flag: str = 'call') -> float:
    d1_val = d1(s, K, r, o, t, flag)
    return norm.pdf(d1_val) / (s * o * np.sqrt(t)) * 10000


@catch_exception
@vectorize_inputs
def vega(s: float, K: float, r: float, o: float, t: float, flag: str = 'call') -> float:
    d1_val = d1(s, K, r, o, t, flag)
    return s * norm.pdf(d1_val) * np.sqrt(t) / 100  # Divided by 100 for 1% change


@catch_exception
@vectorize_inputs
def theta(s: float, K: float, r: float, o: float, t: float, flag: str = 'call') -> float:
    d1_val = d1(s, K, r, o, t, flag)
    d2_val = d2(s, K, r, o, t, flag)

    # First part of theta (same for both call and put)
    theta_part1 = -s * norm.pdf(d1_val) * o / (2 * np.sqrt(t))

    # Second part depends on option type
    if flag.lower() in ["call", "c"]:
        theta_part2 = -r * K * np.exp(-r * t) * norm.cdf(d2_val)
    else:  # put
        theta_part2 = r * K * np.exp(-r * t) * norm.cdf(-d2_val)

    # Return theta per day (t is in years)
    return (theta_part1 + theta_part2) / 365.0


@catch_exception
@vectorize_inputs
def rho(s: float, K: float, r: float, o: float, t: float, flag: str = 'call') -> float:
    d2_val = d2(s, K, r, o, t, flag)

    if flag.lower() in ["call", "c"]:
        return K * t * np.exp(-r * t) * norm.cdf(d2_val) / 100
    else:  # put
        return -K * t * np.exp(-r * t) * norm.cdf(-d2_val) / 100


@catch_exception
@vectorize_inputs
def vanna(s: float, K: float, r: float, o: float, t: float, flag: str = 'call') -> float:
    d1_val = d1(s, K, r, o, t, flag)
    d2_val = d2(s, K, r, o, t, flag)

    return -norm.pdf(d1_val) * d2_val / o


@catch_exception
@vectorize_inputs
def volga(s: float, K: float, r: float, o: float, t: float, flag: str = 'call') -> float:
    d1_val = d1(s, K, r, o, t, flag)
    d2_val = d2(s, K, r, o, t, flag)

    return s * norm.pdf(d1_val) * np.sqrt(t) * d1_val * d2_val / o


@catch_exception
@vectorize_inputs
def charm(s: float, K: float, r: float, o: float, t: float, flag: str = 'call') -> float:
    d1_val = d1(s, K, r, o, t, flag)
    d2_val = d2(s, K, r, o, t, flag)

    # First term is the same for calls and puts
    term1 = -norm.pdf(d1_val) * d1_val / (2 * t)

    # Second term depends on option type
    if flag.lower() in ["call", "c"]:
        term2 = -r * np.exp(-r * t) * norm.cdf(d2_val)
    else:  # put
        term2 = r * np.exp(-r * t) * norm.cdf(-d2_val)

    # Return charm per day (t is in years)
    return (term1 + term2) / 365.25


@catch_exception
@vectorize_inputs
def greeks(s: float, K: float, r: float, o: float, t: float,
           flag: str = 'call') -> Dict[str, float]:
    return {
        'price': bs(s, K, r, o, t, flag),
        'delta': delta(s, K, r, o, t, flag),
        'gamma': gamma(s, K, r, o, t, flag),
        'vega': vega(s, K, r, o, t, flag),
        'theta': theta(s, K, r, o, t, flag),
        'rho': rho(s, K, r, o, t, flag),
        'vanna': vanna(s, K, r, o, t, flag),
        'volga': volga(s, K, r, o, t, flag),
        'charm': charm(s, K, r, o, t, flag)
    }


@catch_exception
@vectorize_inputs
def iv(option_price: float, s: float, K: float, r: float, t: float,
       flag: str = 'call') -> float:
    """
    Calculate implied volatility using py_volib for vectorized computation.

    Parameters:
    - option_price: Market price of the option
    - s: Underlying price
    - K: Strike price
    - r: Risk-free rate
    - t: Time to expiry in years
    - flag: 'call' or 'put'

    Returns:
    - Implied volatility
    """

    # Check if option price is within theoretical bounds
    if flag.lower() in ["call", "c"]:
        intrinsic = max(0, s - K * np.exp(-r * t))
        if option_price < intrinsic:
            return np.nan  # Price below intrinsic value
        if option_price >= s:
            return np.inf  # Price exceeds underlying
    else:  # put
        intrinsic = max(0, K * np.exp(-r * t) - s)
        if option_price < intrinsic:
            return np.nan  # Price below intrinsic value
        if option_price >= K:
            return np.inf  # Price exceeds strike

    flag = 'c' if flag.lower() in ["call", "c"] else 'p'

    iv_value = implied_volatility(
        price=option_price,
        S=s,
        K=K,
        t=t,
        r=r,
        flag=flag
    )
    return iv_value


@catch_exception
def get_domain(domain_params: Tuple[float, float, int] = (-1.5, 1.5, 1000),
               s: float = None,
               r: float = None,
               o: np.ndarray = None,
               t: float = None,
               return_domain: str = 'log_moneyness') -> np.ndarray:
    """
    Compute the x-domain for a given return type (log-moneyness, moneyness, returns, strikes, or delta).

    Parameters:
    -----------
    domain_params : Tuple[float, float, int],
        Parameters for log-moneyness domain: (min_log_moneyness, max_log_moneyness, num_points).
        Default is (-1.5, 1.5, 1000).
    s : float, optional
        Spot price of the underlying asset. Required for 'strikes' and 'delta' domains.
    r : float, optional
        Risk-free interest rate. Required for 'delta' domain.
    o : np.ndarray, optional
        Array of implied volatilities. Required for 'delta' domain.
    t : float, optional
        Time to maturity in years. Required for 'delta' domain.
    return_domain : str, optional
        The desired domain to return. Options are 'log_moneyness', 'moneyness', 'returns' 'strikes', or 'delta'.
        Default is 'log_moneyness'.

    Returns:
    --------
    np.ndarray
        The x-domain array corresponding to the specified return_domain.

    Raises:
    -------
    ValueError
        If required parameters are missing for the specified return_domain.
    """

    # Extract log-moneyness parameters and generate array
    LM = np.linspace(domain_params[0], domain_params[1], domain_params[2])

    # Handle different return domains
    if return_domain == 'log_moneyness':
        return LM

    elif return_domain == 'moneyness':
        return np.exp(LM)

    elif return_domain == 'returns':
        return np.exp(LM) - 1

    elif return_domain == 'strikes':
        if s is None:
            raise ValueError("Spot price 's' is required for return_domain='strikes'.")
        return np.exp(LM) * s

    elif return_domain == 'delta':
        # Check for required parameters
        required_params = {'s': s, 'r': r, 'o': o, 't': t}
        missing_params = [param for param, value in required_params.items() if value is None]
        if missing_params:
            raise ValueError(f"The following parameters are required for return_domain='delta': {missing_params}")

        if len(o) != len(LM):
            raise ValueError(
                f"'o' must have the same length as the log-moneyness array ({len(LM)})."
                f"Length 'o'={len(o)}, length 'LM'={len(LM)}")

        # Compute strikes
        K = np.exp(LM) * s

        # Compute deltas
        D = delta(s, K, r, o, t, 'call')
        return D

    else:
        raise ValueError(
            f"Invalid return_domain: {return_domain}. Must be one of ['log_moneyness', 'moneyness', 'returns', 'strikes', 'delta'].")
