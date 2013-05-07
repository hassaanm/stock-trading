import json
import os
import pickle
from datetime import date
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
        
    def getReturns(self, compName) :
        mapKey = 'returns'
        try :
            return self.data[compName][mapKey]
        except KeyError:
            pass
        close = self.getData(compName, CLOSE)
        open = self.getData(compName, OPEN)
        returns = [(c-o)/o for (c,o) in zip(close,open)]
        self.data[compName][mapKey] = returns
        return returns
    
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
        nStdDev = [sum(((x-a)**2)/n for x in w)**.5 for (w, a) in zip(window(compData, n), nAvg)]
        self.data[compName][mapKey] = nStdDev
        return nStdDev
        
    def nDaySharpeRatio(self, n, compName, stat) :
        mapKey = stat + 'Sharpe' + str(n)
        try :
            return self.data[compName][mapKey]
        except KeyError:
            pass
        nAvg = self.nDayAverage(n, compName, stat)
        nStdDev = self.nDayStdDev(n, compName, stat)
        nSharpe = [(a/s if s != 0 else 0) for (a,s) in zip(nAvg, nStdDev)]
        self.data[compName][mapKey] = nSharpe
        return nSharpe

class Featurizer :

    outFeatures = 2
    statFeatures = 11
    numDaysOfHistory = 5
    baseFeatures = 5 + numDaysOfHistory
    
    def __init__(self, stockHistory, company, *args) :
        self.net = None
        self.parseArgs(args)
        self.stockHistory = stockHistory
        self.cut = max(self.N, Featurizer.numDaysOfHistory)
        self.returnCut = self.cut - Featurizer.numDaysOfHistory
        self.nDayCut = 0 if self.returnCut > 0 else (Featurizer.numDaysOfHistory-self.N)
        
        self.dates = stockHistory.getDates(company)[self.cut:]
        self.average = stockHistory.getAveragePrices(company)[self.cut:]
        self.volume = stockHistory.getData(company, VOLUME)[self.cut:]
        self.open = stockHistory.getData(company, OPEN)[self.cut:]
        self.close = stockHistory.getData(company, CLOSE)[self.cut:]

        self.returns = stockHistory.getReturns(company)[self.returnCut:]

        self.nDaySlope = stockHistory.nDaySlope(self.N, company, OPEN)[self.nDayCut:]
        self.nDayVolume = stockHistory.nDayAverage(self.N, company, VOLUME)[self.nDayCut:]
        self.nDayOpenAverage = stockHistory.nDayAverage(self.N, company, OPEN)[self.nDayCut:]
        self.nDayCloseAverage = stockHistory.nDayAverage(self.N, company, CLOSE)[self.nDayCut:]

        self.defineFeatures()
        self.numExamples = len(self.dates) - 1
        self.numFeatures = len(self.featureFunctions)
        self.numTargetFeatures = Featurizer.outFeatures

    def loadNN(self, fname) :
        f = open(fname, 'r')
        self.net = pickle.load(f)
        self.numFeatures += 2
    
    def defineFeatures(self) :
        features = []
        # Add features for Monday thru Friday
        for i in range(5) :
            features.append((lambda x: lambda pos : self.dates[pos].weekday() == x)(i))
        # Add features for previous numDaysOfHistory days
        #for i in range(Featurizer.numDaysOfHistory) :
        #    features.append((lambda x: lambda pos : self.returns[pos] > 0.025)(i))

        features.append(lambda pos : self.nDaySlope[pos] > 0)
        features.append(lambda pos : self.nDaySlope[pos] < 0)
        features.append(lambda pos : self.nDaySlope[pos] > self.slopePos)
        features.append(lambda pos : self.nDaySlope[pos] < self.slopeNeg)

        # figure out good values for these
        features.append(lambda pos : self.open[pos] > self.nDayOpenAverage[pos])
        features.append(lambda pos : self.open[pos] < self.nDayOpenAverage[pos])

        # figure out good values for these
        features.append(lambda pos : self.close[pos] > self.nDayCloseAverage[pos])
        features.append(lambda pos : self.close[pos] < self.nDayCloseAverage[pos])

        # figure out good values for these
        features.append(lambda pos : self.volume[pos] > self.nDayVolume[pos])
        features.append(lambda pos : self.volume[pos] < self.nDayVolume[pos])

        features.append(lambda pos : self.volume[pos] > self.nDayVolume[pos] and self.nDaySlope[pos] > self.slopePos)
        self.featureFunctions = features
    
    def features(self, pos) :
        example = TrainingExample()
        for feature in self.featureFunctions :
            example.addFeature(feature(pos))

        # Neural net output features
        if self.net != None :
            netOutput = [int(round(x)) for x in list(self.net.activate(example.features))]
            for netOut in netOutput :
                example.addFeature(netOut)
        example.addOutput(self.average[pos] > self.average[pos+1])
        example.addOutput(self.average[pos] < self.average[pos+1])
        return example
    
    def parseArgs(self, args) :
        self.stat = OPEN
        self.N = 5
        self.slopePos = 1.5
        self.slopeNeg = -self.slopePos
        for i in range(len(args)) :
            arg = args[i]
            if i == 0 :
                self.N = int(arg)
            if i == 1 :
                self.slopePos = float(arg)
            if i == 2 :
                self.slopeNeg = float(arg)
            if i == 3 :
                s = arg.lower()
                if s == 'o' :
                    self.stat = OPEN
                elif s == 'h' :
                    self.stat = HIGH
                elif s == 'l' :
                    self.stat = LOW
                elif s == 'c' :
                    self.stat = CLOSE
            if i == 4 :
                break # no more args
        """
        print 'N:', self.N
        print 'slopePos:', self.slopePos
        print 'slopeNeg:', self.slopeNeg
        print 'Using stats:', self.stat
        """

class TrainingSet :
    def __init__(self, stockHistory, company) :
        self.pos = 0
        self.company = company
        self.featurizer = Featurizer(stockHistory, company)
        self.numExamples = self.featurizer.numExamples
    
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
