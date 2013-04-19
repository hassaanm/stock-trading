#!/usr/local/bin/python

import json
import os
import sys
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src')
import data

companiesToGraph = sys.argv[1:]
stockHistory = data.StockHistory('nasdaq100')

if len(companiesToGraph) > 0 :
    print 'Generating graphs.'
for compName in companiesToGraph :
    compName = compName.upper()
    plt.xlabel('Time')
    plt.ylabel('Stock Price')
    plt.title(compName)
    ax = plt.subplot(111)
    if not stockHistory.hasCompanyData(compName) :
        print 'No data for company', compName
        continue
    openYs = stockHistory.getData(compName, data.OPEN)
    highYs = stockHistory.getData(compName, data.HIGH)
    lowYs = stockHistory.getData(compName, data.LOW)
    closeYs = stockHistory.getData(compName, data.CLOSE)
    ax.plot(range(len(openYs)), openYs, label='Open')
    ax.plot(range(len(highYs)), highYs, label='High')
    ax.plot(range(len(lowYs)), lowYs, label='Low')
    ax.plot(range(len(closeYs)), closeYs, label='Close')
    ax.legend()
    plt.show()

print 'Done.'