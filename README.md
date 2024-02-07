# Stock Market Data Analysis with Streamlit
This Streamlit web application allows users to visualize and analyze stock market data using candlestick charts, moving averages, relative strength index (RSI), and fetch recent news articles related to a selected stock ticker symbol.

# Features

* Candlestick Chart Visualization: Visualize stock market data using candlestick charts, showing open, high, low, and close prices over a specified time frame.
* Moving Averages (SMA and EMA): Calculate and display simple moving averages (SMA) and exponential moving averages (EMA) to identify trends in the stock data.
* Relative Strength Index (RSI): Calculate and plot the relative strength index (RSI) to determine if a stock is overbought or oversold.
* Fetch News Articles: Fetch recent news articles related to the selected stock ticker symbol to provide users with relevant information about the company.

## Getting Started
### Prerequisites
Before running the application, make sure you have the following installed:

<br/> Python 3.x
<br/> Streamlit
<br/> Plotly
<br/> Polygon API key (sign up [here](https://polygon.io/) to get your API key)

# Installation
Clone the repository:

```bash
git clone https://github.com/hakan8252/stock-market-app.git
```

Install the required Python packages:
```bash
pip install -r requirements.txt
```

Usage
Set up your Polygon API key by replacing "YOUR_POLYGON_API_KEY" in the code with your actual API key.

Run the Streamlit app:

```bash
streamlit run streamlit_app.py
```

Access the app in your web browser at http://localhost:8501.

# Contributing
Contributions are welcome! If you find any bugs or have suggestions for improvement, please open an issue or submit a pull request.

# Acknowledgements
This project uses data from the Polygon API.
Candlestick chart visualization is implemented using Plotly.
Relative Strength Index (RSI) calculations are based on standard financial formulas.





