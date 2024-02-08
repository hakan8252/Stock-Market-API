import requests
from polygon import RESTClient
import pandas as pd
from datetime import datetime
import streamlit as st

# # Get the API key from the environment variable
# POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

api_key=st.secrets.secrets.POLYGON_API_KEY
client = RESTClient(api_key=api_key)

# Function to fetch tickers from Polygon.io
@st.cache_data(ttl=3600)  # Cache data for 1 hour
def fetch_tickers():
    try:
        ticker_url = "https://api.polygon.io/v3/reference/tickers"
        params = {
            "active": "true",
            "apiKey": client,
            "limit": 1000,
            "market": "stocks"
        }
        response = requests.get(ticker_url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        tickers_data = response.json()
        tickers = [ticker["ticker"] for ticker in tickers_data["results"]]
        return tickers
    except Exception as e:
        st.sidebar.error(f"Error fetching tickers: {str(e)}")
        return []


# Function to fetch data from Polygon.io
@st.cache_data(ttl=3600)  # Cache data for 1 hour
def fetch_data(selected_ticker, timeframe, start_date, end_date):
    data = client.get_aggs(selected_ticker, 1, timeframe, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

    # Extract relevant data from the list of 'Agg' objects
    opens = [agg.open for agg in data]
    highs = [agg.high for agg in data]
    lows = [agg.low for agg in data]
    closes = [agg.close for agg in data]
    volumes = [agg.volume for agg in data]
    transactions = [agg.transactions for agg in data]
    timestamps = [agg.timestamp for agg in data]

    # Convert timestamps to datetime objects
    timestamps = [datetime.utcfromtimestamp(ts / 1000) for ts in timestamps]

    # Convert data to Pandas DataFrame
    df = pd.DataFrame({
        'timestamp': timestamps,
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes,
        'volume': volumes,
        'transactions': transactions
    })

    return df


# Function to fetch news articles based on a given ticker symbol
@st.cache_data(ttl=3600)  # Cache data for 1 hour
def fetch_news(ticker):
    try:
        news_url = "https://api.polygon.io/v2/reference/news"
        params = {
            "ticker": ticker,
            "apiKey": client,
            "limit": 10  # You can adjust the limit as per your preference
        }
        response = requests.get(news_url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        news_data = response.json()["results"]
        return news_data
    except Exception as e:
        st.sidebar.error(f"Error fetching news: {str(e)}")
        return []


# Function to calculate Simple Moving Average (SMA)
def calculate_sma(data, window):
    return data.rolling(window=window).mean()


# Function to calculate Exponential Moving Average (EMA)
def calculate_ema(data, window):
    return data.ewm(span=window, adjust=False).mean()


# Function to calculate Relative Strength Index (RSI)
def calculate_rsi(data, window):
    delta = data.diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
