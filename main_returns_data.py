#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Created on Tue Dec 15 11:27:53 2020.
This file is used to collection returns of stocks of interest and
returns of the benchmark market. Data is saved in the data folder.

@author: williammartin
"""

# import standard libraries
import os
# import third-party libraries
# import local libraries
from mlf import download_stock_returns, download_market_returns
from mlf import download_rf_returns, download_stock_betas

if __name__ == '__main__':

    # get stock returns
    filename = 'data/returns/raw/stock_returns.csv'

    if not os.path.exists(filename):
        # download returns
        returns = download_stock_returns()
        returns.to_csv(filename)

    # get s&p500 returns
    filename = 'data/returns/raw/market_returns.csv'

    if not os.path.exists(filename):
        # download benchmark S&P 500
        returns = download_market_returns()
        returns.to_csv(filename)

    # get riskless rate from fama french
    filename = 'data/returns/raw/rf_returns.csv'

    if not os.path.exists(filename):
        returns = download_rf_returns()
        returns.to_csv(filename)
