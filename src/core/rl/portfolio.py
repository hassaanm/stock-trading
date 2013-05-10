import math
import numpy
import random
import sys
from datetime import timedelta, date

from core.util.data import StockHistory, Featurizer, OPEN
from core.util.graphics import plot

def evalLinUCB(stockHistory=None, featurizer=None, dataSet='nasdaq100', graph=0, verbose=0, pickNum=5, money=10000.0, tradeCost=0.01, alpha=0.1):
    # sanitize input
    graph = int(graph)
    verbose = int(verbose)
    pickNum = float(pickNum)
    money = float(money)
    tradeCost= float(tradeCost)
    alpha = float(alpha)

    if stockHistory == None :
        stockHistory = StockHistory(dataSet)
    if featurizer == None :
        featurizer = Featurizer(stockHistory)

    startDate = stockHistory.startDate
    endDate = stockHistory.endDate
    currentDate = startDate
    testSizes = [0.1*i for i in range(1, 10)]
    testStartDates = [timedelta(days=int((endDate - startDate).days * (1 - testSize))) + startDate for testSize in testSizes]

    agents = [
        LinUCBAgent(stockHistory, featurizer, tradeCost, pickNum, money, testStartDates, alpha),
        RandomAgent(tradeCost, pickNum, money, testStartDates),
        PrevBestAgent(tradeCost, pickNum, money, testStartDates)
        ]
    names = ['LinUCB', 'Random', 'PrevBest']
    numAgents = len(agents)
    agentReturns = [[] for i in range(numAgents)]
    agentTestMoney = [[] for i in range(numAgents)]
    testingDays = []    

    print
    print 'Begin Training'

    while currentDate < endDate :
        sys.stdout.write("\r%s" %str(currentDate))
        sys.stdout.flush()
        #if currentDate == testStartDate :
        #    print
        #    print 'Begin Testing'
        companies = [company for company in stockHistory.compNames() if featurizer.isValidDate(company, currentDate)]
        features = [featurizer.getFeatures(company, currentDate) for company in companies]
        returns = [stockHistory.getReturn(0, company, currentDate) for company in companies]
        if len(companies) > 0 :
            for agent, allReturns, allMoney in zip(agents, agentReturns, agentTestMoney) :
                chosenStocks, avgReturn, sharpeRatio = agent.select(companies, features, returns)
                allReturns.append(avgReturn)
                openPrices = {company: stockHistory.get(company, currentDate, OPEN) for company in companies}
                money = agent.updateMoney(currentDate, chosenStocks, openPrices, avgReturn)
                allMoney.append(money)
                #if currentDate > testStartDate:
                #    testingDays.append(currentDate)
                #    allMoney.append(money)
                #    if verbose:
                #        if agent == agents[0] :
                #            print (' %10f\t%s\t%8.5f\t') % (money, chosenStocks, avgReturn),
                #        else : print ('%8.5f\t') % avgReturn,
                #        if agent == agents[numAgents - 1] : print
        currentDate = currentDate + timedelta(days=1)
    if graph :
        totalReturns = [[sum(returns[:i]) for i in range(len(returns))] for returns in agentReturns]
        plot(totalReturns, labels=names, ylabel='Total Return', xlabel='Time (Days)')
        for i in range(len(testSizes)) :
            yss = []
            for testMoney in agentTestMoney :
                yss.append([m[i] for m in testMoney if m[i] != 10000])
            plot(yss, labels=names, ylabel='Total Money', xlabel='Time (Days)')
    CAGRs = [agent.CAGRs(endDate) for agent in agents]
    #print 'Training days:', (testStartDate - startDate).days, 'Testing days:', (endDate - testStartDate).days, 'Total days:', (endDate - startDate).days
    for agent, name, cagr in zip(agents, names, CAGRs) :
        print name, '(money, CAGR):'
        print '\n'.join(str(s) for s in zip(testSizes, agent.moneyForTest, cagr))
        print
    return CAGRs[0]

