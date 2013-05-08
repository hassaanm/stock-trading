import math
import numpy
import random
import sys
from datetime import timedelta

from core.util.data import StockHistory, Featurizer, OPEN


class Portfolio(object):

    def __init__(self, stockHistory=None, featurizer=None, testSize=0.2, pickNum=5, money=10000.0, verbose=False, graph=False):
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
        self.graph = int(graph)

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

    def printData(self, startDate, testStartDate, endDate, linUCBMoney, randomMoney, yesterdayMoney, avgMoney):
        years = (endDate - testStartDate).days / 365.25
        linUCBCAGR = self.CAGR(linUCBMoney, years)
        print 'Training days:', (testStartDate - startDate).days, 'Testing days:', (endDate - testStartDate).days, 'Total days:', (endDate - startDate).days
        print ('%-14s %14f %2.2f') % ('Real Money:', linUCBMoney, linUCBMoney)
        print ('%-14s %14f %2.2f') % ('Random Money:', randomMoney, self.CAGR(randomMoney, years))
        print ('%-14s %14f %2.2f') % ('Yesterday Money:', yesterdayMoney, self.CAGR(yesterdayMoney, years))
        print ('%-14s %14f %2.2f') % ('Average Money:', avgMoney, self.CAGR(avgMoney, years))
        return linUCBCAGR

    def run(self):
        startDate = self.stockHistory.startDate
        endDate = self.stockHistory.endDate
        date = startDate
        # linUCB, random, yesterday's best and average money
        money = [self.startMoney, self.startMoney, self.startMoney, self.startMoney]
        testStartDate = timedelta(days=int((endDate - date).days * (1 - self.testPercentage))) + date
        returns = []
        while date < endDate :
            sys.stdout.write("\r%s" %str(date))
            sys.stdout.flush()
            companies = [company for company in self.companies if self.featurizer.isValidDate(company, date)]
            features = [self.featurizer.getFeatures(company, date) for company in companies]
            prevReturns = returns
            returns = [self.stockHistory.getReturn(0, company, date) for company in companies]
            if len(companies) > 0 :
                linUCBStocks, linUCBReturn, linUCBSharpeRatio = self.LinUCB(companies, features, returns)
                randomStocks, randomReturn, randomSharpeRatio = self.randomSelection(companies, returns)
                yesterdayBestStocks, yesterdayBestReturn, yesterdayBestSharpeRatio = self.yesterdayBestSelection(companies, returns, prevReturns)
                averageReturn = self.averageSelection(returns)
                moneyReturns = [linUCBReturn, randomReturn, yesterdayBestReturn, averageReturn]
                stocksChosen = [linUCBStocks, randomStocks, yesterdayBestStocks, randomStocks]
                if date > testStartDate:
                    openPrices = {company: self.stockHistory.get(company, date, OPEN) for company in companies}
                    costs = [self.getTradeCost(m, s, openPrices) for (m, s) in zip(money, stocksChosen)]
                    money = [self.updateMoney(m, r, c) for (m, r, c) in zip(money, moneyReturns, costs)]
                if self.verbose:
                    print ('%10f\t%8.5f\t%8.5f\t%8.5f\t%8.5f\t%s') % (money[0], linUCBReturn, randomReturn, yesterdayBestReturn, averageReturn, stocks)
            date = date + timedelta(days=1)
        cagr = self.printData(startDate, testStartDate, endDate, *money)
        return cagr

    def sharpeRatio(self, avgReturn, rewards) :
        diffSquaredSum = sum([(r - avgReturn)**2 for r in rewards])
        stddev = (diffSquaredSum / float(self.numToPick))**0.5
        sharpeRatio = avgReturn / stddev if stddev != 0 else 0
        return sharpeRatio
    
    def randomSelection(self, stocks, rewards) :
        selections = random.sample(zip(stocks, rewards), self.numToPick)
        chosenStocks = [sel[0] for sel in selections]
        chosenRewards = [sel[1] for sel in selections]
        avgStockReturn = sum(chosenRewards) / float(self.numToPick)
        sharpeRatio = self.sharpeRatio(avgStockReturn, chosenRewards)
        return chosenStocks, avgStockReturn, sharpeRatio

    def averageSelection(self, rewards) :
        return sum(rewards) / len(rewards)

    def yesterdayBestSelection(self, stocks, rewards, yesterdayRewards) :
        selections = sorted(zip(yesterdayRewards, stocks, rewards))[-self.numToPick:]
        chosenStocks = [sel[1] for sel in selections]
        chosenRewards = [sel[2] for sel in selections]
        avgStockReturn = sum(chosenRewards) / float(self.numToPick)
        sharpeRatio = self.sharpeRatio(avgStockReturn, chosenRewards)
        return chosenStocks, avgStockReturn, sharpeRatio
    
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

        stockIndeces = numpy.argsort(p)[-self.numToPick:]

        chosenStocks = [stocks[index] for index in stockIndeces]
        chosenRewards = [rewards[index] for index in stockIndeces]
        avgStockReturn = sum(chosenRewards) / float(self.numToPick)

        sharpeRatio = self.sharpeRatio(avgStockReturn, chosenRewards)

        return chosenStocks, avgStockReturn, sharpeRatio

def runPortfolio(stockHistory=None, featurizer=None, *args):
    portfolio = Portfolio(stockHistory, featurizer, *args)
    return portfolio.run()
