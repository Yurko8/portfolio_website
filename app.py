import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import base64
import os

API_KEY = os.getenv("API_KEY")

def get_portfolio_data(params):
    api_url = "" # TO BE ADDED WHEN THE FINAL API IS DONE!
    weights, technical_data = requests.get(api_url).json()
    return weights, technical_data

def fetch_stock_data(symbol):
    base_url = 'https://www.alphavantage.co/query?'
    function = 'TIME_SERIES_DAILY_ADJUSTED'
    url = f"{base_url}function={function}&symbol={symbol}&apikey={API_KEY}&outputsize=compact"

    response = requests.get(url)
    data = response.json()

    if 'Time Series (Daily)' in data:
        df = pd.DataFrame.from_dict(data['Time Series (Daily)'], orient='index', dtype='float')
        df = df.rename(columns={
            '1. open': 'open',
            '2. high': 'high',
            '3. low': 'low',
            '4. close': 'close',
            '5. adjusted close': 'adjusted_close',
            '6. volume': 'volume',
            '7. dividend amount': 'dividend_amount',
            '8. split coefficient': 'split_coefficient'
        })
        df.index = pd.to_datetime(df.index)
        return df.sort_index()
    else:
        st.error(f"Error fetching data for {symbol}. Please check the symbol and try again.")
        return pd.DataFrame()

image_path = "images/portfolio_logo.jpeg"
with open(image_path, "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode()

st.set_page_config(layout="wide", page_title="JPMST Capital")

st.markdown("""
    <style>
    /* Global settings */
    body {
        background-color: #0e1117;
        color: white;
    }

    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: #1f232a;
        color: white;
    }

    /* Widget labels */
    .sidebar .sidebar-content .element-container {
        color: white;
    }

    /* Headers and text */
    h1, h2, h3, h4, h5, h6, p, div, label {
        color: white;
    }

    /* Input elements */
    .stTextInput, .stNumberInput, .stSelectbox, .stMultiselect {
        background-color: #262c3a;
        color: white;
    }

    /* Button styling */
    button {
        background-color: #ff4b4b;
        color: white;
    }

    /* Adjusting margin for headers */
    .sub-header {
        color: #ff6f61;
        margin-top: 20px;
    }

    </style>
    """, unsafe_allow_html=True)


st.markdown(f"""
    <div style='text-align: center;'>
        <img src="data:image/jpeg;base64,{encoded_image}" width="400"> <!-- Adjusted width to 400px -->
    </div>
    """, unsafe_allow_html=True)

st.markdown('''
# Welcome to JPMST Capital!
''')

st.markdown('<h2 class="sub-header">Cutting-Edge Portfolio Optimization</h2>', unsafe_allow_html=True)

st.markdown('''
## About us:
We are a specialized portfolio optimization firm leveraging advanced tools,
including Deep Neural Networks, Geometric Brownian Motion, and Monte Carlo Simulations,
to deliver maximum returns for our clients while adhering to their defined risk parameters.
''')

st.markdown('''
## How does it work?
Our services deliver optimized stock weight recommendations based on advanced predictions and simulations.
These allocations are updated periodically as new data becomes available.
By selecting "Get Optimized Weights," you will gain access to a histogram displaying our suggested portfolio distribution, along with a graph illustrating the projected performance of your portfolio.
''')

available_stocks = ['AAPL', 'XOM', 'MSFT', 'NEE', 'AMT', 'CAT', 'PG', 'JNJ', 'MCD', 'GS']
st.sidebar.header("Your desired parameters for a portfolio")
invest_amount = st.sidebar.number_input(label="Please choose the amount you would like to invest:", min_value=100, max_value=1000000, step=100, value=1000)
risk = st.sidebar.slider(label="What would be the desired risk?", min_value=0.01, max_value=0.15, step=0.01)
desired_stocks = st.sidebar.multiselect("Please select the desired stocks you would like to invest your capital in...", available_stocks, default=None)

url_optimize = ""
params = {"risk": risk, "investment_amount": invest_amount, "desired_stocks": desired_stocks}

click = st.button(label="Get optimized weights!")


if click:
    weights, technical_data = get_portfolio_data(params=params)
    st.markdown("### Portfolio Weight Distribution")
    plt.figure(figsize=(10, 6))
    bars = plt.bar(weights.keys(), weights.values(), color='#d62728', edgecolor='white')
    plt.xlabel("Stocks", fontsize=12, fontweight='bold')
    plt.ylabel("Weight", fontsize=12, fontweight='bold')
    plt.title("Portfolio Weight Distribution", fontsize=16, fontweight='bold')
    plt.grid(True, color='gray', linestyle='--', linewidth=0.5)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.tight_layout()
    plt.show()



st.sidebar.markdown("If you're uncertain about which stocks to invest in, you can visualize the closing price trends over time below.")
selected_stocks = st.sidebar.multiselect("Select stocks to plot", available_stocks, default=['AAPL'])

plot_placeholder = st.sidebar.empty()

if selected_stocks:
    with plot_placeholder.container():
        plt.style.use('dark_background')
        plt.figure(figsize=(6, 4))

        for stock in selected_stocks:
            stock_df = fetch_stock_data(stock)
            if not stock_df.empty:
                plt.plot(stock_df.index, stock_df['close'], label=stock)

        plt.title("Stock Closing Prices Over Time", color='white')
        plt.xlabel("Date", color='white')
        plt.ylabel("Price", color='white')
        plt.legend(loc="upper left")
        plt.grid(True, color='gray')
        st.pyplot(plt)
else:
    plot_placeholder.write("Please select at least one stock to plot.")
