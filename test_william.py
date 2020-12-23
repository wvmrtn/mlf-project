#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Created on Wed Dec 23 11:22:15 2020.

@author: williammartin
"""

# import standard libraries
# import third-party libraries
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectKBest, f_regression
# import local libraries
from mlf import LinearRegressor

if __name__ == '__main__':

    lr = LinearRegressor()
    lr.generate_xy(num_topics=50, num_days=3)
    lr.scale_x()

    # sk = SelectKBest(score_func=f_regression, k=5)
    # sk = sk.fit(lr.X_scaled, lr.y['y_bin'])
    # X = sk.transform(lr.X_scaled)

    # separate train and test
    X_train, X_test, y_train, y_test = train_test_split(lr.X_scaled,
                                                        lr.y['y_ret'],
                                                        test_size=0.2)

    reg = lr.fit(X_train, y_train)
    print(reg.score(X_train, y_train))
    print(reg.score(X_test, y_test))
