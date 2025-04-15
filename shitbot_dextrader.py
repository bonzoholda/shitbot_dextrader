import os
import time
import numpy as np
import pandas as pd
from web3 import Web3
from web3.exceptions import TimeExhausted, TransactionNotFound
from cryptography.fernet import Fernet
from web3 import Web3
from fastapi import FastAPI

#import from binance related
from binance.client import Client
from binance.enums import *
import requests
import gc

session = requests.Session()
# Use the session
session.close()  # Release resources


#pip install python-binance  ###dependency for bsc price feed, run first

app = FastAPI()

# ===================
# Load environment variables from .env file
# ===================
from dotenv import load_dotenv
load_dotenv()

# Retrieve API keys from environment variables
API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')
PRIVKEY = os.getenv('WALLET_PRIVKEY')
ADDRESS = os.getenv('WALLET_ADDRESS')

# ===================
# Define the RPC URL and Chainlink oracle contract details
# ===================
RPC_URL = "https://polygon.meowrpc.com"  # Replace with your RPC endpoint
CHAINLINK_ORACLE_ADDRESS = "0xAB594600376Ec9fD91F8e885dADF0CE036862dE0"  # Example: MATIC/USD on Polygon
CHAINLINK_ABI = [
    {
        "inputs": [],
        "name": "latestRoundData",
        "outputs": [
            {"internalType": "uint80", "name": "roundId", "type": "uint80"},
            {"internalType": "int256", "name": "answer", "type": "int256"},
            {"internalType": "uint256", "name": "startedAt", "type": "uint256"},
            {"internalType": "uint256", "name": "updatedAt", "type": "uint256"},
            {"internalType": "uint80", "name": "answeredInRound", "type": "uint80"},
        ],
        "stateMutability": "view",
        "type": "function",
    }
]

# =====================
# CONFIGURATION
# =====================

CHAINLINK_ORACLE_ADDRESS = "0xAB594600376Ec9fD91F8e885dADF0CE036862dE0"
WEB3_PROVIDER = RPC_URL
SLIPPAGE = 0.01  # 1%
RISK_REWARD_RATIO = (2, 3)
TRADE_FEE = 0.001  # 0.1%
TRAILING_TP_START = 0.003  # 0.3%
TRAILING_TP_CALLBACK = 0.002  # 0.2%


# Contract addresses for tokens in trade
wmatic_address = "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270"
usdt_address = "0xc2132D05D31c914a87C6611C10748AEb04B58e8F"

polygon_rpc = RPC_URL
web3 = Web3(Web3.HTTPProvider(polygon_rpc))

#Load env credentials into local variables
wallet_address = ADDRESS
private_key = PRIVKEY

#Validating input variables
if not wallet_address.startswith("0x") or len(wallet_address) != 42:
    raise ValueError("Invalid Wallet.")
if len(private_key) < 64:
    raise ValueError("Invalid Private Key.")


# Generate a key and encrypt private key
encryption_key = Fernet.generate_key()
cipher = Fernet(encryption_key)

encrypted_private_key = cipher.encrypt(private_key.encode())


QUICKSWAP_ROUTER_ADDRESS = web3.to_checksum_address("0xa5E0829CaCED8fFDD4De3c43696c57F7D7A678ff")  # QuickSwap Router

