"""
Data fetching and processing module for the Voly package.

This module handles fetching options data from exchanges and processing 
it into a standardized format for further analysis.
"""

import os
import asyncio
import websockets
import json
import pandas as pd
import requests
import time
import datetime as dt
import re
import numpy as np
from typing import List, Dict, Any, Optional, Union
from voly.formulas import (bs, delta, gamma, vega, theta, rho)
from voly.utils.logger import logger, catch_exception
from voly.exceptions import VolyError


async def subscribe_channels(ws, channels):
    """Helper function to subscribe to a list of channels"""
    await ws.send(json.dumps({
        "jsonrpc": "2.0",
        "method": "public/subscribe",
        "id": 42,
        "params": {"channels": channels}
    }))
    await ws.recv()  # Skip confirmation


async def unsubscribe_channels(ws, channels):
    """Helper function to unsubscribe from a list of channels"""
    await ws.send(json.dumps({
        "jsonrpc": "2.0",
        "method": "public/unsubscribe",
        "id": 43,
        "params": {"channels": channels}
    }))
    await ws.recv()  # Skip confirmation


@catch_exception
async def process_batch(ws, batch: List[str], batch_num: int, total_batches: int) -> List[Dict[str, Any]]:
    """Process a batch of instruments and return their data"""
    # Create channel subscriptions
    ticker_channels = [f"ticker.{instr}.100ms" for instr in batch]
    book_channels = [f"book.{instr}.100ms" for instr in batch]
    channels = ticker_channels + book_channels

    # Subscribe to channels
    await subscribe_channels(ws, channels)

    # Process batch responses
    data_count = 0
    needed_responses = len(batch) * 2  # Ticker and book for each instrument
    instrument_data = {}

    while data_count < needed_responses:
        try:
            response = await ws.recv()
            data = json.loads(response)

            if 'params' in data and 'data' in data['params'] and 'channel' in data['params']:
                channel = data['params']['channel']
                parts = channel.split('.')

                if len(parts) >= 2:
                    channel_type = parts[0]  # 'ticker' or 'book'
                    instr_name = parts[1]

                    if instr_name in batch:
                        if instr_name not in instrument_data:
                            instrument_data[instr_name] = {}

                        if channel_type not in instrument_data[instr_name]:
                            instrument_data[instr_name][channel_type] = data['params']['data']
                            data_count += 1

        except Exception as e:
            logger.error(f"Error in batch {batch_num}: {e}")
            break

    # Unsubscribe from channels
    await unsubscribe_channels(ws, channels)

    # Process data for this batch
    batch_results = []
    for instr_name, channels_data in instrument_data.items():
        row = {"instrument_name": instr_name}

        # Merge ticker data
        if 'ticker' in channels_data:
            ticker = channels_data['ticker']
            # Add basic fields
            for k, v in ticker.items():
                if k not in ['stats', 'greeks']:
                    row[k] = v

            # Flatten stats and greeks
            for nested_key in ['stats', 'greeks']:
                if nested_key in ticker and isinstance(ticker[nested_key], dict):
                    for k, v in ticker[nested_key].items():
                        row[k] = v

        # Merge book data
        if 'book' in channels_data:
            book = channels_data['book']
            # Add book fields that don't conflict with ticker
            for k, v in book.items():
                if k not in row and k not in ['bids', 'asks']:
                    row[k] = v

            # Store raw bids and asks
            if 'bids' in book:
                row['bids'] = book['bids']
            if 'asks' in book:
                row['asks'] = book['asks']

        batch_results.append(row)

    return batch_results


@catch_exception
async def get_deribit_data(currency: str = "BTC") -> pd.DataFrame:
    """
    Get options data with ticker and order book information from Deribit.

    Parameters:
    currency (str): Currency to fetch options for (default: "BTC")

    Returns:
    pandas.DataFrame: DataFrame with ticker and book data
    """
    total_start = time.time()

    # Get active options instruments
    logger.info(f"Fetching {currency} options...")
    try:
        response = requests.get(
            "https://www.deribit.com/api/v2/public/get_instruments",
            params={"currency": currency, "kind": "option", "expired": "false"}
        )
        response.raise_for_status()  # Raise exception for non-200 status codes
    except requests.RequestException as e:
        raise ConnectionError(f"Failed to connect to Deribit API: {str(e)}")

    try:
        instruments = [i['instrument_name'] for i in response.json()['result']]
    except (KeyError, json.JSONDecodeError) as e:
        raise VolyError(f"Failed to parse Deribit API response: {str(e)}")

    total_instruments = len(instruments)
    logger.info(f"Found {total_instruments} active {currency} options")

    # Calculate batches
    total_batches = (total_instruments + 100 - 1) // 100

    # Collect data
    all_data = []

    try:
        async with websockets.connect('wss://www.deribit.com/ws/api/v2') as ws:
            for i in range(0, total_instruments, 100):
                batch_num = i // 100 + 1
                batch = instruments[i:i + 100]

                batch_results = await process_batch(ws, batch, batch_num, total_batches)
                all_data.extend(batch_results)
    except (websockets.exceptions.WebSocketException, ConnectionError) as e:
        raise ConnectionError(f"WebSocket connection error: {str(e)}")

    total_time = time.time() - total_start
    logger.info(f"Total fetching time: {total_time:.2f}s")

    if not all_data:
        raise VolyError("No data collected from Deribit")

    return pd.DataFrame(all_data)


