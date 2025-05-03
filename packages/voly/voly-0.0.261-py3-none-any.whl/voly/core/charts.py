"""
Visualization module for the Voly package.

This module provides visualization functions for volatility surfaces,
risk-neutral densities, and model fitting results.
"""

import numpy as np
import pandas as pd
from scipy import interpolate
from typing import Dict, List, Tuple, Optional, Union, Any
from voly.utils.logger import logger, catch_exception
from voly.models import SVIModel
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

# Set default renderer to browser for interactive plots
pio.renderers.default = "browser"


@catch_exception
def plot_volatility_smile(x_array: np.ndarray,
                          iv_array: np.ndarray,
                          option_chain: pd.DataFrame = None,
                          maturity: Optional[str] = None,
                          return_domain: str = 'log_moneyness') -> go.Figure:
    """
    Plot volatility smile for a single expiry.

    Parameters:
    - x_array: Array of x-axis values in the specified domain
    - iv_array: Implied volatility values
    - option_chain: Optional market data for comparison
    - maturity: Maturity name for filtering market data
    - return_domain: Type of x-domain ('log_moneyness', 'moneyness', 'strikes', 'delta')

    Returns:
    - Plotly figure
    """

    # Map domain types to axis labels
    domain_labels = {
        'log_moneyness': 'Log Moneyness',
        'moneyness': 'Moneyness',
        'returns': 'Returns',
        'strikes': 'Strike Price',
        'delta': 'Delta'
    }

    fig = go.Figure()

    # Add model curve
    fig.add_trace(
        go.Scatter(
            x=x_array,
            y=iv_array * 100,  # Convert to percentage
            mode='lines',
            name='Model',
            line=dict(color='#0080FF', width=2)
        )
    )

    # Add market data if provided
    if option_chain is not None and maturity is not None:
        currency = option_chain['currency'].iloc[0]
        maturity_data = option_chain[option_chain['maturity'] == maturity]
        if return_domain == 'delta':
            maturity_data = maturity_data[maturity_data['flag'] == 'C']

        if not maturity_data.empty:
            # Add bid and ask IVs if available
            for iv_type in ['bid_iv', 'ask_iv']:
                if iv_type in maturity_data.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=maturity_data[return_domain],
                            y=maturity_data[iv_type] * 100,  # Convert to percentage
                            mode='markers',
                            name=iv_type.replace('_', ' ').upper(),
                            marker=dict(size=8, symbol='circle', opacity=0.7)
                        )
                    )

            title = f'{currency} - Vol Smile for {maturity}'
        else:
            title = f'{currency} - Vol Smile for {maturity}'
    else:
        title = 'Volatility Smile'

    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title=domain_labels.get(return_domain, 'X Domain'),
        yaxis_title='Implied Volatility (%)',
        template='plotly_dark',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )

    return fig


@catch_exception
def plot_all_smiles(x_surface: Dict[str, np.ndarray],
                    iv_surface: Dict[str, np.ndarray],
                    option_chain: Optional[pd.DataFrame] = None,
                    return_domain: str = 'log_moneyness') -> List[go.Figure]:
    """
    Plot volatility smiles for all expiries.

    Parameters:
    - x_surface: Dictionary mapping maturity names to x-domain arrays
    - iv_surface: Dictionary mapping maturity names to IV arrays
    - option_chain: Optional market data for comparison
    - return_domain: Type of x-domain ('log_moneyness', 'moneyness', 'strikes', 'delta')

    Returns:
    - List of Plotly figures
    """
    return [
        plot_volatility_smile(
            x_array=x_surface[maturity],
            iv_array=iv_surface[maturity],
            option_chain=option_chain,
            maturity=maturity,
            return_domain=return_domain
        )
        for maturity in iv_surface.keys()
    ]


