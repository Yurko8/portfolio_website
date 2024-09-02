import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import base64


api_key = 'change_when_presenting'


def fetch_stock_data(symbol):
    base_url = 'https://www.alphavantage.co/query?'
    function = 'TIME_SERIES_DAILY_ADJUSTED'
    url = f"{base_url}function={function}&symbol={symbol}&apikey={api_key}&outputsize=compact"

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


st.markdown("""
    <style>
    .corner-logo {
        position: fixed;
        top: 10px;
        right: 10px;
        width: 200px;  /* Increased the size of the logo */
        z-index: 1;
    }
    .content {
        margin-top: 120px;  /* Adjust margin to avoid overlap with the larger logo */
    }
    </style>
    """, unsafe_allow_html=True)


st.markdown(f"""
    <div class="corner-logo">
        <img src="data:image/jpeg;base64,{encoded_image}" width="200">  <!-- Adjust the width here as well -->
    </div>
    """, unsafe_allow_html=True)


st.markdown('''
# Welcome to JPMST Capital!
''')


st.markdown('<h2 class="sub-header">Cutting-Edge Portfolio Optimization</h2>', unsafe_allow_html=True)

st.markdown('''
## About us:
We are a small-scale portfolio optimization company that uses tools such as Deep Neural Networks
in combination with Geometric Brownian Motion and Monta Carlo Simulations to ensure that our customers receive the highest return value within the specified risk parameters.
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

params = {"risk": risk, "investment_amount": invest_amount}

click = st.button(label="Get optimized weights!")

# if click:
st.sidebar.markdown("If you're uncertain about which stocks to invest in, you can visualize the closing price trends over time below.")

selected_stocks = st.sidebar.multiselect("Select stocks to plot", available_stocks, default=['AAPL'])

plot_placeholder = st.sidebar.empty()


if selected_stocks:
    with plot_placeholder.container():
        plt.figure(figsize=(6, 4))

        for stock in selected_stocks:
            stock_df = fetch_stock_data(stock)
            if not stock_df.empty:
                plt.plot(stock_df.index, stock_df['close'], label=stock)

        plt.title("Stock Closing Prices Over Time")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend(loc="upper left")
        plt.grid(True)
        st.pyplot(plt)
else:
    plot_placeholder.write("Please select at least one stock to plot.")
