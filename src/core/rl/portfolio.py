import math
import numpy
import random

from core.util.data import StockHistory, TrainingSet, Featurizer

class Portfolio(object):

    def __init__(self, pickNum, testSize, money, verbose = False):
        self.stockHistory = StockHistory('nasdaq100')
        self.companies = self.stockHistory.compNames()
        self.featurizer = Featurizer(self.stockHistory)

        self.A = dict()
        self.b = dict()
        self.alpha = 1
        self.stockCost = 0
        self.numToPick = pickNum
        self.testPercentage = testSize
        self.startMoney = money
        self.verbose = verbose
        self.numberOfFeatures = self.featurizer.numFeatures

    def CAGR(self, endMoney, years):
        totalReturn = endMoney / float(self.startMoney)
        CAGR = totalReturn ** (1 / float(years))
        return ((CAGR - 1) * 100)

    def updateMoney(self, money, stockReturn):
        cost = self.stockCost * 2 * self.numToPick
        money = money + money * stockReturn - cost if money > 0 else 0
        return money

    def printData(self, trainSet, totalSet, realMoney, randomMoney, avgMoney, bestMoney):
        years = (totalSet - trainSet) / 250.8
        print 'Training days:', trainSet, 'Testing days:', (totalSet - trainSet), 'Total days:', totalSet
        print ('%-14s %14f %2.2f') % ('Real Money:', realMoney, self.CAGR(realMoney, years))
        print ('%-14s %14f %2.2f') % ('Random Money:', randomMoney, self.CAGR(randomMoney, years))
        print ('%-14s %14f %2.2f') % ('Average Money:', avgMoney, self.CAGR(avgMoney, years))
        print ('%-14s %14f %2.2f') % ('Best Money:', bestMoney, self.CAGR(bestMoney, years))

    def run(self):
        # get data
        trainingSets = {}
        returns = {}
        for company in self.companies:
            trainingSets[company] = TrainingSet(self.featurizer, company)
            returns[company] = iter(self.stockHistory.getReturns(company)[self.featurizer.cut:])
        testStart = 0
        for trainingExample in TrainingSet(self.featurizer, self.companies[0]):
            testStart += 1
        testStart = int(testStart * (1 - self.testPercentage))

        # run LinUCB
        flag = True
        count = 0
        realMoney = self.startMoney
        randomMoney = self.startMoney
        avgMoney = self.startMoney
        bestMoney = self.startMoney
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
                if self.verbose:
                    print stockReturn, randomReturn, avgReturn, bestReturn, sharpeRatio, stocks
                count += 1
                if count > testStart:
                    realMoney = self.updateMoney(realMoney, stockReturn)
                    randomMoney = self.updateMoney(randomMoney, randomReturn)
                    avgMoney = self.updateMoney(avgMoney, avgReturn)
                    bestMoney = self.updateMoney(bestMoney, bestReturn)
        self.printData(testStart, count, realMoney, randomMoney, avgMoney, bestMoney)

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
        sharpeRatio = avgReturn / sharpeRatio

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

def runPortfolio(numOfStocks, testPercentage, money, verbose):
    portfolio = Portfolio(numOfStocks, testPercentage, money, verbose)
    portfolio.run()
