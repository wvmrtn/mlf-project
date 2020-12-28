#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Created on Wed Dec 23 11:23:32 2020.

@author: williammartin
"""

# import standard libraries
from datetime import timedelta
import glob
import re
import numpy as np
import pickle
# import third-party libraries
import gensim
from gensim import corpora
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR, SVC
import tensorflow.keras as keras
from keras.layers import Dense
from keras.models import Sequential
from keras.initializers import RandomUniform
from keras.optimizers import SGD
# import local libraries


class BaseModel():

    def __init__(self):
        self.X = pd.DataFrame()
        self.X_info = pd.DataFrame()
        self.y = pd.DataFrame()
        self.X_scaled = pd.DataFrame()
        self.scaler = None

    def scale_x(self, scaler=StandardScaler):
        self.scaler = scaler()
        self.scaler = self.scaler.fit(self.X)
        X_scaled = self.scaler.transform(self.X)
        self.X_scaled = pd.DataFrame(data=X_scaled, index=self.X.index,
                                     columns=self.X.columns)
        return self.X_scaled

    def generate_xy(self, num_topics, num_days, keep_app=True, delay=60):
        """Generate X and y for machine learning model.

        Parameters
        ----------
        num_topics : int
            Number of topics to parse.
        num_days : int
            Number of days to predict.
        keep_app : bool, optional
            Keep only application dates, otherwise grant. The default is True.
        delay : int, optional
            Number days to consider when computing feature. The default is 60.
        scaler : sklearn.preprocessing.OBJ, optional
            Scaler of sklearn.preprocessing to use to scaler the data.

        Returns
        -------
        X : pd.DataFrame
            DataFrame containing features.
        y : pd.DataFrame
            DataFrame containing labels.

        """
        self.num_topics = num_topics
        self.num_days = num_days
        self.keep_app = keep_app
        self.delay = delay

        # get available topics
        NUM_TOPICS = glob.glob(r'data/nlp/*.gensim')
        NUM_TOPICS = [int(re.findall(r'\d+', s)[0]) for s in NUM_TOPICS]
        NUM_DAYS = list(range(2, 61))

        assert num_topics in\
            NUM_TOPICS, f'LDA model not found for {num_topics} topics'
        assert num_days in\
            NUM_DAYS, f'{num_days} outside scope of admissible days'

        # create input and output of models
        # load patent data
        patents = pd.read_csv('data/patents/clean/patents.csv.gz',
                              compression='gzip')
        patents['text'] = patents['text'].apply(lambda x: x.split(' '))

        # load returns
        stocks = pd.read_csv('data/returns/clean/adj_stock_returns.csv',
                             index_col=0)
        stocks.index = pd.to_datetime(stocks.index)

        # load expenses
        expenses = pd.read_csv('data/returns/clean/expenditures.csv',
                               index_col=0)
        expenses.index = pd.to_datetime(expenses.index)

        # load lda model
        ldamodel = gensim.models.ldamodel.LdaModel.load(
            f'data/nlp/model{num_topics}.gensim')

        # remove columns from patents
        keep_col = ['app_number', 'cited_patent_number', 'num_inventor',
                    'patent_num_claims', 'ticker', 'text',
                    'app_date', 'patent_date']
        X = patents[keep_col]

        X.loc[:, 'app_date'] = pd.to_datetime(X.loc[:, 'app_date'])
        X.loc[:, 'patent_date'] = pd.to_datetime(X.loc[:, 'patent_date'])

        # create feature with number of patent applications filed
        # in the last 60 days.
        X['num_app_prior'] = np.nan
        for ticker, x in X.groupby('ticker'):
            for i, patent in x.iterrows():
                app_date_delayed = patent['app_date'] - timedelta(days=delay)
                num_app_prior = len(x[(x['app_date'] >= app_date_delayed) &
                                      (x['app_date'] < patent['app_date'])]
                                    )
                X.at[i, 'num_app_prior'] = num_app_prior

        date_col = ''
        remove = ''
        if keep_app:
            date_col = 'app_date'
            remove = 'patent_date'
        else:
            date_col = 'patent_date'
            remove = 'app_date'
        # rename to date and remove column that we don't need
        X = X.drop(columns=[remove])
        X = X.rename(columns={date_col: 'date'})
        X = X.sort_values(by='date')

        # create feature with scaled R&D expenses
        X['rd_exp'] = np.nan
        for i, (d, row) in enumerate(expenses.iterrows()):
            if i < len(expenses)-1:
                xd = X[(X['date'] >= d) & (X['date'] < expenses.index[i+1])]
                X.at[xd.index, 'rd_exp'] = xd['ticker'].apply(
                    lambda x: row.get(x))

        # create corpora and dictionary
        dictionary = pickle.load(open('data/nlp/dictionary.pkl', 'rb'))
        #  dictionary = corpora.Dictionary(list(patents['text'].values))

        # create feature with topic extraction from lda modela
        X[[f'topic{t}' for t in range(num_topics)]] = 0.0

        for i, x in X.iterrows():
            new_doc_bow = dictionary.doc2bow(x['text'])
            t_prob = ldamodel.get_document_topics(new_doc_bow,
                                                  minimum_probability=0.0)
            for t in t_prob:
                X.at[i, 'topic'+str(t[0])] = t[1]

        # drop columns that are not needed
        X = X.drop(columns=['text'])

        # remove all dates that are on 2010-01-04 (starting day of stocks)
        # since we need to get 1 day of returns prior to date
        X = X[X['date'] > '2010-01-04']

        # define y output
        y = pd.DataFrame(index=X.index, columns=['y_ret', 'y_bin'],
                         data=np.nan)

        for i, x in X.iterrows():
            # get returns one day before date
            sub = stocks[x['ticker']]
            ret_before = sub[sub.index < x['date']].iloc[-1:]
            ret_after = sub[sub.index >= x['date']].iloc[:num_days-1]
            ret = pd.concat([ret_before, ret_after], axis=0)
            ret = (ret + 1).cumprod(axis=0).iloc[-1]-1
            y.at[i, 'y_ret'] = ret
            y.at[i, 'y_bin'] = 0 if ret < 0 else 1

        # remove nans in y (some stocks were not publicly traded before
        # some date)
        index_drop = y[y['y_ret'].isna()].index
        y = y.drop(index=index_drop)
        X = X.drop(index=index_drop)

        # get X for model and X containing info of X
        self.X_info = X[['app_number', 'ticker', 'date']]
        self.X = X.drop(columns=['app_number', 'ticker', 'date'])
        self.y = y

        return X, y


class LinearRegressor(LinearRegression, BaseModel):

    def __init__(self):
        super().__init__()


class SVMRegressor(SVR, BaseModel):

    def __init__(self, gamma='scale', C=1.0):
        super().__init__(gamma=gamma, C=C)

    
class SVMClassifier(SVC, BaseModel):

    def __init__(self, gamma='scale', C=1.0):
        super().__init__(gamma=gamma, C=C)
        self.train_acc = None
        self.test_acc = None


class NNClassifier(Sequential, BaseModel):

    def __init__(self):
        super().__init__()

    def add_layers(self, features_dim, neurons, layers, activation='sigmoid'):
        init = RandomUniform(minval=-1, maxval=1)

        # Input layer:
        self.add(Dense(units=neurons,
                       input_dim=features_dim,
                       activation='sigmoid',
                       kernel_initializer=init,
                       bias_initializer=init))

        # Add dense layers in sequence
        for i in range(layers):
            self.add(Dense(units=neurons,
                           activation=activation,
                           kernel_initializer=init,
                           bias_initializer=init))

        # Output layer:
        self.add(Dense(1, activation='sigmoid', kernel_initializer=init))


    def define_optimizer(self, lr):
        opt = SGD(lr=lr, momentum=0.9)
        self.compile(loss='binary_crossentropy', optimizer=opt,
                     metrics=['accuracy'])


if __name__ == '__main__':
    pass
