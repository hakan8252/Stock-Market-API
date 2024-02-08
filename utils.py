import requests
import pandas as pd
from datetime import datetime
import streamlit as st

# # Get the API key from the environment variable
# POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")

POLYGON_API_KEY=st.secrets.secrets.POLYGON_API_KEY

# Function to fetch tickers from Polygon.io
@st.cache_data(ttl=3600)  # Cache data for 1 hour
def fetch_tickers():
    try:
        ticker_url = "https://api.polygon.io/v3/reference/tickers"
        params = {
            "active": "true",
            "apiKey": POLYGON_API_KEY,
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
    try:
        url = f"https://api.polygon.io/v2/aggs/ticker/{selected_ticker}/range/1/{timeframe}/{start_date}/{end_date}?adjusted=true&sort=asc&limit=120&apiKey={POLYGON_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()["results"]

        # Extract relevant data
        opens = [item['o'] for item in data]
        highs = [item['h'] for item in data]
        lows = [item['l'] for item in data]
        closes = [item['c'] for item in data]
        volumes = [item['v'] for item in data]
        timestamps = [datetime.fromtimestamp(item['t'] / 1000) for item in data]

        # Convert data to Pandas DataFrame
        df = pd.DataFrame({
            'timestamp': timestamps,
            'open': opens,
            'high': highs,
            'low': lows,
            'close': closes,
            'volume': volumes,
        })

        return df
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return pd.DataFrame()


# Function to fetch news articles based on a given ticker symbol
@st.cache_data(ttl=3600)  # Cache data for 1 hour
def fetch_news(ticker):
    try:
        news_url = "https://api.polygon.io/v2/reference/news"
        params = {
            "ticker": ticker,
            "apiKey": POLYGON_API_KEY,
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
