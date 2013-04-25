import json
import os
import math
from itertools import islice

DATE      = 'Date'
OPEN      = 'Open'
HIGH      = 'High'
LOW       = 'Low'
CLOSE     = 'Close'
VOLUME    = 'Volume' 
ADJ_CLOSE = 'Adj_Close'

AVAILABLE_STATS = {
DATE,
OPEN,
HIGH,
LOW,
CLOSE,
VOLUME,
ADJ_CLOSE
}

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
    def __init__(self, dirName) :
        self.path = os.path.dirname(os.path.realpath(__file__)) + '/../../../data/' + dirName
        files = [f for f in os.listdir(self.path) if 'json' in f]
        print 'Reading files in', dirName
        companyStockHistory = {}
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
            if compName not in companyStockHistory :
                companyStockHistory[compName] = {}
            companyStockHistory[compName][year] = quotes
        # compile data for multiple years in one company
        self.data = {}
        for comp in companyStockHistory :
            compYears = companyStockHistory[comp]
            compData = []
            for year in sorted(compYears.keys()) :
                compData += compYears[year]
            self.data[comp] = {}
            for stat in AVAILABLE_STATS :
                try :
                    self.data[comp][stat] = [float(quote[stat]) for quote in compData]
                except :
                    self.data[comp][stat] = [quote[stat] for quote in compData]
    
    def hasCompanyData(self, compName) :
        return compName in self.data
    
    def getData(self, compName, stat) :
        try :
            return self.data[compName][stat]
        except :
            return []
    
    def nDayAverage(self, n, compName, stat) :
        mapKey = stat + 'Avg' + str(n)
        try :
            return self.data[compName][mapKey]
        except :
            pass
        compData = self.getData(compName, stat)
        nAvg = [sum(i)/n for i in window(compData, n)]
        self.data[compName][mapKey] = nAvg
        return nAvg
    
    def nDaySlope(self, n, compName, stat) :
        mapKey = stat + 'Slope' + str(n)
        try :
            return self.data[compName][mapKey]
        except :
            pass
        compData = self.getData(compName, stat)
        nSlope = [(i[-1] - i[0])/n for i in window(compData, n)]
        self.data[compName][mapKey] = nSlope
        return nSlope
    
    def nDayStdDev(self, n, compName, stat) :
        mapKey = stat + 'StdDev' + str(n)
        try :
            return self.data[compName][mapKey]
        except :
            pass
        nAvg = self.nDayAverage(n, compName, stat)
        compData = self.getData(compName, stat)
        nStdDev = [math.sqrt(sum(x*x for x in i)/n - a*a) for (i, a) in zip(window(compData, n), nAvg)]
        self.data[compName][mapKey] = nStdDev
        return nStdDev
    
    @staticmethod
    def availableStats() :
        return AVAILABLE_STATS