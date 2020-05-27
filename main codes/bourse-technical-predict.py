import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np
import pandas as pd
import talib as ta
import gzip
import os
from os import listdir

style.use('ggplot')





def STOD(close, low, high, n):
	#STOK = ((close - pd.rolling_min(low, n)) / (pd.rolling_max(high, n) - pd.rolling_min(low, n))) * 100
	STOK = ((close - low.rolling(window=n, min_periods=0).min()) / (high.rolling(window=n, min_periods=0).max() - low.rolling(window=n, min_periods=0).min())) * 100
	#STOD = pd.rolling_mean(STOK, 3)
	STOD = STOK.rolling(window=3, min_periods=0).mean()
	return STOD



def process_stock(ticker):
	returnString = ""
	buySignal = 0
	sellSignal = 0

	
	with open(ticker, 'rb') as fd:
		gzip_fd = gzip.GzipFile(fileobj=fd)	
		df = pd.read_csv(gzip_fd, encoding = "utf-8")
		if(not df.empty):
			#df.drop(df.head(2).index, inplace=True)
			df["<DTYYYYMMDD>"] =  pd.to_datetime(df["<DTYYYYMMDD>"], format="%Y%m%d")
			df.reset_index(inplace=True)
			df.set_index("<DTYYYYMMDD>", inplace=True)
			df = df.drop("<PER>", axis=1)
			df = df.drop("index", axis=1)
			df.dropna(inplace=True)
			df = df.iloc[::-1]
		else:
			return "", ""

		RSI = ta.RSI(np.array(df['<CLOSE>'].astype(float)))#under 30 should buy, higher than 70 should sell
		if RSI[-1]<30:
			buySignal += 1
			returnString += " RSI:buy "
		if RSI[-1]>70:
			sellSignal += 1
			returnString += " RSI:sell "
		MA10 = ta.EMA(np.array(df['<CLOSE>'].astype(float)), timeperiod=10)
		MA30 = ta.EMA(np.array(df['<CLOSE>'].astype(float)), timeperiod=30)
		MA50 = ta.EMA(np.array(df['<CLOSE>'].astype(float)), timeperiod=50)#exponantial moving average
		if((MA10[-1] >= MA30[-1] and MA10[-2] < MA30[-2]) or ((MA30[-1] >= MA50[-1] and MA30[-2] < MA50[-2]))):
			buySignal += 1
			returnString += " MA:buy(simillar to MACDFIX) "
		if((MA10[-1] <= MA30[-1] and MA10[-2] > MA30[-2]) or (MA30[-1] <= MA50[-1] and MA30[-2] > MA50[-2])):
			sellSignal += 1
			returnString += " MA:sell(simillar to MACDFIX) "
		SAR = ta.SAR(np.array(df['<HIGH>'].astype(float)), np.array(df['<LOW>'].astype(float)))#best for stable markets and may cause premature signals
		if(SAR[-2]<df['<CLOSE>'].iloc[-2] and SAR[-1]>=df['<CLOSE>'].iloc[-1]):
			sellSignal += 1
			returnString += " SAR:buy(best for stable markets) "
		if(SAR[-2]>df['<CLOSE>'].iloc[-2] and SAR[-1]<=df['<CLOSE>'].iloc[-1]):
			buySignal += 1
			returnString += " SAR:sell(best for stable markets) "
		# Stoch = ta.STOCH(np.array(df['<HIGH>']), np.array(df['<LOW>']), np.array(df['<CLOSE>']))
		STOCH = np.array(STOD(df['<CLOSE>'], df['<LOW>'], df['<HIGH>'], 14))#Readings above 80 are considered overbought while readings below 20 are considered oversold.
		if STOCH[-1]<20:
			buySignal += 1
			returnString += " STOCH:buy(similar to RSI) "
		if STOCH[-1]>80:
			sellSignal += 1
			returnString += " STOCH:sell(similar to RSI) "
		'''
		for i in range(len(Stoch[0])-8):
			Stoch[0][i+8] = Stoch[0][i+8]/Stoch[0][8:].max()*100
			Stoch[1][i+8] = Stoch[1][i+8]/Stoch[1][8:].max()*100
		'''
		# ATR = ta.ATR(np.array(df['<HIGH>'].astype(float)), np.array(df['<LOW>'].astype(float)), np.array(df['<CLOSE>'].astype(float)), timeperiod=10)#difrrent in each case
		AD = ta.AD(np.array(df['<HIGH>'].astype(float)), np.array(df['<LOW>'].astype(float)), np.array(df['<CLOSE>'].astype(float)), np.array(df['<VOL>'], dtype=np.double))#Upward :more buying than selling
		if(AD[-1] > AD[-2] and AD[-2] > AD[-3]):
			buySignal += 1
			returnString += " AD:buy(not defenitive) "
		elif(AD[-1] < AD[-2] and AD[-2] < AD[-3]):
			sellSignal += 1
			returnString += " AD:sell(not defenitive) "
		ADX = ta.ADX(np.array(df['<HIGH>'].astype(float)), np.array(df['<LOW>'].astype(float)), np.array(df['<CLOSE>'].astype(float)))#readings below 20 that signal a weak trend or readings above 40 that signal a strong trend.
		if(ADX[-1]>40):
			buySignal += 1
			sellSignal += 1
			returnString += " ADX:strong trend "
		elif(ADX[-1]<20):
			buySignal -= 1
			sellSignal -= 1
			returnString += " ADX:week trend "
		AROONOSC = ta.AROONOSC(np.array(df['<HIGH>'].astype(float)), np.array(df['<LOW>'].astype(float)))
		if(AROONOSC[-1]>50):
			buySignal += 1
			returnString += " AROONOSC:buy "
		elif(AROONOSC[-1]<-50):
			sellSignal += 1
			returnString += " AROONOSC:sell "
		MACDFIX = ta.MACDFIX(np.array(df['<CLOSE>'].astype(float)))
		if(MACDFIX[0][-1]<0 and MACDFIX[0][-1]>=0):
			buySignal += 1
			returnString += " MACDFIX:buy "
		if(MACDFIX[0][-1]>0 and MACDFIX[0][-1]<=0):
			sellSignal += 1
			returnString += " MACDFIX:sell "
		# print(df['<CLOSE>'])
		# print(type(df['<DTYYYYMMDD>'].iloc[-1]))
		# print(MACDFIX)
		# plt.plot(df['<DTYYYYMMDD>'], df['<CLOSE>'])
		# df.plot(x='<DTYYYYMMDD>', y='<CLOSE>')
		# df['<CLOSE>'].plot()
		# plt.plot(ADX)
		# plt.plot(MACDFIX[1])
		# plt.plot(MACDFIX[2])
		# plt.legend(loc=4)
		# plt.xlabel('Date')
		# plt.ylabel('Price')
		# plt.show()



		# print(buySignal)
		# print(sellSignal)
		'''
		if(buySignal>sellSignal and buySignal>=3):
			# print("buy: {}".format(buySignal))
			return "buy: {}".format(buySignal)
		elif(buySignal<sellSignal and sellSignal>=3):
			# print("sell: {}".format(sellSignal))
			return "sell: {}".format(sellSignal)
		else:
			# print("hold")
			return "hold"
		'''
		return "buy: {} - sell: {}".format(buySignal, sellSignal), returnString
		'''

		#%matplotlib inline

		def get_stock(stock,start,end):
		 return web.DataReader(stock,'google',start,end)['Close']

		def get_high(stock,start,end):
		 return web.DataReader(stock,'google',start,end)['High']

		def get_low(stock,start,end):
		 return web.DataReader(stock,'google',start,end)['Low']

		def STOK(close, low, high, n): 
		 STOK = ((close - pd.rolling_min(low, n)) / (pd.rolling_max(high, n) - pd.rolling_min(low, n))) * 100
		 return STOK

		def STOD(close, low, high, n):
		 STOK = ((close - pd.rolling_min(low, n)) / (pd.rolling_max(high, n) - pd.rolling_min(low, n))) * 100
		 STOD = pd.rolling_mean(STOK, 3)
		 return STOD

		df = pd.DataFrame(get_stock('FB', '1/1/2016', '12/31/2016'))
		df['High'] = get_high('FB', '1/1/2016', '12/31/2016')
		df['Low'] = get_low('FB', '1/1/2016', '12/31/2016')
		df['%K'] = STOK(df['Close'], df['Low'], df['High'], 14)
		df['%D'] = STOD(df['Close'], df['Low'], df['High'], 14)
		df.tail()

		'''


def get_stock():
    tickers = [f for f in listdir()]
    tickers.sort()
    count = 0
    for ticker in tickers:
        if count == 0:
            count += 1
            continue
        print(ticker)
        signal, returnString = process_stock(ticker)
        print(signal)
        print(returnString)
        print("")
        count += 1


get_stock()
