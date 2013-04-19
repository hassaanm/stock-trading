import json
import os

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

class StockHistory :
    def __init__(self, dirName) :
        path = os.path.dirname(os.path.realpath(__file__)) + '/../data/' + dirName
        files = [f for f in os.listdir(path) if 'json' in f]
        print 'Reading files in', dirName
        companyStockHistory = {}
        for fName in files :
            f = open(path + '/' + fName, 'r')
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
                self.data[comp][stat] = [quote[stat] for quote in compData]
            
    def hasCompanyData(self, compName) :
        return compName in self.data
        
    def getData(self, compName, stat) :
        return self.data[compName][stat]
        
    @staticmethod
    def availableStats() :
        return AVAILABLE_STATS