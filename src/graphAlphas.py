#!/usr/local/bin/python

from core.rl.portfolio import evalLinUCB
from core.util.graphics import plot
from core.util.data import Featurizer, StockHistory

alphas = [0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
testSizes = [0.1*i for i in range(1, 10)]
stockHistory = StockHistory('nasdaq100')
featurizer = Featurizer(stockHistory)
alphaCAGRs = []
for alpha in alphas :
	CAGRs = evalLinUCB(stockHistory, featurizer, alpha=alpha)
	alphaCAGRs.append(CAGRs)

plot(alphaCAGRs,
	xss=[testSizes for i in range(len(alphaCAGRs))],
	labels=[str(a) for a in alphas],
	xlabel='Testing Percentage',
	ylabel='CAGR',
	legendLoc='lower right')