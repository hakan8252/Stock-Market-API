import streamlit as st
import plotly.graph_objs as go
from datetime import datetime, timedelta
from polygon import RESTClient
import requests
import pandas as pd
from plotly.subplots import make_subplots

# Initialize the RESTClient with your API key
POLYGON_API_KEY = "dh5skqccO4AKJ4X7aHnpxjeW1VJS9_eS"
client = RESTClient(api_key=POLYGON_API_KEY)

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


# Function to fetch tickers from Polygon.io
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

# Main function to run the Streamlit app
def main():
    st.title("Stock Market Data")

    # Fetch tickers from Polygon.io
    tickers = fetch_tickers()

    # Define default values for input fields
    default_timeframe = "day"
    default_end_date = datetime.now()
    default_start_date = default_end_date - timedelta(days=7)

    # Create sidebar for inputs
    st.sidebar.header("Input Parameters")
    ticker_input = st.sidebar.text_input("Enter a ticker", "")
    selected_ticker = st.sidebar.selectbox("Or select a ticker", tickers)

    # Allow user to enter a ticker manually
    selected_ticker = ticker_input if ticker_input else selected_ticker

    timeframe = st.sidebar.selectbox("Select timeframe", ["day", "week", "month"], index=0)  # Set index to 0 for default value
    start_date = st.sidebar.date_input("Select start date", value=default_start_date)
    end_date = st.sidebar.date_input("Select end date", value=default_end_date)

    # Check if the selected start date is more than two years before the current date
    if (datetime.now() - datetime.combine(start_date, datetime.min.time())).days > 365 * 2:
        st.sidebar.warning("Warning: Selected start date cannot be more than two years before the current date.")

    # Fetch data based on the selected ticker
    df = fetch_data(selected_ticker, timeframe, start_date, end_date)

    # Calculate SMA and EMA
    window_sma = st.sidebar.slider("Select SMA Window", min_value=2, max_value=14, value=2)
    df['sma'] = calculate_sma(df['close'], window_sma)

    window_ema = st.sidebar.slider("Select EMA Window", min_value=2, max_value=14, value=2)
    df['ema'] = calculate_ema(df['close'], window_ema)

    # Calculate RSI
    window_rsi = st.sidebar.slider("Select RSI Window", min_value=2, max_value=14, value=2)
    df['rsi'] = calculate_rsi(df['close'], window_rsi)

    # Fetch news articles based on the selected ticker
    news_data = fetch_news(selected_ticker)

    # Plot candlestick chart with SMA and EMA
    candlestick = go.Candlestick(
        x=df['timestamp'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Candlesticks'
    )

    sma = go.Scatter(
        x=df['timestamp'],
        y=df['sma'],
        mode='lines',
        name='SMA',
    )

    ema = go.Scatter(
        x=df['timestamp'],
        y=df['ema'],
        mode='lines',
        name='EMA',
    )

    # Create a separate plot for RSI
    rsi = go.Scatter(
        x=df['timestamp'],
        y=df['rsi'],
        mode='lines',
        name='RSI',
    )

    # Create subplots with adjusted vertical spacing
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        subplot_titles=("Candlestick Chart with SMA and EMA", "Relative Strength Index (RSI)"),
                        vertical_spacing=0.3)  # Adjust the row heights as per your preference

    # Add candlestick to the first subplot
    fig.add_trace(candlestick, row=1, col=1)

    # Add SMA and EMA to the first subplot
    fig.add_trace(sma, row=1, col=1)
    fig.add_trace(ema, row=1, col=1)

    # Add RSI to the second subplot
    fig.add_trace(rsi, row=2, col=1)

    # Update layout with adjusted margins
    fig.update_layout(xaxis_title="Date", yaxis_title="Price",
                    height=800)  # Adjust top and bottom margins as per your preference

    fig.update_yaxes(title_text="RSI", row=2, col=1)

    # Display the plot
    st.plotly_chart(fig)

    # Display news articles
    st.title("News Articles")
    for news_article in news_data:
        st.subheader(news_article["title"])
        st.write(f"Author: {news_article['author']}")
        st.write(f"Article URL: [{news_article['title']}]({news_article['article_url']})")
        # st.write(f"Description: {news_article['description']}")
        st.image(news_article["image_url"])
        st.markdown("---")  # Add a horizontal line between articles


if __name__ == "__main__":
    main()