@catch_exception
def plot_raw_parameters(fit_results: pd.DataFrame) -> go.Figure:
    """
    Plot raw SVI parameters across different expiries.

    Parameters:
    - fit_results: DataFrame from fit_model() with maturity names as index

    Returns:
    - Plotly figure
    """
    # Select parameters to plot
    param_names = ['a', 'b', 'm', 'rho', 'sigma']

    # Create subplots
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=[f"Parameter {p}: {SVIModel.PARAM_DESCRIPTIONS.get(p, '')}"
                        for p in param_names] + ['']
    )

    # Get maturity names from index
    maturities = fit_results.index

    # Create hover text with maturity info
    tick_labels = [f"{m}" for m in maturities]

    # Plot each parameter
    for i, param in enumerate(param_names):
        row, col = (i // 2) + 1, (i % 2) + 1

        fig.add_trace(
            go.Scatter(
                x=list(range(len(maturities))),
                y=fit_results[param],
                mode='lines+markers',
                name=param,
                line=dict(width=2),
                marker=dict(size=8),
                text=tick_labels,
                hovertemplate="%{text}<br>%{y:.4f}"
            ),
            row=row, col=col
        )

        # Set x-axis labels
        fig.update_xaxes(
            tickvals=list(range(len(maturities))),
            ticktext=maturities,
            tickangle=45,
            row=row, col=col
        )

    # Update layout
    fig.update_layout(
        title='Raw SVI Parameters Across Maturities',
        template='plotly_dark',
        showlegend=False
    )

    return fig


@catch_exception
def plot_jw_parameters(fit_results: pd.DataFrame) -> go.Figure:
    """
    Plot Jump-Wing parameters across different expiries.

    Parameters:
    - fit_results: DataFrame from fit_model() with maturity names as index

    Returns:
    - Plotly figure
    """
    # Select parameters to plot
    param_names = ['nu', 'psi', 'p', 'c', 'nu_tilde']

    # Create subplots
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=[f"Parameter {p}: {SVIModel.PARAM_DESCRIPTIONS.get(p, '')}"
                        for p in param_names] + ['']
    )

    # Get maturity names from index
    maturities = fit_results.index

    # Create hover text with maturity info
    tick_labels = [f"{m}" for m in maturities]

    # Plot each parameter
    for i, param in enumerate(param_names):
        row, col = (i // 2) + 1, (i % 2) + 1

        fig.add_trace(
            go.Scatter(
                x=list(range(len(maturities))),
                y=fit_results[param],
                mode='lines+markers',
                name=param,
                line=dict(width=2),
                marker=dict(size=8),
                text=tick_labels,
                hovertemplate="%{text}<br>%{y:.4f}"
            ),
            row=row, col=col
        )

        # Set x-axis labels
        fig.update_xaxes(
            tickvals=list(range(len(maturities))),
            ticktext=maturities,
            tickangle=45,
            row=row, col=col
        )

    # Update layout
    fig.update_layout(
        title='Jump-Wing Parameters Across Maturities',
        template='plotly_dark',
        showlegend=False
    )

    return fig


@catch_exception
def plot_fit_performance(fit_results: pd.DataFrame) -> go.Figure:
    """
    Plot the fitting accuracy statistics.

    Parameters:
    - fit_results: DataFrame from fit_model() with maturity names as index

    Returns:
    - Plotly figure
    """
    # Define metrics to plot
    metrics = {
        'rmse': {'title': 'RMSE by Expiry', 'row': 1, 'col': 1, 'ylabel': 'RMSE (%)', 'scale': 100},
        'mae': {'title': 'MAE by Expiry', 'row': 1, 'col': 2, 'ylabel': 'MAE (%)', 'scale': 100},
        'r2': {'title': 'R² by Expiry', 'row': 2, 'col': 1, 'ylabel': 'R²', 'scale': 1},
        'max_error': {'title': 'Max Error by Expiry', 'row': 2, 'col': 2, 'ylabel': 'Max Error (%)', 'scale': 100}
    }

    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[metrics[m]['title'] for m in metrics]
    )

    # Get maturity names from index and create x-axis indices
    maturities = fit_results.index
    x_indices = list(range(len(maturities)))

    # Create hover labels
    hover_labels = [f"{m}" for m in maturities]

    # Plot each metric
    for metric, config in metrics.items():
        fig.add_trace(
            go.Scatter(
                x=x_indices,
                y=fit_results[metric] * config['scale'],
                mode='lines+markers',
                name=metric.upper(),
                line=dict(width=2),
                marker=dict(size=8),
                text=hover_labels,
                hovertemplate="%{text}<br>%{y:.4f}"
            ),
            row=config['row'], col=config['col']
        )

        # Update axes
        fig.update_yaxes(title_text=config['ylabel'], row=config['row'], col=config['col'])

    # Set x-axis labels for all subplots
    for row in range(1, 3):
        for col in range(1, 3):
            fig.update_xaxes(
                tickvals=x_indices,
                ticktext=maturities,
                tickangle=45,
                row=row, col=col
            )

    # Update layout
    fig.update_layout(
        title='Model Fitting Accuracy Statistics',
        template='plotly_dark',
        showlegend=False
    )

    return fig


