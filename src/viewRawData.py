#!/usr/local/bin/python

import sys
from core.util import data
from core.util.graphics import plot

companiesToGraph = sys.argv[1:]
stockHistory = data.StockHistory('nasdaq100')

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

print 'Done.'
