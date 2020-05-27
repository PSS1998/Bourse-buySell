import datetime as dt
from datetime import timedelta
import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np
import pandas as pd
import talib as ta
import gzip
import os
from os import listdir






def process_stock(ticker):
	returnString = ""
	buySignal = 0
	sellSignal = 0

	
	with open("../bourse_price/"+ticker, 'rb') as fd:
		gzip_fd = gzip.GzipFile(fileobj=fd)	
		df = pd.read_csv(gzip_fd, encoding = "utf-8")
		if(not df.empty):
			#df.drop(df.head(2).index, inplace=True)
			df["<DTYYYYMMDD>"] =  pd.to_datetime(df["<DTYYYYMMDD>"], format="%Y%m%d")
			now = dt.datetime.now() - timedelta(days=3)
			if df["<DTYYYYMMDD>"][0] < now:
				return "", ""
			df.reset_index(inplace=True)
			df.set_index("<DTYYYYMMDD>", inplace=True)
			df = df.drop("<PER>", axis=1)
			df = df.drop("index", axis=1)
			df.dropna(inplace=True)
			df = df.iloc[::-1]
		else:
			return "", ""



		cci_one = ta.CCI(np.array(df['<HIGH>'].astype(float)), np.array(df['<LOW>'].astype(float)), np.array(df['<CLOSE>'].astype(float)), timeperiod=170)
		cci_two = ta.CCI(np.array(df['<HIGH>'].astype(float)), np.array(df['<LOW>'].astype(float)), np.array(df['<CLOSE>'].astype(float)), timeperiod=34)
		mfi = ta.MFI(np.array(df['<HIGH>'].astype(float)), np.array(df['<LOW>'].astype(float)), np.array(df['<CLOSE>'].astype(float)), np.array(df['<VOL>'].astype(float)))



		if( (cci_one[-1] < -100) & (cci_two[-1] < -100) & (mfi[-1] < 25) ):
			return "buy"
		if( (cci_one[-1] > 100) & (cci_two[-1] > 100) ):
			return "sell"


		


def get_stock():
	with open('../index.txt') as f:
	    tickers = f.read().splitlines()
	    # tickers = [f for f in listdir()]
	    # tickers.sort()
	    count = 0
	    for ticker in tickers:
	        if count == 0:
	            count += 1
	            continue
	        print(ticker)
	        signal = process_stock(ticker)
	        print(signal)
	        print("")
	        count += 1


get_stock()
