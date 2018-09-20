import bs4 as bs
import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np
import os
from os import listdir
import pandas as pd
#import pandas_datareader.data as web
#import pickle
import requests
from collections import Counter
from sklearn import svm, cross_validation, neighbors
from sklearn.ensemble import VotingClassifier, RandomForestClassifier

style.use('ggplot')


def save_sp500_tickers():
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        tickers.append(ticker)
    with open("sp500tickers.pickle", "wb") as f:
        pickle.dump(tickers, f)
    return tickers


# save_sp500_tickers()
def get_data_from_yahoo(reload_sp500=False):
    if reload_sp500:
        tickers = save_sp500_tickers()
    else:
        with open("sp500tickers.pickle", "rb") as f:
            tickers = pickle.load(f)
    if not os.path.exists('stock_dfs'):
        os.makedirs('stock_dfs')

    start = dt.datetime(2010, 1, 1)
    end = dt.datetime.now()
    for ticker in tickers:
        # just in case your connection breaks, we'd like to save our progress!
        if not os.path.exists('stock_dfs/{}.csv'.format(ticker)):
            df = web.DataReader(ticker, 'morningstar', start, end)
            df.reset_index(inplace=True)
            df.set_index("Date", inplace=True)
            df = df.drop("Symbol", axis=1)
            df.to_csv('stock_dfs/{}.csv'.format(ticker))
        else:
            print('Already have {}'.format(ticker))


def get_data_from_HDD():
    main_df = pd.DataFrame()

    count = 0

    tickers = [f for f in listdir()]
    tickers.sort()
    print(tickers)
    print(len(tickers))
    for ticker in tickers:
        if count == 0:
            print("0")
            count += 1
            continue
        df = pd.read_csv(ticker)
        df.reset_index(inplace=True)
        df.set_index("<DTYYYYMMDD>", inplace=True)
        df = df.drop("<PER>", axis=1)
        df = df.drop("index", axis=1)

        df.rename(columns={'<CLOSE>': ticker}, inplace=True)
        df.drop(['<LAST>', '<OPEN>', '<OPENINT>', '<VOL>', '<VALUE>', '<LOW>', '<HIGH>', '<FIRST>'], 1, inplace=True)

        if main_df.empty:
            main_df = df
#            main_df.set_index("<DTYYYYMMDD>", inplace=True)
        else:
            main_df = pd.merge(main_df, df, on='<DTYYYYMMDD>', how='outer')

        if count % 10 == 0:
            print(count)
        count += 1
#    df.reset_index(inplace=True)
#    main_df.set_index('<DTYYYYMMDD>', inplace=True)
    main_df = main_df.sort_values('<DTYYYYMMDD>', ascending=False)
    print(main_df.columns)
    main_df = main_df.drop('<TICKER>_x', axis=1)
    main_df = main_df.drop('<TICKER>_y', axis=1)
    print(main_df.columns)
#    for i in range(2,54):
#        main_df = main_df.drop('<TICKER>_x.{}'.format(i), axis=1)
#    for i in range(2,54):
#        main_df = main_df.drop('<TICKER>_y.{}'.format(i), axis=1)
    print(main_df.head())
    main_df.to_csv('iran-bource_joined_closes.csv')

#get_data_from_HDD()



def compile_data():
    with open("sp500tickers.pickle", "rb") as f:
        tickers = pickle.load(f)

    main_df = pd.DataFrame()

    for count, ticker in enumerate(tickers):
        df = pd.read_csv('stock_dfs/{}.csv'.format(ticker))
        df.set_index('Date', inplace=True)

        df.rename(columns={'Adj Close': ticker}, inplace=True)
        df.drop(['Open', 'High', 'Low', 'Close', 'Volume'], 1, inplace=True)

        if main_df.empty:
            main_df = df
        else:
            main_df = main_df.join(df, how='outer')

        if count % 10 == 0:
            print(count)
    print(main_df.head())
    main_df.to_csv('sp500_joined_closes.csv')


