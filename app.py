import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
import base64
import os
from collections import defaultdict

API_KEY = os.getenv("API_KEY")

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
n_simulations = st.sidebar.number_input(label="Please choose the number of simulations you would like to run, each simulation corresponds to 30 minute intervals", min_value=10, max_value=5000, step=10, value=10)
desired_stocks = st.sidebar.multiselect("Please select the desired stocks you would like to invest your capital in...", available_stocks, default=None)


def fetch_data(stocks, n_simulations):
    stocks_param = str(stocks)
    api_url = f"https://portfolio-manager-96271241201.europe-west1.run.app/portfolio?stocks={stocks_param}&n_simulations={n_simulations}"
    response = requests.get(api_url)
    data = response.json()
    returns = data[0]
    vol = data[1]
    sharpe = data[2]
    weights = data[3]
    return returns, vol, sharpe, weights

click = st.button(label="Get optimized weights!")

if click:

    with st.spinner('Fetching and processing data...'):


        returns, vol, sharpe, weights = fetch_data(desired_stocks, n_simulations)


        average_return = np.mean(returns)*100
        expected_profit = invest_amount * average_return
        average_volatility = np.mean(vol)*100


        st.markdown("### Portfolio Performance")


        number_of_simulations = list(range(1, len(returns) + 1))
        annualized_returns = returns

        plt.figure(figsize=(10, 6))
        plt.plot(number_of_simulations, annualized_returns, marker='o', linestyle='-', color='#1f77b4', linewidth=2)
        plt.title('Annualized Returns vs Number of Simulations', fontsize=14, weight='bold')
        plt.xlabel('Number of Simulations', fontsize=12)
        plt.ylabel('Annualized Returns (%)', fontsize=12)
        plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        plt.tight_layout()
        st.pyplot(plt)
        plt.close()

        st.markdown("### Portfolio Value")

        returns_monthly = (np.array(returns)/5040)+1
        return_investment = invest_amount*np.cumprod(returns_monthly)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(number_of_simulations, return_investment, label='Portfolio Value', linewidth=2)
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.set_title("Portfolio Value Over Time", fontsize=16, fontweight='bold')
        ax.set_xlabel("Time Period (Number of Simulations)", fontsize=12)
        ax.set_ylabel("Portfolio Value", fontsize=12)
        ax.legend()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_linewidth(1.5)
        ax.spines['bottom'].set_linewidth(1.5)
        ax.tick_params(axis='both', which='major', labelsize=10)
        st.pyplot(fig)

        sum_dict = defaultdict(float)
        num_dicts = len(weights)
        for d in weights:
            for key, value in d.items():
                sum_dict[key] += value
        mean_dict = {key: sum_val / num_dicts for key, sum_val in sum_dict.items()}

        st.markdown("### Average Portfolio Weight Distribution")

        plt.figure(figsize=(10, 6))
        bars = plt.bar(mean_dict.keys(), mean_dict.values(), color='#d62728', edgecolor='white')
        plt.xlabel("Stocks", fontsize=12, fontweight='bold')
        plt.ylabel("Weight", fontsize=12, fontweight='bold')
        plt.title("Portfolio Weight Distribution", fontsize=16, fontweight='bold')
        plt.grid(True, color='gray', linestyle='--', linewidth=0.5)
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        plt.tight_layout()
        st.pyplot(plt)
        plt.close()


        st.markdown("### Portfolio Performance Metrics")
        st.write(f"**Average Volatility:** {average_volatility:,.2f}%")
        st.write(f"**Average Return:** {average_return:,.2f}%")


        st.markdown("### Investment Return")
        st.write(f"If you invest {invest_amount:,.2f} Dollars, you are expected to make {expected_profit:,.2f} Dollars based on the expected return.")

        sp_500 = 20.34
        difference = sp_500 - average_return
        st.markdown("### Benchmark Comparison")
        if difference > 0:
            st.write(f"Your return is {difference}% higher than S&P 500")
        else:
            st.write(f"Your return is {difference}% lower than S&P 500")

    st.success('Data processing complete!')



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
