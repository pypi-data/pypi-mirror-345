# Voly - Options & Volatility Research Package

Voly is a Python package for options data analysis, volatility surface modeling, and risk-neutral density estimation. It provides a simple interface for handling common options research tasks, including data collection, model fitting, and visualization.

## Features

- **Data Collection**: Fetch options data from exchanges (currently supports Deribit)
- **Volatility Surface Modeling**: Fit SVI (Stochastic Volatility Inspired) model to market data
- **Risk-Neutral Density**: Calculate and analyze risk-neutral density distributions
- **Surface Interpolation**: Interpolate volatility surfaces across different expiries
- **Options Pricing & Greeks**: Calculate Black-Scholes prices and all major Greeks
- **Visualizations**: Generate interactive plots using Plotly

## Installation

You can install Voly using pip:

```bash
pip install voly
```

## Quick Start

```python
import pandas as pd
from voly import VolyClient

# Initialize the client
voly = VolyClient()

# Fetch options data (or load your own data)
option_chain = voly.get_option_chain(exchange='deribit', currency='BTC')

# Fit an SVI model to the data with visualization
fit_results = voly.fit_model(option_chain, plot=True)

# Calculate risk-neutral density
rnd_results = voly.rnd(fit_results, spot_price=option_chain['underlying_price'].iloc[0], plot=True)

# Calculate probability of price above a target
probability = voly.probability(rnd_results, target_price=32000, direction='above')
print(f"Probability of price above 32000: {probability:.2%}")

# Calculate option Greeks
greeks = voly.greeks(s=30000, k=32000, r=0.05, vol=0.6, t=0.25, option_type='call')
print(f"Option Greeks: {greeks}")
```

## Example: Visualizing the Volatility Surface

```python
import pandas as pd
from voly import VolyClient

# Initialize the client
voly = VolyClient()

# Load your own data or fetch from exchange
# The DataFrame should have columns for:
# - log_moneyness
# - strike
# - mark_iv (implied volatility)
# - yte (years to expiry)
# - dte (days to expiry)
# - maturity_name (identifier for the expiry)
data = pd.read_csv('your_options_data.csv')

# Fit the SVI model
fit_results = voly.fit_model(data, plot=True)

# Display the 3D volatility surface
surface_fig = fit_results['plots']['surface_3d']
surface_fig.show()
```

## Documentation

For full documentation, visit [https://docs.voly.io](https://docs.voly.io)

## Development

### Setting up the development environment

```bash
# Clone the repository
git clone https://github.com/manudc22/voly.git
cd voly

# Install development dependencies & activate venv
./env_setup.sh --all
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.