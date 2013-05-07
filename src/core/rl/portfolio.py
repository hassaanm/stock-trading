import math
import numpy
import random
import sys
from datetime import timedelta

from core.util.data import StockHistory, Featurizer, OPEN


class Portfolio(object):

    def __init__(self, stockHistory=None, featurizer=None, testSize=0.2, pickNum=5, money=10000.0, verbose = False):
        if stockHistory == None :
            self.stockHistory = StockHistory('nasdaq100')
        else :
            self.stockHistory = stockHistory
        self.companies = self.stockHistory.compNames()
        if featurizer == None :
            self.featurizer = Featurizer(self.stockHistory)
        else :
            self.featurizer = featurizer
        self.numberOfFeatures = self.featurizer.numFeatures

        self.A = dict()
        self.b = dict()
        self.alpha = 0.1
        self.tradeCost = 0.01
        self.testPercentage = float(testSize)
        self.numToPick = int(pickNum)
        self.startMoney = float(money)
        self.verbose = int(verbose)

    # compound annual growth rate
    def CAGR(self, endMoney, years):
        totalReturn = endMoney / float(self.startMoney)
        CAGR = totalReturn ** (1 / float(years))
        return ((CAGR - 1) * 100)

    def updateMoney(self, money, stockReturn, cost):
        profit = money * stockReturn
        money = money + profit - cost if money > 0 else 0
        return money

    def getTradeCost(self, money, stocks, openPrices):
        perStockMoney = money / self.numToPick
        cost = 0
        for stock in stocks:
            price = openPrices[stock]
            cost += ((perStockMoney / price) * self.tradeCost * 2)
        return cost

    def printData(self, startDate, testStartDate, endDate, realMoney, randomMoney, avgMoney):
        years = (endDate - testStartDate).days / 365.25
        realCAGR = self.CAGR(realMoney, years)
        print 'Training days:', (testStartDate - startDate).days, 'Testing days:', (endDate - testStartDate).days, 'Total days:', (endDate - startDate).days
        print ('%-14s %14f %2.2f') % ('Real Money:', realMoney, realCAGR)
        print ('%-14s %14f %2.2f') % ('Random Money:', randomMoney, self.CAGR(randomMoney, years))
        print ('%-14s %14f %2.2f') % ('Average Money:', avgMoney, self.CAGR(avgMoney, years))
        return realCAGR

    def run(self):
        startDate = self.stockHistory.startDate
        endDate = self.stockHistory.endDate
        date = startDate
        # real, random and average money
        money = [self.startMoney, self.startMoney, self.startMoney]
        testStartDate = timedelta(days=int((endDate - date).days * (1 - self.testPercentage))) + date
        while date < endDate :
            sys.stdout.write("\r%s" %str(date))
            sys.stdout.flush()
            companies = [company for company in self.companies if self.featurizer.isValidDate(company, date)]
            features = [self.featurizer.getFeatures(company, date) for company in companies]
            returns = [self.stockHistory.getReturn(0, company, date) for company in companies]
            if len(companies) > 0 :
                stocks, moneyReturns, sharpeRatio = self.LinUCB(companies, features, returns)
                if self.verbose:
                    print ('%10f\t%8.5f\t%8.5f\t%8.5f\t%8.5f\t%s') % (money[0], moneyReturns[0], moneyReturns[1], moneyReturns[2], sharpeRatio, stocks)
                if date > testStartDate:
                    openPrices = {company: self.stockHistory.get(company, date, OPEN) for company in stocks}
                    cost = self.getTradeCost(money[0], stocks, openPrices)
                    money = [self.updateMoney(m, r, cost) for (m, r) in zip(money, moneyReturns)]
            date = date + timedelta(days=1)
        cagr = self.printData(startDate, testStartDate, endDate, *money)
        return cagr

    def LinUCB(self, stocks, features, rewards):
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
        stockIndeces = sortedStocks[:self.numToPick]

        stockReturn = 0
        sharpeRatio = 0
        randomReturn = sum(random.sample(rewards, self.numToPick))

        for index in stockIndeces:
            chosen.append((stocks[index], features[index], rewards[index]))
            stockReturn += rewards[index]

        avgStockReturn = stockReturn / float(self.numToPick)
        
        for stock, feature, reward in chosen:
            sharpeRatio += (reward - avgStockReturn)**2

        sharpeRatio = (sharpeRatio / float(self.numToPick))**0.5
        sharpeRatio = avgStockReturn / sharpeRatio if sharpeRatio != 0 else 0

        # sharpe ratio reward
        #for stock, feature, reward in chosen:
        #    x = numpy.array(feature)
        #    self.A[stock] += numpy.dot(x, x.T)
        #    self.b[stock] += sharpeRatio * x.T

        avgReturn = sum(rewards) / len(rewards)
        rewards.sort()

        chosenStocks, chosenFeatures, chosenRewards = zip(*chosen)
        return chosenStocks, ((stockReturn/self.numToPick), (randomReturn/self.numToPick), avgReturn), sharpeRatio

def runPortfolio(stockHistory=None, featurizer=None, *args):
    portfolio = Portfolio(stockHistory, featurizer, *args)
    portfolio.run()
