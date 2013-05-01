import math
import numpy

class Portfolio(object):

    def __init__(self):
        self.A = dict()
        self.b = dict()
        self.alpha = 1
        self.numberOfFeatures = 10

    # TODO: return feature vector for stock on date
    def getFeatures(self, stockSymbol, date):
        return numpy.zeros(self.numberOfFeatures)

    # TODO: return reward for stock on date (either pure profit, index, Sharpe ratio, etc.)
    def getReward(self, stockSymbol, date):
        return 0

    def LinUCB(self, stocks, date, numberOfStocksToPick):
        p = []

        for stock in stocks:
            if stock not in self.A:
                self.A[stock] = numpy.identity(self.numberOfFeatures)
                self.b[stock] = numpy.zeros(self.numberOfFeatures)
            theta = numpy.dot(numpy.linalg.inv(self.A[stock]), self.b[image])
            x = self.getFeatures(stock, date)
            p.append(float(numpy.dot(theta.T, x) + self.alpha * math.sqrt(numpy.dot(numpy.dot(x.T, numpy.linalg.inv(self.A[stock])), x))))

        chosenStocks = []
        sortedStocks = numpy.argsort(p)[::-1]
        stockIndeces = sortedStocks[:numberOfStocksToPick]

        for index in stockIndeces:
            chosenStocks.append(stocks[index])
        
        for stock in chosenStocks:
            x = self.getFeatures(stock, date)
            self.A[stock] += numpy.dot(x, x.T)
            self.b[stock] += self.getReward(stock, date) * x.T

        return chosenStocks