def visualize_data():
    df = pd.read_csv('iran-bource_joined_closes.csv')
    df = df.drop('<DTYYYYMMDD>', axis=1)
    df_corr = df.corr()
    print(df_corr.head())
    df_corr.to_csv('sp500corr.csv')
    data1 = df_corr.values
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)

    heatmap1 = ax1.pcolor(data1, cmap=plt.cm.RdYlGn)
    fig1.colorbar(heatmap1)

    ax1.set_xticks(np.arange(data1.shape[1]) + 0.5, minor=False)
    ax1.set_yticks(np.arange(data1.shape[0]) + 0.5, minor=False)
    ax1.invert_yaxis()
    ax1.xaxis.tick_top()
    column_labels = df_corr.columns
    row_labels = df_corr.index
    ax1.set_xticklabels(column_labels)
    ax1.set_yticklabels(row_labels)
    plt.xticks(rotation=90)
    heatmap1.set_clim(-1, 1)
    plt.tight_layout()
    plt.show()

#visualize_data()


def process_data_for_labels(ticker):
    hm_days = 4
    df = pd.read_csv('iran-bource_joined_closes.csv', index_col=0)
    df = df.drop('Abiak.Cement.csv', axis=1)
    tickers = df.columns.values.tolist()
    df.fillna(0, inplace=True)
    for i in range(1, hm_days+1):
        df['{}_{}d'.format(ticker, i)] = (df[ticker].shift(-i) - df[ticker]) / df[ticker]
    df.fillna(0, inplace=True)
    return tickers, df


def buy_sell_hold(*args):
    cols = [c for c in args]
    requirement1 = 0.02
    requirement2 = 0.02
    for col in cols:
        if col > requirement1:
            return 1
        if col < -requirement2:
            return -1
    return 0


def extract_featuresets(ticker):
    tickers, df = process_data_for_labels(ticker)

    df['{}_target'.format(ticker)] = list(map( buy_sell_hold,
                                               df['{}_1d'.format(ticker)],
                                               df['{}_2d'.format(ticker)],
                                               df['{}_3d'.format(ticker)],
                                               df['{}_4d'.format(ticker)]
#                                               ,df['{}_5d'.format(ticker)],
#                                               df['{}_6d'.format(ticker)],
#                                               df['{}_7d'.format(ticker)]
                                               ))

    vals = df['{}_target'.format(ticker)].values.tolist()
    str_vals = [str(i) for i in vals]
    print('Data spread:', Counter(str_vals))

    df.fillna(0, inplace=True)
    df = df.replace([np.inf, -np.inf], np.nan)
    df.dropna(inplace=True)

    df_vals = df[[ticker for ticker in tickers]].pct_change()
    df_vals = df_vals.replace([np.inf, -np.inf], 0)
    df_vals.fillna(0, inplace=True)

    X = df_vals.values
    y = df['{}_target'.format(ticker)].values
    return X, y, df


def do_ml(ticker):
    X, y, df = extract_featuresets(ticker)

    X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.25)

    clf = VotingClassifier([('lsvc', svm.LinearSVC()),
                            ('knn', neighbors.KNeighborsClassifier()),
                            ('rfor', RandomForestClassifier())])

    clf.fit(X_train, y_train)
    confidence = clf.score(X_test, y_test)
    print('accuracy:', confidence)
    clf.fit(X_train[:-1], y_train[:-1])
    predictions_test = clf.predict(X_test)
    predictions = clf.predict(X_test[-1].reshape(1,-1))
    print(predictions)
    print('predicted class counts:', Counter(predictions_test))
#    print()
#    print()
    return confidence


#do_ml('Kimia.Zanjan.Co.csv')

#'''
from statistics import mean

