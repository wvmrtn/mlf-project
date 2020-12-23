#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Created on Wed Dec 23 11:22:15 2020.

@author: williammartin
"""

# import standard libraries
# import third-party libraries
# import local libraries
from mlf import generate_xy

if __name__ == '__main__':
    
    X, y = generate_xy(num_topics=20, num_days=7)