class Agent (object) :
    def __init__(self, tradeCost, pickNum, money, testStartDates):
        self.tradeCost = float(tradeCost)
        self.numToPick = int(pickNum)
        self.startMoney = float(money)
        self.moneyForTest = [self.startMoney for t in range(len(testStartDates))]
        self.testStartDates = testStartDates

    # compound annual growth rate
    def CAGRs(self, endDate):
        cagrs = []
        for money, startDate in zip(self.moneyForTest, self.testStartDates) :
            years = (endDate - startDate).days / 365.25
            totalReturn = money / float(self.startMoney)
            cagr = (totalReturn ** (1 / years)) - 1
            cagrs.append(cagr * 100)
        return cagrs

    def updateMoney(self, date, stocks, openPrices, stockReturn):
        updatedMoney = []
        costs = self.getTradeCosts(stocks, openPrices)
        for testDate, money, cost in zip(self.testStartDates, self.moneyForTest, costs) :
            if testDate < date :
                profit = money * stockReturn
                money += (profit - cost)
                if money < 0 :
                    money = 0
            updatedMoney.append(money)
        self.moneyForTest = updatedMoney
        return self.moneyForTest

    def getTradeCosts(self, stocks, openPrices):
        costs = []
        for money in self.moneyForTest :
            perStockMoney = money / self.numToPick
            cost = 0
            for stock in stocks:
                price = openPrices[stock]
                cost += ((perStockMoney / price) * self.tradeCost * 2)
            costs.append(cost)
        return costs

    def averageReturn(self, chosenRewards) :
        return sum(chosenRewards) / float(self.numToPick)

    def sharpeRatio(self, avgReturn, rewards) :
        diffSquaredSum = sum([(r - avgReturn)**2 for r in rewards])
        stddev = (diffSquaredSum / float(self.numToPick))**0.5
        sharpeRatio = avgReturn / stddev if stddev != 0 else 0
        return sharpeRatio

    def printData(self, cagr):
        print ('%-14s %14f %2.2f') % ('Real Money:', self.moneyForTest, cagr)

class LinUCBAgent (Agent) :
    def __init__(self, stockHistory, featurizer, tradeCost, pickNum, money, testStartDates, alpha):
        super(LinUCBAgent, self).__init__(tradeCost, pickNum, money, testStartDates)
        self.stockHistory = stockHistory
        self.featurizer = featurizer
        self.companies = self.stockHistory.compNames()
        self.numberOfFeatures = self.featurizer.numFeatures
        self.A = dict()
        self.b = dict()
        self.alpha = float(alpha)

    def select(self, stocks, features, rewards):
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
        avgStockReturn = self.averageReturn(chosenRewards)

        sharpeRatio = self.sharpeRatio(avgStockReturn, chosenRewards)

        return chosenStocks, avgStockReturn, sharpeRatio

class RandomAgent (Agent) :
    def select(self, stocks, features, rewards):
        selections = random.sample(zip(stocks, rewards), min(len(stocks), self.numToPick))
        chosenStocks = [sel[0] for sel in selections]
        chosenRewards = [sel[1] for sel in selections]
        avgStockReturn = self.averageReturn(chosenRewards)
        sharpeRatio = self.sharpeRatio(avgStockReturn, chosenRewards)
        return chosenStocks, avgStockReturn, sharpeRatio

class PrevBestAgent (Agent) :
    def __init__(self, tradeCost, pickNum, money, testStartDates) :
        super(PrevBestAgent, self).__init__(tradeCost, pickNum, money, testStartDates)
        self.prevRewards = None

    def select(self, stocks, features, rewards):
        if self.prevRewards == None :
            selections = random.sample(zip(stocks, rewards), min(len(stocks), self.numToPick))
            chosenStocks = [sel[0] for sel in selections]
            chosenRewards = [sel[1] for sel in selections]
        else :
            selections = sorted(zip(self.prevRewards, stocks, rewards))[-self.numToPick:]
            chosenStocks = [sel[1] for sel in selections]
            chosenRewards = [sel[2] for sel in selections]
        self.prevRewards = rewards
        avgStockReturn = self.averageReturn(chosenRewards)
        sharpeRatio = self.sharpeRatio(avgStockReturn, chosenRewards)
        return chosenStocks, avgStockReturn, sharpeRatio