@catch_exception
def plot_3d_surface(x_surface: Dict[str, np.ndarray],
                    iv_surface: Dict[str, np.ndarray],
                    fit_results: pd.DataFrame = None,
                    return_domain: str = 'log_moneyness') -> go.Figure:
    """
    Plot 3D implied volatility surface.

    Parameters:
    - x_surface: Dictionary mapping maturity names to x-domain arrays
    - iv_surface: Dictionary mapping maturity names to IV arrays
    - fit_results: Optional DataFrame with maturity information
    - return_domain: Type of x-domain ('log_moneyness', 'moneyness', 'strikes', 'delta')

    Returns:
    - Plotly figure
    """

    # Map domain types to axis labels
    domain_labels = {
        'log_moneyness': 'Log Moneyness',
        'moneyness': 'Moneyness',
        'returns': 'Returns',
        'strikes': 'Strike Price',
        'delta': 'Delta'
    }

    # Get maturity names and sort by YTM
    maturities = list(iv_surface.keys())
    if fit_results is not None:
        maturity_values = [fit_results.loc[name, 't'] for name in maturities]
        # Sort by maturity
        sorted_indices = np.argsort(maturity_values)
        maturities = [maturities[i] for i in sorted_indices]
        maturity_values = [maturity_values[i] for i in sorted_indices]
    else:
        maturity_values = list(range(len(maturities)))

    # Create a common x-grid for all maturities
    # Use 100 points between the min and max x-values across all maturities
    all_x = np.concatenate([x_surface[m] for m in maturities])
    x_min, x_max = np.min(all_x), np.max(all_x)
    x_grid = np.linspace(x_min, x_max, 400)

    # Create a matrix for the surface
    z_matrix = np.zeros((len(maturities), len(x_grid)))

    # Fill the matrix with interpolated IV values
    for i, maturity in enumerate(maturities):
        x_values = x_surface[maturity]
        iv_values = iv_surface[maturity] * 100  # Convert to percentage

        # Create interpolation function
        f = interpolate.interp1d(x_values, iv_values, kind='cubic',
                                 bounds_error=False, fill_value='extrapolate')

        # Generate interpolated values for the common x-grid
        z_matrix[i] = f(x_grid)

    # Create figure with the surface
    fig = go.Figure(data=[go.Surface(
        z=z_matrix,
        x=x_grid,
        y=maturity_values,
        colorscale='Plotly3'
    )])

    # Add contours
    fig.update_traces(contours_z=dict(
        show=True,
        usecolormap=True,
        highlightcolor="white",
        project_z=True
    ))

    # Update layout
    fig.update_layout(
        title='Implied Volatility Surface',
        template='plotly_dark',
        scene=dict(
            xaxis_title=domain_labels.get(return_domain, 'X Domain'),
            yaxis_title='Years to Expiry',
            zaxis_title='Implied Volatility (%)',
            aspectratio=dict(x=1, y=1, z=0.7)
        ),
        scene_camera_eye=dict(x=1, y=-2, z=0.5)
    )

    return fig
