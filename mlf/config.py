#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Created on Fri Dec 11 19:29:34 2020.

@author: williammartin
"""

# import standard libraries
# import third-party libraries
# import local libraries

NAME_TICK = {'Bristol-Myers Squibb': 'BMY',
             #'Celgene': None,  # private company
             'Vertex Pharmaceuticals': 'VRTX',
             'Gilead Sciences': 'GILD',
             #'Allergan': None,  # private?
             'Roche': 'RHHBY',
             'Amgen Inc': 'AMGN',
             'Johnson %26 Johnson': 'JNJ',
             'Novo Nordisk': 'NVO',
             'AbbVie': 'ABBV',
             'Pfizer': 'PFE',
             'AstraZeneca': 'AZN',
             'Biogen Idec': 'BIIB',
             #'Shire': None,  # difficult to query shire for patents
             #'sanofi-aventis': None,  # private company
             'Merck': 'MRK',
             'GlaxoSmithKline': 'GSK',
             'Novartis': 'NVS',
             'Regeneron Pharmaceuticals': 'REGN',
             'Bayer Aktiengesellschaft': 'BAYRY',
             'Eli Lilly': 'LLY',
             'Alexion Pharmaceuticals': 'ALXN'}

TICK_NAME = {v: k for k, v in NAME_TICK.items()}

if __name__ == '__main__':
    pass
