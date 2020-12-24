#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Created on Wed Dec 23 11:22:15 2020.

@author: williammartin
"""

# import standard libraries
# import third-party libraries
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.model_selection import GridSearchCV
# import local libraries
from mlf import LinearRegressor, SVMRegressor, SVMClassifier

if __name__ == '__main__':

    reg = SVMClassifier()
    reg.generate_xy(num_topics=100, num_days=30)
    reg.scale_x()

    sk = SelectKBest(score_func=f_regression, k=10)
    sk = sk.fit(reg.X_scaled, reg.y['y_bin'])
    X = sk.transform(reg.X_scaled)

    param_grid = {'C': [1, 10, 50, 1000],
                  'gamma': [1, 0.3, 0.1, 0.01]}

    # separate train and test
    X_train, X_test, y_train, y_test = train_test_split(X,
                                                        reg.y['y_bin'],
                                                        test_size=0.2)

    cv = GridSearchCV(reg, param_grid)
    cv = cv.fit(X_train, y_train)
    print(cv.score(X_train, y_train))
    print(cv.score(X_test, y_test))

    # reg = reg.fit(X_train, y_train)
    # print(reg.score(X_train, y_train))
    # print(reg.score(X_test, y_test))
