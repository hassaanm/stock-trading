import math
import numpy
import random

from core.util.data import StockHistory, TrainingSet, Featurizer

class Portfolio(object):

    def __init__(self):
        self.stockHistory = StockHistory('nasdaq100')
        self.companies = self.stockHistory.compNames()
        self.featurizer = Featurizer(self.stockHistory)

        self.A = dict()
        self.b = dict()
        self.alpha = 1
        self.numberOfFeatures = self.featurizer.numFeatures

    def run(self):
        # get data
        trainingSets = {}
        returns = {}
        for company in self.companies:
            trainingSets[company] = TrainingSet(self.featurizer, company)
            returns[company] = iter(self.stockHistory.getReturns(company)[self.featurizer.cut:])

        # run LinUCB
        flag = True
        count = 0
        realMoney = 10000
        randomMoney = 10000
        # loop until out of training data
        while flag:
            # get features and rewards
            features = []
            rewards = []
            for company in self.companies:
                try:
                    features.append(trainingSets[company].next().features)
                    rewards.append(returns[company].next())
                except:
                    flag = False
            # call LinUCB
            stocks, stockReturn, randomReturn, sharpeRatio = self.LinUCB(self.companies, features, rewards, 10)
            print stockReturn, randomReturn, sharpeRatio, stocks
            count += 1
            if count > 120:
                realMoney += realMoney * stockReturn
                randomMoney += randomMoney * randomReturn
        print count, realMoney, randomMoney

    def LinUCB(self, stocks, features, rewards, numberOfStocksToPick):
        p = []

        for stock, feature in zip(stocks, features):
            if stock not in self.A:
                self.A[stock] = numpy.identity(self.numberOfFeatures)
                self.b[stock] = numpy.zeros(self.numberOfFeatures)
            theta = numpy.dot(numpy.linalg.inv(self.A[stock]), self.b[stock])
            x = numpy.array(feature)
            p.append(float(numpy.dot(theta.T, x) + self.alpha * math.sqrt(numpy.dot(numpy.dot(x.T, numpy.linalg.inv(self.A[stock])), x))))

        chosen = []
        sortedStocks = numpy.argsort(p)[::-1]
        stockIndeces = sortedStocks[:numberOfStocksToPick]

        stockReturn = 0
        sharpeRatio = 0
        randomReturn = sum(random.sample(rewards, numberOfStocksToPick))

        for index in stockIndeces:
            chosen.append((stocks[index], features[index], rewards[index]))
            stockReturn += rewards[index]

        avgReturn = stockReturn / float(numberOfStocksToPick)
        
        for stock, feature, reward in chosen:
            x = numpy.array(feature)
            self.A[stock] += numpy.dot(x, x.T)
            self.b[stock] += reward * x.T
            sharpeRatio += (reward - avgReturn)**2

        sharpeRatio = (sharpeRatio / float(numberOfStocksToPick))**0.5

        chosenStocks, chosenFeaturs, chosenRewards = zip(*chosen)

        return chosenStocks, stockReturn, randomReturn, sharpeRatio

def runPortfolio():
    portfolio = Portfolio()
    portfolio.run()