@catch_exception
def process_option_chain(df: pd.DataFrame, currency: str) -> pd.DataFrame:
    """
    Process raw option chain data into a standardized format.

    Parameters:
    df (pd.DataFrame): Raw option chain data
    currency (str): Currency code (e.g., 'BTC', 'ETH')

    Returns:
    pd.DataFrame: Processed option chain data
    """
    logger.info(f"Processing data for {currency}...")

    # Apply extraction to create new columns
    df['spot_price'] = df['index_price'].iloc[0]
    s = df['spot_price'].iloc[0]
    df['instrument'] = df['instrument_name']
    splits = df['instrument'].str.split('-')
    df['maturity'] = splits.str[1]
    if currency == 'XRP':
        df['strikes'] = splits.str[2].str.replace('d', '.', regex=False).astype(float)
    else:
        df['strikes'] = splits.str[2].astype(float)
    df['flag'] = splits.str[3]

    # Create maturity date at 8:00 AM UTC
    df['expiry'] = pd.to_datetime(df['maturity'].apply(
        lambda x: int(dt.datetime.strptime(x, "%d%b%y")
                      .replace(hour=8, minute=0, second=0, tzinfo=dt.timezone.utc)
                      .timestamp() * 1000)), unit='ms')

    # Get reference time from timestamp
    reference_time = dt.datetime.fromtimestamp(df['timestamp'].iloc[0] / 1000)

    # Calculate time to expiry in years
    df['t'] = ((df['expiry'] - reference_time).dt.total_seconds() / (24 * 60 * 60)) / 365.25

    # Calculate implied volatility (convert from percentage)
    df['mark_iv'] = df['mark_iv'] / 100
    df['bid_iv'] = df['bid_iv'].replace({0: np.nan}) / 100
    df['ask_iv'] = df['ask_iv'].replace({0: np.nan}) / 100

    df['mark_price'] = df['mark_price'] * s
    df['bid_price'] = df['best_bid_price'] * s
    df['ask_price'] = df['best_ask_price'] * s
    df['bid_amount'] = df['best_bid_amount']
    df['ask_amount'] = df['best_ask_amount']

    for idx, row in df.iterrows():
        # Process bid side
        if 'bids' in row and isinstance(row['bids'], list) and len(row['bids']) > 0:
            clean_bids = []  # Clean up the bid data
            for bid in row['bids']:
                if len(bid) >= 3:
                    # Extract price and quantity, removing 'new' if present
                    price = round(float(bid[1] * s) if bid[0] == 'new' else float(bid[0] * s), 8)
                    qty = round(float(bid[2]) if bid[0] == 'new' else float(bid[1]), 8)
                    clean_bids.append((price, qty))
            if clean_bids:
                df.at[idx, 'bids'] = clean_bids

        # Process ask side
        if 'asks' in row and isinstance(row['asks'], list) and len(row['asks']) > 0:
            clean_asks = []  # Clean up the ask data
            for ask in row['asks']:
                if len(ask) >= 3:
                    # Extract price and quantity, removing 'new' if present
                    price = round(float(ask[1] * s) if ask[0] == 'new' else float(ask[0] * s), 8)
                    qty = round(float(ask[2]) if ask[0] == 'new' else float(ask[1]), 8)
                    clean_asks.append((price, qty))
            if clean_asks:
                df.at[idx, 'asks'] = clean_asks

    df['bid_depth'] = df['bids']
    df['ask_depth'] = df['asks']

    df['bs'] = bs(df['spot_price'], df['strikes'], df['interest_rate'], df['mark_iv'], df['t'], df['flag'])
    df['delta'] = delta(df['spot_price'], df['strikes'], df['interest_rate'], df['mark_iv'], df['t'], df['flag'])
    df['gamma'] = gamma(df['spot_price'], df['strikes'], df['interest_rate'], df['mark_iv'], df['t'], df['flag'])
    df['vega'] = vega(df['spot_price'], df['strikes'], df['interest_rate'], df['mark_iv'], df['t'], df['flag'])
    df['theta'] = theta(df['spot_price'], df['strikes'], df['interest_rate'], df['mark_iv'], df['t'], df['flag'])
    df['rho'] = rho(df['spot_price'], df['strikes'], df['interest_rate'], df['mark_iv'], df['t'], df['flag'])

    df['open_interest'] = df['open_interest'] * s
    df['volume'] = df['volume'] * s

    df = df[['currency', 'spot_price',
             'timestamp', 'instrument', 'maturity', 'strikes', 'flag', 'expiry', 't',
             'mark_iv', 'bid_iv', 'ask_iv', 'mark_price', 'bid_price', 'ask_price', 'bid_amount', 'ask_amount', 'bid_depth', 'ask_depth',
             'bs', 'delta', 'gamma', 'vega', 'theta', 'rho',
             'interest_rate', 'open_interest', 'volume']]

    logger.info(f"Processing complete!")

    return df


@catch_exception
async def fetch_option_chain(exchange: str = 'deribit',
                             currency: str = 'BTC') -> pd.DataFrame:
    """
    Fetch option chain data from the specified exchange.

    Parameters:
    exchange (str): Exchange to fetch data from (currently only 'deribit' is supported)
    currency (str): Currency to fetch options for (e.g., 'BTC', 'ETH')

    Returns:
    pd.DataFrame: Processed option chain data
    """
    if exchange.lower() != 'deribit':
        raise VolyError(f"Exchange '{exchange}' is not supported. Currently only 'deribit' is available.")

    # Get raw data
    if currency not in ['BTC', 'ETH']:
        new_currency = 'USDC'
        raw_data = await get_deribit_data(currency=new_currency)
        raw_data['currency'] = raw_data['instrument_name'].str.split('-').str[0].str.split('_').str[0]
        raw_data = raw_data[raw_data['currency'] == currency]
    else:
        raw_data = await get_deribit_data(currency=currency)
        raw_data['currency'] = currency

    # Process data
    processed_data = process_option_chain(raw_data, currency)

    return processed_data
