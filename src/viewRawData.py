#!/usr/local/bin/python

import sys
from core.util import data
from core.util.graphics import plot, plotDistribution

dataSet = sys.argv[1]
companiesToGraph = sys.argv[2:]
stockHistory = data.StockHistory(dataSet)

if len(companiesToGraph) > 0 :
    print 'Generating graphs.'
for compName in companiesToGraph :
    compName = compName.upper()
    if not stockHistory.hasCompanyData(compName) :
        print 'No data for company', compName
        continue
    openYs = stockHistory.getData(compName, data.OPEN)
    highYs = stockHistory.getData(compName, data.HIGH)
    lowYs = stockHistory.getData(compName, data.LOW)
    closeYs = stockHistory.getData(compName, data.CLOSE)
    plot([openYs, highYs, lowYs, closeYs],
        labels=['Open', 'High', 'Low', 'Close'],
        title=compName,
        xlabel='Time',
        ylabel='Stock Price')
"""
sharpeRatios = []
for comp in stockHistory.compNames() :
    sharpeRatios += stockHistory.nDaySharpeRatio(5, comp, data.OPEN)
plotDistribution(sharpeRatios, -7, -1)

sharpeRatios = []
for comp in stockHistory.compNames() :
    sharpeRatios += stockHistory.nDaySharpeRatio(10, comp, data.OPEN)
plotDistribution(sharpeRatios, -7, 0)

sharpeRatios = []
for comp in stockHistory.compNames() :
    sharpeRatios += stockHistory.nDaySharpeRatio(25, comp, data.OPEN)
plotDistribution(sharpeRatios, -7, 1)

sharpeRatios = []
for comp in stockHistory.compNames() :
    sharpeRatios += stockHistory.nDaySharpeRatio(100, comp, data.OPEN)
plotDistribution(sharpeRatios, -7, 1)
"""
print 'Done.'
