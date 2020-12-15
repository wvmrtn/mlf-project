#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Created on Fri Dec 11 15:46:11 2020.

@author: williammartin
"""

# import standard libraries
import requests
# import third-party libraries
import dask
import pandas as pd
# import local libraries
from .config import QUERY_FEAT, ENDPOINTS

dask.config.set(scheduler="processes")


def query_patent(assignee, start_date, end_date):
    """Get patent information from query.

    Parameters
    ----------
    assignee : str
        Organisation of patent.
    start_date : str
        Start date to query filing dates. Format: YYYY-MM-DD.
    end_date : strin
        End date to query filing dates. Format: YYYY-MM-DD..

    Returns
    -------
    content : json
        Content of request.

    """
    feat = ['"' + f + '"' for f in QUERY_FEAT]
    feat = '[' + ','.join(feat) + ']'
    url = 'https://api.patentsview.org/patents/query?' +\
          'q={"_and":' +\
          '[' +\
          '{"_contains":{"assignee_organization":"' + assignee + '"}},' +\
          '{"_gte":{"app_date":"' + start_date + '"}},' +\
          '{"_lte":{"app_date":"' + end_date + '"}}' +\
          ']' +\
          '}' +\
          '&f=' + feat + \
          '&o={"page":1,"per_page":10000}'

    response = requests.get(url)
    content = response.json()

    return content


def parse_patent(content):
    """Parse request content into parsed data.

    Parameters
    ----------
    content : json
        Content of request.

    Returns
    -------
    parsed : pd.DataFrame
        pd.DataFrame containing parsed patent information.

    """
    parsed = pd.DataFrame(columns=QUERY_FEAT, index=range(content['count']))
    content = content['patents']

    if content:
        for i, c in enumerate(content):
            for _, row in ENDPOINTS.iterrows():
                if row[1] == 'patents':
                    key = row[0]
                    parsed.at[i, key] = c[key]
                else:
                    key = row[1]
                    subkey = row[0]
                    if key in ['wipos', 'nbers', 'uspcs', 'cpcs', 'assignees']:
                        temp = []
                        for k in c[key]:
                            if k[subkey] is not None:
                                temp.append(k[subkey])
                        parsed.at[i, subkey] = ' '.join(temp)

                    elif key in ['inventors', 'citedby_patents',
                                 'cited_patents']:
                        parsed.at[i, subkey] = len(c[key])

                    elif key in ['applications']:
                        parsed.at[i, subkey] = c[key][0][subkey]
                        if len(c[key]) > 1:
                            print(c[key])

        parsed = parsed.rename(columns={'inventor_id': 'num_inventor'})

    return parsed


@dask.delayed
def read_patent_file(filepath):
    patent = pd.read_csv(filepath, compression='gzip')
    return patent


if __name__ == '__main__':
    pass
