import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
import base64
import os
from collections import defaultdict

API_KEY = os.getenv("API_KEY")
available_stocks = ['AAPL', 'XOM', 'MSFT', 'NEE', 'AMT', 'CAT', 'PG', 'JNJ', 'MCD', 'GS']


stock_descriptions = {
    'AAPL': 'Apple Inc. is a multinational technology company known for its innovative consumer electronics and software.',
    'XOM': 'Exxon Mobil Corporation is one of the world\'s largest publicly traded oil and gas companies.',
    'MSFT': 'Microsoft Corporation is a global leader in software, services, devices, and solutions.',
    'NEE': 'NextEra Energy, Inc. is an energy company involved in electricity generation from renewable resources.',
    'AMT': 'American Tower Corporation is a real estate investment trust and owner of wireless and broadcast communications infrastructure.',
    'CAT': 'Caterpillar Inc. is a manufacturer of construction and mining equipment, diesel and natural gas engines, and industrial gas turbines.',
    'PG': 'Procter & Gamble Co. is a multinational consumer goods corporation that produces a wide range of products.',
    'JNJ': 'Johnson & Johnson is a multinational corporation that develops medical devices, pharmaceutical, and consumer packaged goods.',
    'MCD': 'McDonald\'s Corporation is the world\'s largest restaurant chain by revenue.',
    'GS': 'The Goldman Sachs Group, Inc. is a leading global investment banking, securities, and investment management firm.'
}


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


st.set_page_config(layout="wide", page_title="JPMST Capital", page_icon="📈")

page = st.sidebar.selectbox("Choose a page:", ["Home", "Stock Information & Graphs", "Portfolio Optimization"])


if page == "Home":
    st.markdown("<h1 style='text-align: center;'>Welcome to JPMST Capital! 📊</h1>", unsafe_allow_html=True)


    image_path = "images/portfolio_logo.jpeg"
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()

    st.markdown(f"""
        <div style='text-align: center;'>
            <img src="data:image/jpeg;base64,{encoded_image}" width="300">
        </div>
        """, unsafe_allow_html=True)


    st.markdown('''### Cutting-Edge Portfolio Optimization Using Advanced Financial Technologies!''')

    st.markdown('''**What We Do:**
    At JPMST Capital, we specialize in portfolio optimization using advanced tools like Deep Neural Networks, Geometric Brownian Motion, and Monte Carlo Simulations. These tools help us deliver maximum returns to our clients while managing risk within the client’s defined parameters.''')

    st.markdown('''**How It Works:**
    By clicking "Get Optimized Weights," we trigger our API to pull stock data, preprocess it, make predictions, and perform portfolio optimization. You can define your own investment amount, number of simulations, and the stocks you'd like to include in your portfolio.''')



elif page == "Stock Information & Graphs":
    st.markdown("# Stock Information and Visualizations 📈")


    st.markdown("### Stock Descriptions:")
    for stock in available_stocks:
        st.markdown(f"**{stock}:** {stock_descriptions.get(stock, 'No description available.')}")


    st.sidebar.markdown("### Stock Price Visualization")
    selected_stocks = st.sidebar.multiselect("Select stocks to visualize", available_stocks, default=['AAPL'])

    if selected_stocks:
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(6, 4))

        for stock in selected_stocks:
            stock_df = fetch_stock_data(stock)
            if not stock_df.empty:
                ax.plot(stock_df.index, stock_df['close'], label=stock)

        ax.set_title("Stock Closing Prices Over Time", fontsize=12, color='white')
        ax.set_xlabel("Date", fontsize=10, color='white')
        ax.set_ylabel("Price ($)", fontsize=10, color='white')
        ax.legend(loc='upper left', fontsize=8)
        ax.grid(True, linestyle='--', alpha=0.5)

        st.sidebar.pyplot(fig)
        plt.close()

    else:
        st.sidebar.write("Please select at least one stock to plot.")


elif page == "Portfolio Optimization":
    st.markdown("# Portfolio Optimization 🎯")


    st.sidebar.header("Your desired parameters for a portfolio")
    invest_amount = st.sidebar.number_input(label="Please choose the amount you would like to invest:", min_value=100, max_value=1000000, step=100, value=1000)
    n_simulations = st.sidebar.number_input(label="Please choose the number of simulations:", min_value=10, max_value=5000, step=10, value=10)


    all_option = ['Select All']
    desired_stocks = st.sidebar.multiselect(
        "Select stocks to invest in",
        all_option + available_stocks,
        default=None
    )

    if 'Select All' in desired_stocks:
        desired_stocks = available_stocks

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


    click = st.button(label="Get Optimized Weights!")

    if click:
        with st.spinner('Fetching and processing data...'):
            returns, vol, sharpe, weights = fetch_data(desired_stocks, n_simulations)

            average_return_profit = np.mean(returns)
            average_return = np.mean(returns) * 100
            expected_profit = invest_amount * average_return_profit
            average_volatility = np.mean(vol) * 100

            st.markdown("### Portfolio Performance 📈")
            plt.figure(figsize=(10, 6))
            plt.plot(range(1, len(returns) + 1), returns, marker='o', color='#1f77b4')
            plt.title('Annualized Returns vs Number of 30 Minutes Intervals', fontsize=12, color='white')
            plt.xlabel('Number of 30 Minutes Intervals', fontsize=10, color='white')
            plt.ylabel('Annualized Returns (%)', fontsize=10, color='white')
            plt.grid(True)
            st.pyplot(plt)
            plt.close()

            st.markdown("### Portfolio Value Over Time 💼")
            plt.figure(figsize=(10, 6))
            portfolio_value = invest_amount * np.cumprod((np.array(returns) / 5040) + 1)
            plt.plot(range(1, len(returns) + 1), portfolio_value)
            plt.title('Portfolio Value Over Time', fontsize=12, color='white')
            plt.xlabel('Number of 30 Minutes Intervals', fontsize=10, color='white')
            plt.ylabel('Portfolio Value ($)', fontsize=10, color='white')
            plt.grid(True)
            st.pyplot(plt)
            plt.close()

            sum_dict = defaultdict(float)
            for d in weights:
                for key, value in d.items():
                    sum_dict[key] += value
            mean_weights = {key: val / len(weights) for key, val in sum_dict.items()}

            st.markdown("### Average Portfolio Weight Distribution 📊")
            plt.figure(figsize=(10, 6))
            plt.bar(mean_weights.keys(), mean_weights.values(), color='#d62728')
            plt.xlabel('Stocks', fontsize=10, color='white')
            plt.ylabel('Weight', fontsize=10, color='white')
            plt.title('Portfolio Weight Distribution', fontsize=12, color='white')
            plt.grid(True)
            st.pyplot(plt)
            plt.close()

          
            sp_500_return = 20.34
            st.markdown(f"""
                <div style="font-size: 26px; line-height: 1.6;">
                    <p><strong>Average Volatility:</strong> {average_volatility:,.2f}%</p>
                    <p><strong>Average Return:</strong> {average_return:,.2f}%</p>
                    <p><strong>S&P 500 Comparison:</strong>
                        {'Your return is higher' if sp_500_return < average_return else 'Your return is lower'}
                        than the S&P 500 by {abs(sp_500_return - average_return):,.2f}%
                    </p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("### 🎉 **Congratulations on Your Investment!** 🎉", unsafe_allow_html=True)
            st.markdown(f"<h2 style='color: #4CAF50;'>If you invest <strong>{invest_amount:,.2f}</strong> Dollars, you are expected to make <strong>{expected_profit:,.2f}</strong> Dollars profit! 💸</h2>", unsafe_allow_html=True)
            st.balloons()
