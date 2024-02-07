import streamlit as st
import plotly.graph_objs as go
from datetime import datetime, timedelta
from plotly.subplots import make_subplots
import pandas as pd
from utils import fetch_tickers, fetch_data, fetch_news, calculate_sma, calculate_ema, calculate_rsi

# Set background color for the entire app
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

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