# ABI for QuickSwap Router
ROUTER_ABI = [
        {"inputs":[{"internalType":"address","name":"_factory","type":"address"},{"internalType":"address","name":"_WETH","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"WETH","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"amountADesired","type":"uint256"},{"internalType":"uint256","name":"amountBDesired","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amountTokenDesired","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountIn","outputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountOut","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsIn","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"reserveA","type":"uint256"},{"internalType":"uint256","name":"reserveB","type":"uint256"}],"name":"quote","outputs":[{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETHSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermit","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermitSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityWithPermit","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapETHForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETHSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}
]

# ABI pendek untuk fungsi ERC20 balanceOf
erc20_abi = [
    {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"}
]

# Initialize contract
router_contract = web3.eth.contract(address=QUICKSWAP_ROUTER_ADDRESS, abi=ROUTER_ABI)


# =====================
# USE BINANCE PRICE FEED TO GENERATE SIGNALS
# =====================


client = Client(API_KEY, API_SECRET)

# Function to get historical data incrementally
def get_historical_data(symbol='POLUSDT', interval=Client.KLINE_INTERVAL_5MINUTE, limit=1000):
    try:
        # Fetch initial historical data
        klines = client.get_historical_klines(symbol, interval, limit=limit)
        df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 
                                           'close_time', 'quote_asset_volume', 'number_of_trades', 
                                           'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
        
        # Convert and optimize data types
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['close'] = df['close'].astype('float32')
        df['volume'] = df['volume'].astype('float32')
        return df
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return pd.DataFrame()

# Update DataFrame with new data
def update_historical_data(df, symbol='POLUSDT', interval=Client.KLINE_INTERVAL_5MINUTE):
    try:
        last_timestamp = int(df['timestamp'].iloc[-1].timestamp() * 1000)  # Convert to milliseconds
        
        # Fetch new data since the last timestamp
        klines = client.get_historical_klines(symbol, interval, start_str=last_timestamp)
        
        # Convert to DataFrame
        new_df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 
                                               'close_time', 'quote_asset_volume', 'number_of_trades', 
                                               'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
        
        # Optimize new data types
        new_df['timestamp'] = pd.to_datetime(new_df['timestamp'], unit='ms')
        new_df['close'] = new_df['close'].astype('float32')
        new_df['volume'] = new_df['volume'].astype('float32')
        
        # Append only new rows
        updated_df = pd.concat([df, new_df]).drop_duplicates(subset='timestamp').reset_index(drop=True)
        
        # Release memory of the temporary DataFrame
        del new_df
        gc.collect()  # Force garbage collection
        
        return updated_df
    except Exception as e:
        print(f"Error updating historical data: {e}")
        return df

# Function to calculate RSI
def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # Release memory of temporary variables
    del delta, gain, loss, rs
    gc.collect()
    
    return df


# Example RSI calculation function (ensure you have your own or a proper implementation)
def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    return df

######################divergence block 
def detect_rsi_divergence(df, rsi_period=14, window=5):
    """
    Detect RSI divergences (Bullish and Bearish) based on price action.
    :param df: DataFrame containing 'close' prices and RSI.
    :param rsi_period: Period for RSI calculation.
    :param window: Number of bars to consider for local extrema.
    :return: DataFrame with divergence signals.
    """
    
    # Ensure RSI is calculated
    df = calculate_rsi(df, period=rsi_period)
    
    # Identify local highs and lows in price
    df['local_low'] = df['close'].rolling(window=window, center=True).min()
    df['local_high'] = df['close'].rolling(window=window, center=True).max()
    
    # Identify local highs and lows in RSI
    df['rsi_low'] = df['rsi'].rolling(window=window, center=True).min()
    df['rsi_high'] = df['rsi'].rolling(window=window, center=True).max()
    
    # Detect bullish divergence (Price lower low, RSI higher low)
    bullish_condition = (
        (df['close'] < df['close'].shift(window)) &  # Lower low in price
        (df['rsi'] > df['rsi'].shift(window))  # Higher low in RSI
    )
    
    # Detect bearish divergence (Price higher high, RSI lower high)
    bearish_condition = (
        (df['close'] > df['close'].shift(window)) &  # Higher high in price
        (df['rsi'] < df['rsi'].shift(window))  # Lower high in RSI
    )
    
    # Apply signals
    df['divergence_signal'] = 0
    df['divergence_type'] = None
    df.loc[bullish_condition, 'divergence_signal'] = 1  # Buy signal
    df.loc[bullish_condition, 'divergence_type'] = 'bullish'
    df.loc[bearish_condition, 'divergence_signal'] = -1  # Sell signal
    df.loc[bearish_condition, 'divergence_type'] = 'bearish'
    
    gc.collect()
    return df

# Integrate RSI divergence into the main signal function
def generate_signals_with_rsi_divergence(df, local_window=5, rsi_period=14):
    df = generate_signals(df, local_window)
    df = detect_rsi_divergence(df, rsi_period, local_window)
    return df





##########################



def generate_signals(df, local_window=5):
    # Calculate moving averages
    df['sma10'] = df['close'].rolling(window=10).mean()
    df['sma200'] = df['close'].rolling(window=200).mean()
    df['sma9'] = df['close'].rolling(window=9).mean()
    
    # Calculate SMA and Envelopes
    period = 20
    deviation = 0.01
    df['sma'] = df['close'].rolling(window=period).mean()
    df['upper_band'] = df['sma'] * (1 + deviation)
    df['lower_band'] = df['sma'] * (1 - deviation)    

    # Calculate RSI
    df = calculate_rsi(df, period=14)

    # --- New logic for local extremes ---
    # Compute the rolling minimum and maximum over a defined window.
    # We use min_periods=local_window to ensure we only flag signals once we have enough data
    df['rolling_min'] = df['close'].rolling(window=local_window, min_periods=local_window).min()
    df['rolling_max'] = df['close'].rolling(window=local_window, min_periods=local_window).max()

    # To avoid potential floating point issues when checking for equality,
    # you can use np.isclose. Here we use a tolerance value
    tolerance = 1e-8

    # Buy signal: when the previous bar's close was the local minimum and now price increases
    buy_condition = (
        np.isclose(df['close'].shift(1), df['rolling_min'].shift(1), atol=tolerance) &
        (df['close'] > df['close'].shift(1))
    )
    
    # Sell signal: when the previous bar's close was the local maximum and now price decreases
    sell_condition = (
        np.isclose(df['close'].shift(1), df['rolling_max'].shift(1), atol=tolerance) &
        (df['close'] < df['close'].shift(1))
    )

    # Optionally, if you still want to use the envelope bands as an extra filter,
    # you could combine the conditions. For example:
    buy_condition = buy_condition & (df['close'] < df['lower_band'])
    sell_condition = sell_condition & (df['close'] > df['upper_band'])
    
    # Generate signals
    df['signal'] = 0  # Default: no signal
    df['signal_type'] = None  # Default: no signal type
    df.loc[buy_condition, 'signal'] = 1
    df.loc[buy_condition, 'signal_type'] = 'buy'
    df.loc[sell_condition, 'signal'] = -1
    df.loc[sell_condition, 'signal_type'] = 'sell'

    # Clean up (if needed)
    gc.collect()
    
    print("Signals generated based on local extremes and reversals.")
    return df




# =====================
# EMA-BASED SIGNAL GENERATION
# =====================

price_data = []  # Store recent price data for indicators

# Fetch the latest price from Chainlink Oracle
def fetch_price():
    contract = web3.eth.contract(address=CHAINLINK_ORACLE_ADDRESS, abi=[
        {"inputs": [],
         "name": "latestRoundData",
         "outputs": [
             {"internalType": "uint80", "name": "roundId", "type": "uint80"},
             {"internalType": "int256", "name": "answer", "type": "int256"},
             {"internalType": "uint256", "name": "startedAt", "type": "uint256"},
             {"internalType": "uint256", "name": "updatedAt", "type": "uint256"},
             {"internalType": "uint80", "name": "answeredInRound", "type": "uint80"}
         ],
         "stateMutability": "view", "type": "function"}
    ])
    latest_data = contract.functions.latestRoundData().call()
    price = latest_data[1] / 1e8
    return float(price)

signals = []
def fetch_signal():
    data = fetch_historical_data()    
    latest_signal = generate_signals(data)
    signal = latest_signal[1]
    
    return signal

def fetch_latest_price():
    """
    Fetch the latest price from the Chainlink oracle.
    """
    # Initialize web3 connection
    web3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not web3.is_connected():
        raise ConnectionError("Failed to connect to the blockchain.")

    # Access the Chainlink oracle contract
    oracle_contract = web3.eth.contract(address=CHAINLINK_ORACLE_ADDRESS, abi=CHAINLINK_ABI)

    # Call the latestRoundData function
    round_data = oracle_contract.functions.latestRoundData().call()
    price = round_data[1] / 1e8  # Chainlink prices are typically 8 decimals
    updated_at = round_data[3]  # Timestamp of the last update

    return price, updated_at

# Example usage
if __name__ == "__main__":
    try:
        latest_price, timestamp = fetch_latest_price()
        print(f"Latest Price: {latest_price} USD")
        print(f"Last Updated: {timestamp}")
    except Exception as e:
        print(f"Error: {e}")


# Example integration
def fetch_historical_data():
    prices = []
    for _ in range(10):  # Fetch the last 10 price updates
        price, _ = fetch_latest_price()
        prices.append(price)
    return pd.DataFrame({"close": prices})


def calculate_ema(data, period=20):
    """
    Calculate the EMA for the given period.
    """
    return data['close'].ewm(span=period, adjust=False).mean()

#def generate_signals(data):
#    data['EMA_20'] = data['close'].ewm(span=20, adjust=False).mean()
#    data['signal'] = None
#    for i in range(1, len(data)):
#        if data['close'][i] > data['EMA_20'][i]:
#            data.loc[i, 'signal'] = 'buy'
#        elif data['close'][i] < data['EMA_20'][i]:
#            data.loc[i, 'signal'] = 'sell'
#    return data

#def display_signals(data):
#    """
#    Display the generated signals.
#    """
#    print(data[['close', 'EMA_20', 'signal']])

# =====================
# HELPER FUNCTIONS
# =====================
def calculate_portfolio_balance(wmatic_balance, usdt_balance, price):
    return wmatic_balance * price + usdt_balance

def calculate_trade_volume(portfolio_value, percentage):
    return portfolio_value * percentage

def execute_buy(volume, price):
    print(f"Executing BUY: Volume = {volume:.4f}, Price = {price:.4f}")
    # Add actual transaction logic here
    token_in = usdt_address
    token_out = wmatic_address
    lot = volume
    approve_token(token_in, QUICKSWAP_ROUTER_ADDRESS, int(lot * 10**6))
    tx_hash = swap_tokens(token_in, token_out, int(lot * 10**6), 0)    
     
    return True

def execute_sell(volume, price):
    print(f"Executing SELL: Volume = {volume:.4f}, Price = {price:.4f}")
    token_in = usdt_address
    token_out = wmatic_address
    amt_tosell = volume / price
    approve_token(token_out, QUICKSWAP_ROUTER_ADDRESS, web3.to_wei(amt_tosell, 'ether'))
    tx_hash = swap_tokens(token_out, token_in, web3.to_wei(amt_tosell, 'ether'), 0)    
    # Add actual transaction logic here
    return True

# Fungsi untuk mendapatkan saldo token
def get_token_balance(token_address, wallet_address):
    contract = web3.eth.contract(address=Web3.to_checksum_address(token_address), abi=erc20_abi)
    balance = contract.functions.balanceOf(Web3.to_checksum_address(wallet_address)).call()
    decimals = contract.functions.decimals().call()
    return balance / (10 ** decimals)

# =====================
# TRAILING TP/SL MANAGEMENT
# =====================
def monitor_position(entry_price, position_type, current_price, trailing_tp_start, trailing_tp_callback, trailing_tp):
    """
    Monitors the position and adjusts the trailing take profit (TP).
    """
    # Precompute thresholds to save redundant calculations
    long_threshold = entry_price + trailing_tp_callback
    short_threshold = entry_price - trailing_tp_callback

    if position_type == "LONG" and current_price > long_threshold:
        trailing_tp = max(trailing_tp, current_price - trailing_tp_callback)
    elif position_type == "SHORT" and current_price < short_threshold:
        trailing_tp = min(trailing_tp, current_price + trailing_tp_callback)

    # Check if the position should be closed
    if (position_type == "LONG" and current_price <= trailing_tp) or \
       (position_type == "SHORT" and current_price >= trailing_tp):
        close_position(current_price)

    return trailing_tp

def close_position(current_price):
    """
    Closes the position.
    """
    # Use lightweight logging for minimal overhead
    print(f"Position closed at price {current_price}")
    # Avoid unnecessary state persistence


# =====================
# APPROVAL & EXECUTION
# =====================

# Set trade parameters
router_address = Web3.to_checksum_address("0xa5E0829CaCED8fFDD4De3c43696c57F7D7A678ff")  # Replace with the DEX router address
token_in = Web3.to_checksum_address(usdt_address)      # Replace with the input token address (e.g., USDT)
token_out = Web3.to_checksum_address(wmatic_address)    # Replace with the output token address (e.g., WMATIC)
amount_in = 2.0                         # Amount to trade in `token_in` units
slippage = 0.5                         # Slippage tolerance (0.5%)
account = wallet_address        # Replace with your wallet address
USER_ADDRESS = wallet_address
PRIVATE_KEY = encrypted_private_key  # Replace with your private key

###########################
def get_optimized_gas_price():
    gas_price = web3.eth.gas_price
    return int(gas_price * 1.2)  # Use 80% of the suggested gas price
    
# Approve function
def approve_token(token_address, spender_address, amount):
    erc20_abi = [
        {
            "constant": False,
            "inputs": [
                {"name": "_spender", "type": "address"},
                {"name": "_value", "type": "uint256"},
            ],
            "name": "approve",
            "outputs": [{"name": "success", "type": "bool"}],
            "payable": False,
            "stateMutability": "nonpayable",
            "type": "function",
        }
    ]
    token_contract = web3.eth.contract(address=web3.to_checksum_address(token_address), abi=erc20_abi)
    nonce = web3.eth.get_transaction_count(USER_ADDRESS)

    gas_price = get_optimized_gas_price()
    # Build the transaction
    tx = token_contract.functions.approve(spender_address, amount).build_transaction({
        'from': USER_ADDRESS,
        'gas': 100000,
        'gasPrice': gas_price,
        'nonce': nonce,
    })

    # Sign and send the transaction
    #signed_tx = web3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    #tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)

    send_transaction_with_retry(tx, private_key=PRIVATE_KEY)
    
def process_transaction(encrypted_private_key, encryption_key, transaction):
    #from cryptography.fernet import Fernet

    # Dekripsi dan gunakan private key dalam blok terbatas
    #with Fernet(encryption_key) as fernet:
        decrypted_private_key = cipher.decrypt(encrypted_private_key).decode()
        signed_transaction = web3.eth.account.sign_transaction(transaction, decrypted_private_key)

        # Private key akan otomatis dihapus setelah blok selesai
        return signed_transaction


def send_transaction_with_retry(tx, private_key, max_retries=3, gas_multiplier=2):
    retries = 0
    while retries <= max_retries:
        try:
            # Sign and send the transaction
            signed_transaction=process_transaction(encrypted_private_key=private_key, encryption_key=cipher, transaction=tx)
            #signed_txn = web3.eth.account.sign_transaction(tx, private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_transaction.raw_transaction)
            print(f"Transaction sent: {tx_hash.hex()}")

            # Wait for receipt
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            print(f"Transaction confirmed in block {receipt.blockNumber}")
            return tx_hash.hex()

        except TimeExhausted:
            print("Transaction timeout. Retrying with higher gas price...")
            tx['gasPrice'] = int(tx['gasPrice'] * gas_multiplier)  # Increase gas price
            retries += 1

        except TransactionNotFound:
            # Handle transaction not found
            print("Transaction not found. Retrying...")
            retries += 1
            time.sleep(10)

        except Exception as e:
            print(f"Error: {str(e)}")
            raise

    raise Exception("Transaction failed after maximum retries.")

def swap_tokens(token_in, token_out, amount_in, amount_out_min):
    path = [web3.to_checksum_address(token_in), web3.to_checksum_address(token_out)]
    nonce = web3.eth.get_transaction_count(USER_ADDRESS)

    gas_price = get_optimized_gas_price()
    # Build the transaction
    tx = router_contract.functions.swapExactTokensForTokens(
        amount_in, amount_out_min, path, USER_ADDRESS, int(time.time()) + 300
    ).build_transaction({
        'from': USER_ADDRESS,
        'gas': 200000,
        'gasPrice': gas_price,
        'nonce': nonce,
    })

    # Sign and send the transaction
    #signed_tx = web3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    #tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)

    send_transaction_with_retry(tx, private_key=PRIVATE_KEY)



import csv
import os

# =====================
# MAIN TRADING LOGIC
# =====================
class TradingBot:
    CALLBACK_RATE = 0.01  # 0.4% callback
    CHECK_INTERVAL = 15  # Check every 15 seconds
    TP_THRESHOLD = 1.05  # +3% gain to activate trailing TP
    SL_THRESHOLD = 0.95  # -5% loss to activate trailing TP

    def __init__(self):
        self.open_position = None
        self.trailing_tp_active = False
        self.log_file = "trade_logs.csv"
        self.initialize_log()

    def initialize_log(self):
        """Initialize the CSV log file with headers if it doesn't exist."""
        if not os.path.exists(self.log_file):
            with open(self.log_file, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["timestamp", "action", "price", "volume", "position_type", "portfolio_value", "wmatic_balance", "usdt_balance"])

    def log_transaction(self, action, price, volume, position_type, portfolio_value, wmatic_balance, usdt_balance):
        """Log a buy or sell transaction to the CSV file."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, action, price, volume, position_type, portfolio_value, wmatic_balance, usdt_balance])

    def update_trailing_tp_with_activation(self, position_type, current_price, entry_price, trailing_tp):
        """Update trailing TP only in the favorable direction after activation."""
        if position_type == 'long':
            if not self.trailing_tp_active and current_price >= entry_price * self.TP_THRESHOLD:
                self.trailing_tp_active = True
                self.highest_price = current_price
                print(f"Trailing TP activated for LONG at {current_price:.4f}")

            if self.trailing_tp_active:
                self.highest_price = max(self.highest_price, current_price)
                new_trailing_tp = self.highest_price * (1 - self.CALLBACK_RATE)
                if new_trailing_tp > trailing_tp:
                    trailing_tp = new_trailing_tp
                print(f"Updated trailing TP for LONG to {trailing_tp:.4f}")

        elif position_type == 'short':
            if not self.trailing_tp_active and current_price <= entry_price * self.SL_THRESHOLD:
                self.trailing_tp_active = True
                self.lowest_price = current_price
                print(f"Trailing TP activated for SHORT at {current_price:.4f}")

            if self.trailing_tp_active:
                self.lowest_price = min(self.lowest_price, current_price)
                new_trailing_tp = self.lowest_price * (1 + self.CALLBACK_RATE)
                if new_trailing_tp < trailing_tp:
                    trailing_tp = new_trailing_tp
                print(f"Updated trailing TP for SHORT to {trailing_tp:.4f}")

        return trailing_tp

    def trading_execution(self):
        current_price = fetch_price()  # Replace with your function to fetch price
        wmatic_balance = get_token_balance(wmatic_address, wallet_address)
        usdt_balance = get_token_balance(usdt_address, wallet_address)
        portfolio_value = calculate_portfolio_balance(wmatic_balance, usdt_balance, current_price)
        trade_volume = calculate_trade_volume(portfolio_value, 0.16)

        pol_balance = web3.eth.get_balance(wallet_address)
        balance_in_pol = web3.from_wei(pol_balance, 'ether')

        print(f"-------------------------------------------------------------")
        print(f" Balances -- USDT: {usdt_balance:.4f} | WMATIC: {wmatic_balance:.4f} | POL: {balance_in_pol:.4f} ")
        print(f" Current price: {current_price:.4f} | Portfolio: {portfolio_value:.4f} | Lot: {trade_volume:.4f} ")
        print(f"-------------------------------------------------------------")

        if self.open_position:
            self.manage_open_position(current_price, trade_volume, portfolio_value, wmatic_balance, usdt_balance)
        else:
            self.open_new_position(current_price, wmatic_balance, usdt_balance, portfolio_value, trade_volume)

        time.sleep(self.CHECK_INTERVAL)

    def manage_open_position(self, current_price, trade_volume, portfolio_value, wmatic_balance, usdt_balance):
        position_type = self.open_position['type']
        entry_price = self.open_position['entry_price']
        trailing_tp = self.open_position['trailing_tp']
        sl_price = entry_price * (0.95 if position_type == 'long' else 1.05)

        trailing_tp = self.update_trailing_tp_with_activation(position_type, current_price, entry_price, trailing_tp)
        print(f"Monitoring position: Current Price = {current_price:.4f}, Trailing TP = {trailing_tp:.4f}, SL = {sl_price:.4f}")

        if self.trailing_tp_active:
            if (position_type == 'long' and current_price < trailing_tp):
                print(f"Take profit triggered at {current_price:.4f}. Closing LONG position.")
                execute_sell(trade_volume, current_price)
                self.log_transaction("sell", current_price, trade_volume, "long", portfolio_value, wmatic_balance, usdt_balance)
                self.reset_position()
            elif (position_type == 'short' and current_price > trailing_tp):
                print(f"Take profit triggered at {current_price:.4f}. Closing SHORT position.")
                execute_buy(trade_volume, current_price)
                self.log_transaction("buy", current_price, trade_volume, "short", portfolio_value, wmatic_balance, usdt_balance)
                self.reset_position()

        if (position_type == 'long' and current_price <= sl_price):
            print(f"Stop loss triggered at {current_price:.4f}. DCA Long to lower the risk.")
            execute_buy(trade_volume, current_price)
            self.log_transaction("buy", current_price, trade_volume, "long", portfolio_value, wmatic_balance, usdt_balance)
            self.reset_position()
        elif (position_type == 'short' and current_price >= sl_price):
            print(f"Stop loss triggered at {current_price:.4f}. DCA Short to lower the risk.")
            execute_sell(trade_volume, current_price)
            self.log_transaction("sell", current_price, trade_volume, "short", portfolio_value, wmatic_balance, usdt_balance)
            self.reset_position()

    def open_new_position(self, current_price, wmatic_balance, usdt_balance, portfolio_value, trade_volume):
        historical_data = get_historical_data()
        df = update_historical_data(historical_data)
        df_with_signals = generate_signals(df)
        latest_signal = df_with_signals.iloc[-1]['signal_type']
        last_signal = latest_signal
        
        df_withRSIdvg = generate_signals_with_rsi_divergence(df)
        confirmed_signal = df_withRSIdvg.iloc[-1]['divergence_type']
        dvg_signal = confirmed_signal

        if (last_signal == 'buy' or dvg_signal == 'bullish') and usdt_balance > portfolio_value * 0.1 and usdt_balance > trade_volume:
            if execute_buy(trade_volume, current_price):
                self.open_position = {'type': 'long', 'entry_price': current_price, 'trailing_tp': current_price * self.TP_THRESHOLD}
                self.log_transaction("buy", current_price, trade_volume, "long", portfolio_value, wmatic_balance, usdt_balance)
                print(f"LONG position opened at {current_price:.4f}")
        elif (last_signal == 'sell' or dvg_signal== 'bearish' ) and wmatic_balance > (portfolio_value * 0.1 / current_price) and wmatic_balance > (trade_volume / current_price):
            if execute_sell(trade_volume, current_price):
                self.open_position = {'type': 'short', 'entry_price': current_price, 'trailing_tp': current_price * self.SL_THRESHOLD}
                self.log_transaction("sell", current_price, trade_volume, "short", portfolio_value, wmatic_balance, usdt_balance)
                print(f"SHORT position opened at {current_price:.4f}")

        #print(df_with_signals[['timestamp', 'close', 'sma10', 'sma9', 'rsi', 'signal_type']].tail())
        print(df_with_signals[['timestamp', 'close', 'sma', 'upper_band', 'lower_band', 'signal_type']].tail() )
        print(df_withRSIdvg[['divergence_type']].tail() )        

    def reset_position(self):
        self.open_position = None
        self.trailing_tp_active = False



# Main Script

if __name__ == "__main__":
    bot = TradingBot()
    while True:
        try:
            
            #historical_data = update_historical_data(historical_data)
            bot.trading_execution()
            time.sleep(15)  # Wait before next execution
        except Exception as e:
            print(f"Error in trading loop: {e}")

