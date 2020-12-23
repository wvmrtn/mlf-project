#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Created on Mon Dec 14 18:06:26 2020.

@author: williammartin
"""

# import standard libraries
import os
# import third-party libraries
import pandas as pd
import wrds
# import local libraries
from .config import TICK_NAME


def download_stock_returns(start='2009-07-01', end='2019-12-31', stocks=None):
    """Download stock returns from start to end.

    Parameters
    ----------
    start : str, optional
        Start date to query The default is '2009-07-01'.
    end : str, optional
        End date to query. The default is '2019-12-31'.
    stocks : list, optional
        List of stocks to download returns. The default is None.

    Returns
    -------
    X : pd.DataFrame
        DataFrame containing stock returns from start to end.

    """
    db = wrds.Connection(wrds_username=os.environ['WRDS_USER'],
                         wrds_password=os.environ['WRDS_PASS'])

    if stocks is None:
        stocks = list(TICK_NAME.keys())
    ticker_query = "'" + '\', \''.join(stocks) + "'"

    # get stock data
    stock_data = \
        db.raw_sql(
            f"select permco, ticker from crsp.stocknames where ticker in "
            f"({ticker_query})")
    stock_permco = stock_data['permco'].unique().astype(str)

    # get stock returns
    data = \
        db.raw_sql(
            f"select permco, date, ret from crsp.dsf where permco in "
            f"({', '.join(stock_permco)}) and date >= '{start}' and date "
            f"<= '{end}'")

    data = data.set_index('date')

    # clean into dataframe
    X = pd.DataFrame()
    for permco, df in data.groupby('permco'):
        df = df.drop(columns='permco')
        ticker = stock_data[stock_data['permco'] == permco]['ticker'].values[0]
        df.columns = [ticker]
        X = pd.concat([X, df], axis=1, ignore_index=False)

    return X


def download_market_returns(start='2009-07-01', end='2019-12-31'):
    """Download S&P 500 returns.

    Parameters
    ----------
    start : str, optional
        Start date to download data. The default is '2009-07-01'.
    end : str, optional
        End date to download data. The default is '2019-12-31'.

    Returns
    -------
    F : pd.DataFrame
        DataFrame containing the S&P500 returns from start to end.

    """
    db = wrds.Connection(wrds_username=os.environ['WRDS_USER'],
                         wrds_password=os.environ['WRDS_PASS'])

    # get snp500 returns
    returns = db.raw_sql("select caldt, sprtrn from crsp.dsp500 where "
                         f"caldt >= '{start}' and caldt <= '{end}'"
                         )

    F = pd.DataFrame(returns)
    F.columns = ['date', '^GSPC']
    F = returns.set_index('date')

    return F


def download_rf_returns(start='2009-07-01', end='2019-12-31'):
    """Download riskless returns from Fama-French.

    Parameters
    ----------
    start : str, optional
        Start date to download. The default is '2009-07-01'.
    end : TYPE, optional
        End date to download. The default is '2019-12-31'.

    Returns
    -------
    Rf : pd.DataFrame
        DataFrame containing the returns from start to end.

    """
    db = wrds.Connection(wrds_username=os.environ['WRDS_USER'],
                         wrds_password=os.environ['WRDS_PASS'])

    returns = db.raw_sql("select date, rf from ff.factors_daily where "
                         f"date >= '{start}' and date <= '{end}'"
                         )

    Rf = pd.DataFrame(returns)
    Rf = Rf.set_index('date')

    return Rf


def download_expenditures(start='2010-01-01', end='2019-12-31', stocks=None):

    db = wrds.Connection(wrds_username=os.environ['WRDS_USER'],
                         wrds_password=os.environ['WRDS_PASS'])

    if stocks is None:
        stocks = list(TICK_NAME.keys())
    ticker_query = "'" + '\', \''.join(stocks) + "'"

    # get stock returns
    data = \
        db.raw_sql(
            f"select tic, xrdq, xoprq, datadate from comp.fundq where tic in "
            f"({ticker_query}) and "
            f"datadate >= '{start}' and datadate <= '{end}'"
            )

    # get ration of r&d expenditure wrt to total operating expenses
    data['rd_opr'] = data['xrdq']/data['xoprq']

    # clean a bit
    data = data.drop(columns=['xrdq', 'xoprq'])
    data = data.rename(columns={'datadate': 'date'})
    data = data.set_index('date')
    data = data.pivot_table(values='rd_opr', index=data.index, columns='tic',
                            aggfunc='first')

    return data

if __name__ == '__main__':
    pass
