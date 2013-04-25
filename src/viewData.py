#!/usr/local/bin/python

import sys
from core.util.data import StockHistory
from core.util.graphics import plot

companyToGraph = sys.argv[1]
statToGraph = sys.argv[2]

print 'Generating graph.'

stockHistory = StockHistory('nasdaq100')
avg100 = stockHistory.nDayAverage(100, companyToGraph, statToGraph)
slope100 = stockHistory.nDaySlope(100, companyToGraph, statToGraph)
stddev100 = stockHistory.nDayStdDev(100, companyToGraph, statToGraph)

avg10 = stockHistory.nDayAverage(10, companyToGraph, statToGraph)
slope10 = stockHistory.nDaySlope(10, companyToGraph, statToGraph)
stddev10 = stockHistory.nDayStdDev(10, companyToGraph, statToGraph)

print '\n'.join(str(i) for i in zip(stockHistory.getData(companyToGraph, statToGraph)[100:], avg100, stddev100, slope100, avg10, slope10, stddev10))

print 'Generating graphs'

plot([avg100, stockHistory.getData(companyToGraph, statToGraph)], yerrs=[stddev100, None])
plot([avg10, stockHistory.getData(companyToGraph, statToGraph)], yerrs=[stddev10, None])
plot([slope100, slope10])

print 'Done.'
