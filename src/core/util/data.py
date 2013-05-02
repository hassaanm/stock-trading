import json
import os
import math
from datetime import date
from itertools import islice, chain

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
    stats = AVAILABLE_STATS
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
        except KeyError:
            return []
            
    def getAveragePrices(self, compName) :
        mapKey = 'avgPrice'
        try :
            return self.data[compName][mapKey]
        except KeyError:
            pass
        highs = self.getData(compName, HIGH)
        lows = self.getData(compName, LOW)
        avgPrices = [(h+l)/2. for (h,l) in zip(highs, lows)]
        self.data[compName][mapKey] = avgPrices
        return avgPrices
            
    def getDates(self, compName) :
        mapKey = 'dates'
        try :
            return self.data[compName][mapKey]
        except KeyError:
            pass
        data = self.getData(compName, DATE)
        dates = []
        for d in data :
            ymd = [int(i) for i in d.split('-')]
            dates.append(date(*ymd))
        self.data[compName][mapKey] = dates
        return dates
    
    def compNames(self) :
        return self.data.keys()
    
    def nDayAverage(self, n, compName, stat) :
        mapKey = stat + 'Avg' + str(n)
        try :
            return self.data[compName][mapKey]
        except KeyError:
            pass
        compData = self.getData(compName, stat)
        nAvg = [sum(i)/n for i in window(compData, n)]
        self.data[compName][mapKey] = nAvg
        return nAvg
    
    def nDaySlope(self, n, compName, stat) :
        mapKey = stat + 'Slope' + str(n)
        try :
            return self.data[compName][mapKey]
        except KeyError:
            pass
        compData = self.getData(compName, stat)
        nSlope = [(i[-1] - i[0])/n for i in window(compData, n)]
        self.data[compName][mapKey] = nSlope
        return nSlope
    
    def nDayStdDev(self, n, compName, stat) :
        mapKey = stat + 'StdDev' + str(n)
        try :
            return self.data[compName][mapKey]
        except KeyError:
            pass
        nAvg = self.nDayAverage(n, compName, stat)
        compData = self.getData(compName, stat)
        nStdDev = [math.sqrt(sum(x*x for x in i)/n - a*a) for (i, a) in zip(window(compData, n), nAvg)]
        self.data[compName][mapKey] = nStdDev
        return nStdDev

class Featurizer :
    outFeatures = 2
    baseFeatures = 5
    statFeatures = 2
    def __init__(self, stockHistory, *args) :
        self.parseArgs(args)
        self.numFeatures = Featurizer.baseFeatures + len(self.statsToUse) * Featurizer.statFeatures
        self.numTargetFeatures = Featurizer.outFeatures
        self.stockHistory = stockHistory
        
    def setCompany(self, company) :
        self.dates = self.stockHistory.getDates(company)[100:]
        self.numExamples = len(self.dates) - 1
        self.averages = self.stockHistory.getAveragePrices(company)[100:]
        self.slopeFeatures = list(chain.from_iterable((
                                self.stockHistory.nDaySlope(10, company, stat)[90:],
                                self.stockHistory.nDaySlope(100, company, stat)
                              ) for stat in self.statsToUse))
    
    def features(self, pos) :
        example = TrainingExample()
        # Add features for Monday thru Friday
        date = self.dates[pos].weekday()
        for i in range(5) :
            if i == date :
                example.addFeature(1)
            else :
                example.addFeature(0)
        for sFeature in self.slopeFeatures :
            example.addFeature(sFeature[pos] > 1)
        example.addOutput(self.averages[pos] > self.averages[pos+1])
        example.addOutput(self.averages[pos] < self.averages[pos+1])
        return example
    
    def parseArgs(self, args) :
        self.statsToUse = []
        for i in range(len(args)) :
            arg = args[i]
            if i == 0 :
                for char in arg.lower() :
                    if char == 'o' :
                        self.statsToUse.append(OPEN)
                    elif char == 'h' :
                        self.statsToUse.append(HIGH)
                    elif char == 'l' :
                        self.statsToUse.append(LOW)
                    elif char == 'c' :
                        self.statsToUse.append(CLOSE)
                    elif char == 'v' :
                        self.statsToUse.append(VOLUME)
            if i == 1 :
                break # no more args
        if len(args) == 0 :
            self.statsToUse = [OPEN, HIGH, LOW, CLOSE, VOLUME]
        print 'Using stats:', self.statsToUse

class TrainingSet :
    def __init__(self, featurizer, company) :
        self.pos = 0
        featurizer.setCompany(company)
        self.numExamples = featurizer.numExamples
        self.featurizer = featurizer
    
    def __iter__(self) :
        return self
        
    def next(self) :
        if self.pos >= self.numExamples:
            raise StopIteration
        example = self.featurizer.features(self.pos)
        self.pos += 1
        return example
        
class TrainingExample :
    def __init__(self) :
        self.features = []
        self.output = []
        
    def addFeature(self, f) :
        self.features.append(self.boolToInt(f))
        
    def addOutput(self, o) :
        self.output.append(self.boolToInt(o))
        
    def boolToInt(self, b) :
        return 1 if b else 0