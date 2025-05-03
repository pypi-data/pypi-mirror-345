"""
Volatility models for the Voly package.
"""

import numpy as np
from numpy.linalg import solve
from typing import Tuple, Dict, List, Optional, Union
from voly.utils.logger import logger
from scipy.optimize import minimize
from sklearn.metrics import mean_squared_error


class SVIModel:
    """
    Stochastic Volatility Inspired (SVI) model.
    """

    # Parameter names for reference
    PARAM_NAMES = ['a', 'b', 'm', 'rho', 'sigma']
    JW_PARAM_NAMES = ['nu', 'psi', 'p', 'c', 'nu_tilde']

    # Parameter descriptions for documentation
    PARAM_DESCRIPTIONS = {
        'a': 'Base level of total implied variance',
        'b': 'Volatility skewness/smile modulation (controls wing slopes)',
        'm': 'Horizontal shift of the smile peak',
        'rho': 'Skewness/slope of the volatility smile (-1 to 1, rotates smile)',
        'sigma': 'Convexity control of the volatility smile (reduces ATM curvature)',
        'nu': 'ATM variance (level of ATM volatility)',
        'psi': 'ATM volatility skew (affects the gradient of the curve at ATM point)',
        'p': 'Slope of put wing (left side of curve)',
        'c': 'Slope of call wing (right side of curve)',
        'nu_tilde': 'Minimum implied total variance',
    }

    @staticmethod
    def svi(k, a, b, m, rho, sigma):
        """Compute SVI total implied variance."""
        assert b >= 0 and abs(rho) <= 1 and sigma >= 0 and a + b * sigma * np.sqrt(1 - rho ** 2) >= 0
        return a + b * (rho * (k - m) + np.sqrt((k - m) ** 2 + sigma ** 2))

    @staticmethod
    def svi_d(k, b, m, rho, sigma):
        """Compute the derivative of SVI over K"""
        return b * (rho + (k - m) / np.sqrt((k - m) ** 2 + sigma ** 2))

    @staticmethod
    def svi_dd(k, b, m, sigma):
        """Compute the second derivative of SVI over K"""
        return b * sigma ** 2 / ((k - m) ** 2 + sigma ** 2) ** (3 / 2)

    @staticmethod
    def svi_min_strike(sigma, rho, m):
        """Calculate the minimum valid log-strike for this SVI parameterization."""
        return m - ((sigma * rho) / np.sqrt(1 - rho ** 2))

    @staticmethod
    def raw_to_jw_params(a, b, m, rho, sigma, t):
        """Convert raw SVI to Jump-Wing parameters."""
        nu = (a + b * ((-rho) * m + np.sqrt(m ** 2 + sigma ** 2))) / t
        sqrt_nu_t = np.sqrt(nu * t)
        psi = (1 / sqrt_nu_t) * (b / 2) * (rho - (m / np.sqrt(m ** 2 + sigma ** 2)))
        p = (1 / sqrt_nu_t) * b * (1 - rho)
        c = (1 / sqrt_nu_t) * b * (1 + rho)
        nu_tilde = (1 / t) * (a + b * sigma * np.sqrt(1 - rho ** 2))
        return nu, psi, p, c, nu_tilde

    @staticmethod
    def loss(tiv, vega, y, c, d, a):
        """Compute weighted mean squared error for calibration."""
        diff = tiv - (a + d * y + c * np.sqrt(y * y + 1))
        return (vega * diff * diff).mean()

    @classmethod
    def calibration(cls, tiv, vega, k, m, sigma):
        """Calibrate c, d, a parameters given m and sigma."""
        sigma = max(sigma, 0.001)
        vega = vega / vega.max() if vega.max() > 0 else np.ones_like(vega)
        y = (k - m) / sigma

        # Calculate means for matrix construction
        w = vega.mean()
        y1 = (vega * y).mean()
        y2 = (vega * y * y).mean()
        y3 = (vega * np.sqrt(y * y + 1)).mean()
        y4 = (vega * y * np.sqrt(y * y + 1)).mean()
        y5 = (vega * (y * y + 1)).mean()
        vy2 = (vega * tiv * np.sqrt(y * y + 1)).mean()
        vy = (vega * tiv * y).mean()
        v = (vega * tiv).mean()

        # Solve the linear system
        matrix = np.array([[y5, y4, y3], [y4, y2, y1], [y3, y1, w]])
        vector = np.array([vy2, vy, v])
        c, d, a = solve(matrix, vector)

        # Clip parameters to ensure validity
        c = np.clip(c, 0, 4 * sigma)
        a = max(a, 1e-6)
        d = np.clip(d, -min(c, 4 * sigma - c), min(c, 4 * sigma - c))

        return c, d, a, cls.loss(tiv, vega, y, c, d, a)

    @classmethod
    def fit(cls, tiv, vega, k, tau=1.0):
        """Fit SVI model."""
        if len(k) <= 5:
            return [np.nan] * 5, np.inf

        vega = vega / vega.max() if vega.max() > 0 else np.ones_like(vega)
        m_init = np.mean(k)
        sigma_init = max(0.1, np.std(k) * 0.1)

        result = minimize(
            lambda params: cls.calibration(tiv, vega, k, params[1], params[0])[3],
            [sigma_init, m_init],
            bounds=[(0.001, None), (None, None)],
            tol=1e-16, method="SLSQP", options={'maxfun': 5000}
        )

        sigma, m = result.x
        c, d, a_calib, loss = cls.calibration(tiv, vega, k, m, sigma)
        a_calib = max(a_calib, 1e-6)

        # Convert to SVI parameters
        if c != 0:
            a_svi = a_calib / tau
            rho_svi = d / c
            b_svi = c / (sigma * tau)
        else:
            a_svi = a_calib / tau
            rho_svi = b_svi = 0

        return [a_svi, b_svi, m, rho_svi, sigma], loss

    @classmethod
    def correct_calendar_arbitrage(cls, params, t, tiv, vega, k, prev_params, prev_t, k_constraint):
        """Correct calendar arbitrage with relaxed bounds."""
        if np.any(np.isnan(params)) or np.any(np.isnan(prev_params)):
            return params

        a_init, b_init, m_init, rho_init, sigma_init = params
        a_prev, b_prev, m_prev, rho_prev, sigma_prev = prev_params

        def objective(x):
            a, b, m, rho, sigma = x
            w_model = cls.svi(k, a * t, b * t, m, rho, sigma)
            fit_loss = mean_squared_error(tiv, w_model, sample_weight=vega)
            param_deviation = sum(((x[i] - x_init) / max(abs(x_init), 1e-6)) ** 2
                                  for i, x_init in enumerate([a_init, b_init, m_init, rho_init, sigma_init]))
            return fit_loss + 0.01 * param_deviation

        bounds = [
            (max(a_init * 0.8, 1e-6), a_init * 1.2),
            (max(b_init * 0.8, 0), b_init * 1.2),
            (m_init - 0.05, m_init + 0.05),
            (max(rho_init - 0.05, -1), min(rho_init + 0.05, 1)),
            (max(sigma_init * 0.8, 1e-6), sigma_init * 1.2)
        ]

        constraints = [
            {'type': 'ineq', 'fun': lambda x: cls.svi(k_constraint, x[0] * t, x[1] * t, x[2], x[3], x[4]) -
                                              cls.svi(k_constraint, a_prev * prev_t, b_prev * prev_t, m_prev, rho_prev,
                                                      sigma_prev)},
            {'type': 'ineq', 'fun': lambda x: x[0] + x[1] * x[4] * np.sqrt(1 - x[3] ** 2)}
        ]

        result = minimize(
            objective, [a_init, b_init, m_init, rho_init, sigma_init],
            bounds=bounds, constraints=constraints, method='SLSQP',
            options={'disp': False, 'maxiter': 1000, 'ftol': 1e-8}
        )

        if result.success:
            new_params = result.x
            w_current = cls.svi(k_constraint, new_params[0] * t, new_params[1] * t, *new_params[2:])
            w_prev = cls.svi(k_constraint, a_prev * prev_t, b_prev * prev_t, m_prev, rho_prev, sigma_prev)
            violation = np.min(w_current - w_prev)
            logger.info(f"Calendar arb correction {'fixed' if violation >= -1e-6 else 'failed'} for t={t:.4f}, "
                        f"min margin={violation:.6f}")
            return new_params

        logger.error(f"Calendar arb correction failed for t={t:.4f}")
        return params

    @classmethod
    def check_butterfly_arbitrage(cls, a, b, m, rho, sigma, k_range):
        """Check for butterfly arbitrage violations."""
        for k_val in k_range:
            w_k = cls.svi(k_val, a, b, m, rho, sigma)
            w_d_k = cls.svi_d(k_val, b, m, rho, sigma)
            w_dd_k = cls.svi_dd(k_val, b, m, sigma)
            g = (1 - (k_val * w_d_k) / (2 * w_k)) ** 2 - (w_d_k ** 2) / 4 * (1 / w_k + 1 / 4) + w_dd_k / 2
            if g < 0:
                return False
        return True

    @classmethod
    def check_calendar_arbitrage(cls, sorted_maturities, params_dict, groups, s, num_points):
        """Check for calendar arbitrage violations."""
        for i in range(len(sorted_maturities) - 1):
            mat1, mat2 = sorted_maturities[i], sorted_maturities[i + 1]
            t1, params1 = params_dict[mat1]
            t2, params2 = params_dict[mat2]
            a1, b1, m1, rho1, sigma1 = params1
            a2, b2, m2, rho2, sigma2 = params2

            if np.isnan(a1) or np.isnan(a2):
                continue

            # Get strike range for checking
            group = groups.get_group(mat2)
            K = group['strikes'].values
            k_market = np.log(K / s)
            mask = ~np.isnan(k_market)
            k_check = np.unique(
                np.concatenate([k_market[mask], np.linspace(min(k_market[mask]), max(k_market[mask]), num_points)]))

            # Check for violations
            for k_val in k_check:
                w1 = cls.svi(k_val, a1 * t1, b1 * t1, m1, rho1, sigma1)
                w2 = cls.svi(k_val, a2 * t2, b2 * t2, m2, rho2, sigma2)
                if w2 < w1 - 1e-6:
                    logger.warning(
                        f"Calendar arb violation at t1={t1:.4f}, t2={t2:.4f}, k={k_val:.4f}: w1={w1:.6f}, w2={w2:.6f}")
                    return False
        return True


# Models dictionary for easy access
MODELS = {
    'svi': SVIModel,
}
