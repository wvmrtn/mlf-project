#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Created on Sat Dec 12 16:48:23 2020.

@author: williammartin
"""

# import standard libraries
import os
from datetime import datetime, timedelta
# import third-party libraries
import pandas as pd
# import local libraries
from mlf import query_patent, parse_patent
from mlf import NAME_TICK
from mlf import QUERY_FEAT

if __name__ == '__main__':

    # start and end date
    start = '2010-01-01'
    end = '2019-12-31'

    start_dates = pd.date_range(start, end, freq='YS')
    start_dates = start_dates.strftime("%Y-%m-%d")

    end_dates = pd.date_range(start, end, freq='Y')
    end_dates = end_dates.strftime("%Y-%m-%d")

    for o in NAME_TICK.keys():
        for d, _ in enumerate(start_dates):
            # write only if does not exist
            filename = 'data/patents/raw/{}_{}.csv'.format(NAME_TICK[o],
                                                           start_dates[d][:4])
            if not os.path.exists(filename):
                content = query_patent(o.lower(),
                                       start_dates[d],
                                       end_dates[d])
                parsed = parse_patent(content)

                parsed.to_csv(filename)