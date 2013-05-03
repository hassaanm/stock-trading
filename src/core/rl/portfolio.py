import math
import numpy
import random

from core.util.data import StockHistory, TrainingSet, Featurizer

class Portfolio(object):

    def __init__(self, pickNum):
        self.stockHistory = StockHistory('nasdaq100')
        self.companies = self.stockHistory.compNames()
        self.featurizer = Featurizer(self.stockHistory)

        self.A = dict()
        self.b = dict()
        self.alpha = 1
        self.numToPick = pickNum
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
        avgMoney = 10000
        bestMoney = 10000
        # loop until out of training data
        while flag:
            # get features and rewards
            features = []
            rewards = []
            companies = trainingSets.keys()
            for company in companies:
                try:
                    features.append(trainingSets[company].next().features)
                    rewards.append(returns[company].next())
                except:
                    del trainingSets[company]
                    del returns[company]
            flag = len(trainingSets.keys()) != 0
            # call LinUCB
            if flag:
                stocks, stockReturn, randomReturn, avgReturn, bestReturn, sharpeRatio = self.LinUCB(self.companies, features, rewards, self.numToPick)
                print stockReturn, randomReturn, avgReturn, bestReturn, sharpeRatio, stocks
                count += 1
                if count > 1000:
                    realMoney = realMoney + realMoney * stockReturn if realMoney > 0 else 0
                    randomMoney = randomMoney + randomMoney * randomReturn if randomMoney > 0 else 0
                    avgMoney = avgMoney + avgMoney * avgReturn if avgMoney > 0 else 0
                    bestMoney = bestMoney + bestMoney * bestReturn if bestMoney > 0 else 0
        print ('%-14s %14.2f') % ('Real Money:', realMoney)
        print ('%-14s %14.2f') % ('Random Money:', randomMoney)
        print ('%-14s %14.2f') % ('Average Money:', avgMoney)
        print ('%-14s %14.2f') % ('Best Money:', bestMoney)

    def LinUCB(self, stocks, features, rewards, numberOfStocksToPick):
        p = []

        for stock, feature, reward in zip(stocks, features, rewards):
            if stock not in self.A:
                self.A[stock] = numpy.identity(self.numberOfFeatures)
                self.b[stock] = numpy.zeros(self.numberOfFeatures)
            theta = numpy.dot(numpy.linalg.inv(self.A[stock]), self.b[stock])
            x = numpy.array(feature)
            p.append(float(numpy.dot(theta.T, x) + self.alpha * math.sqrt(numpy.dot(numpy.dot(x.T, numpy.linalg.inv(self.A[stock])), x))))
            self.A[stock] += numpy.dot(x, x.T)
            self.b[stock] += reward * x.T

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
            sharpeRatio += (reward - avgReturn)**2

        sharpeRatio = (sharpeRatio / float(numberOfStocksToPick))**0.5

        # sharpe ratio reward
        #for stock, feature, reward in chosen:
        #    x = numpy.array(feature)
        #    self.A[stock] += numpy.dot(x, x.T)
        #    self.b[stock] += sharpeRatio * x.T

        avgReturn = sum(rewards) / len(rewards)
        rewards.sort()
        bestReturn = sum(rewards[::-1][:numberOfStocksToPick])

        chosenStocks, chosenFeatures, chosenRewards = zip(*chosen)
        return chosenStocks, (stockReturn/numberOfStocksToPick), (randomReturn/numberOfStocksToPick), avgReturn, (bestReturn/numberOfStocksToPick), sharpeRatio

def runPortfolio():
    portfolio = Portfolio(5)
    portfolio.run()
