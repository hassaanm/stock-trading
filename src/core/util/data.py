import json
import os
import pickle
from datetime import date, timedelta
from itertools import islice, chain

DATE      = 'Date'
OPEN      = 'Open'
HIGH      = 'High'
LOW       = 'Low'
CLOSE     = 'Close'
VOLUME    = 'Volume'
ADJ_CLOSE = 'Adj_Close'

AVAILABLE_STATS = [
DATE,
OPEN,
HIGH,
LOW,
CLOSE,
VOLUME,
ADJ_CLOSE
]

def window(seq, n=2):
    "Returns a sliding window (of width n) over data from the iterable"
    "   s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...                   "
    it = iter(i for i in seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result

class StockHistory :
    stats = AVAILABLE_STATS
    def __init__(self, dirName) :
        self.path = os.path.dirname(os.path.realpath(__file__)) + '/../../../data/' + dirName
        files = [f for f in os.listdir(self.path) if 'json' in f]
        print 'Reading files in', dirName
        self.data = {}
        self.startDate = date.today()
        self.endDate = date(1970, 1, 1)
        for fName in files :
            f = open(self.path + '/' + fName, 'r')
            try :
                quotes = json.loads(f.read())['query']['results']['quote']
            except :
                print 'No data:', fName
                continue
            quotes.reverse()
            if len(quotes) < 250 :
                print 'Incomplete data:', fName, len(quotes)
            parts = fName.split('.')
            compName = parts[0]
            year = parts[1]
            if compName not in self.data :
                self.data[compName] = {}
            for quote in quotes :
                for key in quote.keys() :
                    if key.lower() == 'date' :
                        ymd = [int(i) for i in quote[key].split('-')]
                        quoteDate = date(*ymd)
                        if quoteDate < self.startDate :
                            self.startDate = quoteDate
                        if quoteDate > self.endDate :
                            self.endDate = quoteDate
                        quote[key] = date(*ymd)
                    else :
                        quote[key] = float(quote[key])
                self.data[compName][quote['date']] = quote
        print 'Start date:', self.startDate
        print 'End date:', self.endDate

    def get(self, comp, date, stat) :
        return self.data[comp][date][stat]

    def getPrev(self, comp, date, stat) :
        return self.get(comp, self.getNDaysAgo(1, comp, date), stat)

    def compNames(self) :
        return self.data.keys()

    def hasDate(self, comp, date) :
        return date in self.data[comp]

    def getFirstDate(self, comp) :
        return sorted(self.data[comp].keys())[0]

    def getNDaysAgo(self, n, comp, date) :
        while n != 0 :
            date = date - timedelta(days=1)
            if self.hasDate(comp, date) :
                n -= 1
        return date

    def nDayAverage(self, n, comp, date, stat) :
        key = str(n) + 'avg' + stat
        if key in self.data[comp][date] :
            return self.data[comp][date][key]
        dates = [self.getNDaysAgo(i, comp, date) for i in range(1, n+1)]
        prices = [self.data[comp][d][stat] for d in dates]
        nAvg = sum(prices) / float(n)
        self.data[comp][date][key] = nAvg
        return nAvg

    def nDaySlope(self, n, comp, date, stat) :
        key = str(n) + 'slope' + stat
        if key in self.data[comp][date] :
            return self.data[comp][date][key]
        prevDate = self.getNDaysAgo(1, comp, date)
        startDate = self.getNDaysAgo(n, comp, date)
        nSlope = (self.data[comp][prevDate][stat] - self.data[comp][startDate][stat]) / float(n)
        self.data[comp][date][key] = nSlope
        return nSlope

    def getReturn(self, n, comp, date) :
        key = str(n) + 'return'
        if key in self.data[comp][date] :
            return self.data[comp][date][key]
        returnDate = self.getNDaysAgo(n, comp, date)
        o = self.data[comp][returnDate][OPEN]
        c = self.data[comp][returnDate][CLOSE]
        nReturn = (c-o)/o
        self.data[comp][date][key] = nReturn
        return nReturn

class Featurizer :
    def __init__(self, stockHistory, numDaysHistory=5, slopeN=5, averageN=5, returnPos=0.05, returnNeg=-0.05, slopePos=1.5, slopeNeg=-1.5, stats=None) :
        self.stockHistory = stockHistory
        self.numDaysHistory = numDaysHistory if numDaysHistory > 0 else 0
        self.slopeN = slopeN if slopeN > 0 else 0
        self.averageN = averageN if averageN > 0 else 0
        self.returnPos = returnPos
        self.returnNeg = returnNeg
        self.slopePos = slopePos
        self.slopeNeg = slopeNeg
        self.startDates = {}
        if stats == None :
            self.stats = [OPEN, CLOSE, VOLUME]
        else :
            self.stats = []
            for s in stats.lower() :
                if s == 'o' :
                    self.stats.append(OPEN)
                elif s == 'h' :
                    self.stats.append(HIGH)
                elif s == 'l' :
                    self.stats.append(LOW)
                elif s == 'c' :
                    self.stats.append(CLOSE)
                elif s == 'v' :
                    self.stats.append(VOLUME)
        self.defineFeatures()
        self.numFeatures = len(self.featureFunctions)

    def defineFeatures(self) :
        features = []
        # Add features for Monday thru Friday
        for i in range(5) :
            features.append((lambda x: lambda comp, date : date.weekday() == x)(i))
        # Add features for previous numDaysHistory days
        for i in range(1, self.numDaysHistory+1) :
            features.append((lambda x: lambda comp, date : self.stockHistory.getReturn(x, comp, date) > 0)(i))
            features.append((lambda x: lambda comp, date : self.stockHistory.getReturn(x, comp, date) < 0)(i))
            features.append((lambda x: lambda comp, date : self.stockHistory.getReturn(x, comp, date) > self.returnPos)(i))
            features.append((lambda x: lambda comp, date : self.stockHistory.getReturn(x, comp, date) < self.returnNeg)(i))

        for stat in self.stats :
            if self.averageN > 0:
                features.append((lambda x: lambda comp, date : self.stockHistory.getPrev(comp, date, x) > self.stockHistory.nDayAverage(self.averageN, comp, date, x))(stat))
                features.append((lambda x: lambda comp, date : self.stockHistory.getPrev(comp, date, x) < self.stockHistory.nDayAverage(self.averageN, comp, date, x))(stat))
            if self.slopeN > 0:
                features.append((lambda x: lambda comp, date : self.stockHistory.nDaySlope(self.slopeN, comp, date, x) > 0)(stat))
                features.append((lambda x: lambda comp, date : self.stockHistory.nDaySlope(self.slopeN, comp, date, x) < 0)(stat))
                features.append((lambda x: lambda comp, date : self.stockHistory.nDaySlope(self.slopeN, comp, date, x) > self.slopePos)(stat))
                features.append((lambda x: lambda comp, date : self.stockHistory.nDaySlope(self.slopeN, comp, date, x) < self.slopeNeg)(stat))

        if self.averageN > 0:
            features.append(lambda comp, date : self.stockHistory.getPrev(comp, date, VOLUME) > self.stockHistory.nDayAverage(self.averageN, comp, date, VOLUME) \
                and self.stockHistory.getPrev(comp, date, OPEN) > self.stockHistory.nDayAverage(self.averageN, comp, date, OPEN))
        
        self.featureFunctions = features

    def getFeatures(self, comp, date) :
        return [self.boolToInt(f(comp, date)) for f in self.featureFunctions]

    def getFirstDate(self, comp) :
        if comp in self.startDates :
            return self.startDates[comp]
        start = self.stockHistory.getFirstDate(comp)
        daysNeeded = max(self.numDaysHistory, self.slopeN, self.averageN)
        while daysNeeded != 0 :
            start = start + timedelta(days=1)
            if self.stockHistory.hasDate(comp, start) :
                daysNeeded -= 1
        self.startDates[comp] = start
        return start

    def isValidDate(self, comp, date) :
        start = self.getFirstDate(comp)
        return date >= start and self.stockHistory.hasDate(comp, date)

    def boolToInt(self, b) :
        return 1 if b else 0
