#!/usr/local/bin/python

import json
import os
import sys
import matplotlib.pyplot as plt

DATE      = 'Date'
OPEN      = 'Open'
HIGH      = 'High'
LOW       = 'Low'
CLOSE     = 'Close'
VOLUME    = 'Volume' 
ADJ_CLOSE = 'Adj_Close'

companyStockHistory = {}

companiesToGraph = sys.argv[2:]
dir = sys.argv[1]
files = [f for f in os.listdir(dir) if 'json' in f]

print 'Reading files.'
for fName in files :
    f = open(dir + "/" + fName, 'r')
    try :
        quotes = json.loads(f.read())['query']['results']['quote']
    except :
        print 'No data:', fName
        continue
    quotes.reverse()
    """
    for quote in quotes :
        print DATE, ':', quote[DATE], ',',
        print OPEN, ':', quote[OPEN], ',',
        print HIGH, ':', quote[HIGH], ',',
        print LOW, ':', quote[LOW], ',',
        print CLOSE, ':', quote[CLOSE], ',',
        print VOLUME, ':', quote[VOLUME], ',',
        print ADJ_CLOSE, ':', quote[ADJ_CLOSE]
    """
    if len(quotes) < 250 :
        print 'Incomplete data:', fName, len(quotes)
    parts = fName.split('.')
    compName = parts[0]
    year = parts[1]
    if compName not in companyStockHistory :
        companyStockHistory[compName] = {}
    companyStockHistory[compName][year] = quotes        

print 'Compiling data.'
for comp in companyStockHistory :
    compYears = companyStockHistory[comp]
    companyStockHistory[comp] = []
    for year in sorted(compYears.keys()) :
        companyStockHistory[comp] += compYears[year]

if len(companiesToGraph) > 0 :
    print 'Generating graphs.'
for compName in companiesToGraph :
    compName = compName.upper()
    plt.xlabel('Time')
    plt.ylabel('Stock Price')
    plt.title(compName)
    ax = plt.subplot(111)
    try :
        quotes = companyStockHistory[compName]
    except :
        print 'No data for company', compName
        continue
    openYs = [quote[OPEN] for quote in quotes]
    highYs = [quote[HIGH] for quote in quotes]
    lowYs = [quote[LOW] for quote in quotes]
    closeYs = [quote[CLOSE] for quote in quotes]
    ax.plot(range(0, len(openYs)), openYs, label='Open')
    ax.plot(range(0, len(highYs)), highYs, label='High')
    ax.plot(range(0, len(lowYs)), lowYs, label='Low')
    ax.plot(range(0, len(closeYs)), closeYs, label='Close')
    ax.legend()
    plt.show()

print 'Done.'