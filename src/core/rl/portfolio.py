import math
import numpy
import random

from core.util.data import StockHistory, TrainingSet, Featurizer

class Portfolio(object):

    def __init__(self, pickNum, testSize, money):
        self.stockHistory = StockHistory('nasdaq100')
        self.companies = self.stockHistory.compNames()
        self.featurizer = Featurizer(self.stockHistory)

        self.A = dict()
        self.b = dict()
        self.alpha = 1
        self.numToPick = pickNum
        self.testPercentage = testSize
        self.startMoney = money
        self.numberOfFeatures = self.featurizer.numFeatures

    def CAGR(self, endMoney, years):
        totalReturn = endMoney / float(self.startMoney)
        CAGR = totalReturn ** (1 / float(years))
        return ((CAGR - 1) * 100)

    def run(self):
        # get data
        trainingSets = {}
        returns = {}
        for company in self.companies:
            trainingSets[company] = TrainingSet(self.featurizer, company)
            returns[company] = iter(self.stockHistory.getReturns(company)[self.featurizer.cut:])
        testSet = 0
        for trainingExample in TrainingSet(self.featurizer, self.companies[0]):
            testSet += 1
        testSet = int(testSet * (1 - self.testPercentage))

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
                print stockReturn, randomReturn, avgReturn, bestReturn, sharpeRatio, stocks
                count += 1
                if count > testSet:
                    realMoney = realMoney + realMoney * stockReturn if realMoney > 0 else 0
                    randomMoney = randomMoney + randomMoney * randomReturn if randomMoney > 0 else 0
                    avgMoney = avgMoney + avgMoney * avgReturn if avgMoney > 0 else 0
                    bestMoney = bestMoney + bestMoney * bestReturn if bestMoney > 0 else 0

        print 'Training days:', testSet, 'Testing days:', (count - testSet), 'Total days:', count
        print ('%-14s %14f %2.2f') % ('Real Money:', realMoney, self.CAGR(realMoney, (count - testSet) / 250.8))
        print ('%-14s %14f %2.2f') % ('Random Money:', randomMoney, self.CAGR(randomMoney, (count - testSet) / 250.8))
        print ('%-14s %14f %2.2f') % ('Average Money:', avgMoney, self.CAGR(avgMoney, (count - testSet) / 250.8))
        print ('%-14s %14f %2.2f') % ('Best Money:', bestMoney, self.CAGR(bestMoney, (count - testSet) / 250.8))

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

def runPortfolio(numOfStocks, testPercentage, money):
    portfolio = Portfolio(numOfStocks, testPercentage, money)
    portfolio.run()
