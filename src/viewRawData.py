#!/usr/local/bin/python

import sys
from core.util import data
from core.util.graphics import plot, plotDistribution

companiesToGraph = sys.argv[1:]
sh = data.StockHistory('nasdaq100')

if len(companiesToGraph) > 0 :
    print 'Generating graphs.'
for compName in companiesToGraph :
    compName = compName.upper()
    if not sh.hasComp(compName) :
        print 'No data for company', compName
        continue
    allDates = sh.getAllDates(compName)
    openYs = [sh.get(compName, date, data.OPEN) for date in allDates]
    highYs = [sh.get(compName, date, data.HIGH) for date in allDates]
    lowYs = [sh.get(compName, date, data.LOW) for date in allDates]
    closeYs = [sh.get(compName, date, data.CLOSE) for date in allDates]
    plot([openYs, highYs, lowYs, closeYs],
        labels=['Open', 'High', 'Low', 'Close'],
        title=compName,
        xlabel='Time',
        ylabel='Stock Price')

print 'Done.'