#'Abiak.Cement.csv',3d one
tickers = ['A..I..S..D..csv', 'A.S.P.CO.csv', 'Alborz.Bimeh.csv', 'Alborz.Cable.csv', 'Ama.csv', 'Amin.Company.csv', 'Amirkabir.Steel.csv', 'Arak.M..Mfg..csv', 'Asan.Pardakht.Pers.csv', 'Asia.Bime.csv', 'Atieh.Dade.Pardaz.csv', 'Azar.Refract..csv', 'Bahman.Group.csv', 'Bahman.Liz..csv', 'Behpak.Co..csv', 'Behpardakht.Mellat.csv', 'Behshahr.Inv..csv', 'Bime.Ma.Co..csv', 'Bime.Saman.Co..csv', 'Buali.Inv..csv', 'Butane.Group.csv', 'Charkheshgar.csv', 'Derakhshan.Teh..csv', 'Doode.Sanati.csv', 'F..&.Kh..Cement.csv', 'Fars.Chem..Ind..csv', 'Fars.Dev..csv', 'G.Barekat.Pharm.csv', 'Gadir.Petro..csv', 'Ghandi.Cables..csv', 'Ghazvin.Sugar.csv', 'Glass.and.Gas.csv', 'Goltash.csv', 'Hamadan.Glass.csv', 'I..Pegah.Dairy.csv', 'Indamin.csv', 'Int..Const..csv', 'Investment.Banking.csv', 'Ir.Inv.Petr..csv', 'Iran.Carbon.csv', 'Iran.China.Clay.csv', 'Iran.Combine.csv', 'Iran.Const..Inv.csv', 'Iran.Ferr..csv', 'Iran.Fold.csv', 'Iran.Glass.Wool.csv', 'Iran.Kh..Inv..csv', 'Iran.Radiator.csv', 'Iran.Tele..Co..csv', 'Iran.Tire.csv', 'Iran.Tractor.M..csv', 'Iran.Yasa.Tire.csv', 'Iranian.Etekai.csv', 'Iranian.Lizing.csv', 'Kaveh.Paper.csv', 'Kavir.Tire.csv', 'Kerman.Invest.csv', 'Kerman.Tire.csv', 'Khalij.Fars.Trans.csv', 'Kharazmi.Info..csv', 'Kimia.Zanjan.Co.csv', 'Loabiran.csv', 'Lorestan.Sugar.csv', 'Maskan.Invest..csv', 'Maskan.Pardis.csv', 'Mellat.Bank.csv', 'Mihan.Insurance.csv', 'Motogen.csv', 'Motorsazan.csv', 'Negin.Tabas.L..csv', 'Nirou.Trans.csv', 'Pak.Dairy.csv', 'Pardis.Petr..csv', 'Pars.Int..Mfg..csv', 'Pars.Khazar.csv', 'Pars.Paper.Ind.Grp.csv', 'Pars.Refract..csv', 'Pars.Shahab.csv', 'Pars.Switch.csv', 'Parsian.Oil&Gas.csv', 'Parsian.csv', 'Paxan.csv', 'Petr..Tran..csv', 'Petro..Inv..csv', 'Piazar.Agro..csv', 'Plascokar.Saipa.csv', 'Pumpiran.csv', 'Rena.Investment.csv', 'Sahand.Rubber.csv', 'Saina.Company.csv', 'Saipa.Azin.csv', 'Saipa.Glass.csv', 'Sand.Foundry.csv', 'Sarma.Afarin.csv', 'Sepahan.Group.csv', 'Shahed.Development.csv', 'Shahed.Inv..csv', 'Shahroud.Sugar.csv', 'Shiraz.Petr..csv', 'Sina.Chem..Ind..csv', 'Tabas.Company.csv', 'Tehran.Stock.Exch..csv', 'Toucaril.Co..csv', 'Tuka.Paint.Co..csv', 'Tuka.Trans..csv', 'Zar.Spring.csv', 'producing.CHDN.csv']

accuracies = []
for count,ticker in enumerate(tickers):

    if count%10==0:
        print(count)

    accuracy = do_ml(ticker)
    accuracies.append(accuracy)
    print("{} accuracy: {}. Average accuracy:{}".format(ticker,accuracy,mean(accuracies)))
    print()
    print()


#'''