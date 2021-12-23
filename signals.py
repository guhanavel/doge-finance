import streamlit
import yfinance as yf
import streamlit as stream
import datetime as dt
import pandas as pd
import pandas_datareader as web
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from GoogleNews import GoogleNews
import time
import csv
import re


def read_csv(csvfilename):
    """
    Reads a csv file and returns a list of lists
    containing rows in the csv file and its entries.
    """
    with open(csvfilename, encoding='utf-8') as csvfile:
        rows = [row for row in csv.reader(csvfile)]
    return rows[1:]


NASQ = read_csv(r"C:\Users\Asus\Downloads\nasdaq_screener_1640064404227.csv")


def listtostring(s):
    # initialize an empty string
    str1 = " "

    # return string
    return str1.join(s)


def lookup(cs):
    dic = {}
    for c in cs:
        wordList = c[1].split()
        dic[listtostring(wordList[:3])] = c[0]
    return dic


TODAY = dt.date.today()
stream.title("Stock Analysis")

searchlist = tuple(lookup(NASQ).keys()) + tuple(lookup(NASQ).values())

tic = stream.selectbox("Stock Code", searchlist)


def convert(t):
    if t in lookup(NASQ).keys():
        return lookup(NASQ)[t]
    else:
        return t
m = stream.markdown("""
<style>
div.stButton > button:first-child {
    background-color: rgb(204, 49, 49);
}
</style>""", unsafe_allow_html=True)

START = stream.date_input("Start Date", value=pd.to_datetime("01-01-2012", format="%d-%m-%Y"), max_value=TODAY)

END = stream.date_input("End Date", min_value=START, max_value=TODAY)


@stream.cache(allow_output_mutation=True)
def load_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end)
    data.reset_index(inplace=False)
    return data


Test = stream.form("Test")
submit = Test.form_submit_button("6MO")
sub = Test.form_submit_button("Submit")
if submit:
    data_read = load_data(convert(tic), dt.datetime.today() - dt.timedelta(days=90), TODAY)
if sub:
    data_read = load_data(convert(tic), START, END)
stream.subheader("Last 5 days")
stream.write(data_read.tail())

close_dat = data_read['Adj Close']
MA_200 = close_dat.rolling(window=200).mean()
MA_50 = close_dat.rolling(window=50).mean()
MA_100 = close_dat.rolling(window=100).mean()
new_data = {'Adj Close': close_dat, 'MA_200': MA_200, 'MA_50': MA_50, 'MA_100': MA_100}
stream.subheader('Stock Graph')
stream.line_chart(new_data)

stock_signal = pd.DataFrame(index=data_read.index)
stock_signal['Price'] = close_dat
stock_signal['Daily Difference'] = stock_signal['Price'].diff()
stock_signal['Signal'] = 0.0
stock_signal['Signal'] = np.where(stock_signal['Daily Difference'] > 0, 1.0, 0.0)
stock_signal['Positions'] = stock_signal['Signal'].diff()
stream.subheader("News")
s = yf.Ticker(convert(tic)).news
i = yf.Ticker(convert(tic)).info
r = yf.Ticker(convert(tic)).recommendations

def info(inf):
    return inf["longBusinessSummary"]

def news_api(news):
    fin = {'Date': [], "News": [], "Link": []}
    for n in range(len(news)):
        fin["Date"].append(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(news[n]["providerPublishTime"])))
        fin["News"].append(news[n]['title'])
        fin['Link'].append(news[n]['link'])
    df2 = pd.DataFrame(data=fin)
    return df2


googlenews = GoogleNews(start="01/01/2012", end="23/12/2021")
googlenews.search(tic)
result = googlenews.result()
fin = {'Date': [], "News": [], "Link": []}
for n in range(len(result)):
    fin["Date"].append(result[n]["datetime"])
    fin["News"].append(result[n]["desc"])
    fin["Link"].append(result[n]["link"])
df = pd.DataFrame(data=fin)
stream.write(news_api(s))
stream.write(df.tail(30))
stream.subheader("Information")
stream.write(info(i))
stream.subheader("Recommendation")
stream.write(r)

