#!/usr/local/bin/python

from core.nn.neuralnet import *
from core.rl.portfolio import runPortfolio
from core.util.data import StockHistory
import sys

def main() :
    if len(sys.argv) < 2 :
        usage()
    method = sys.argv[1]
    args = sys.argv[2:]
    if method == 'nn' :
        trainNN(args)
    elif method == 'retrainNN' :
        testNN(args)
    elif method == 'testNN' :
        testNN(loadNN(args))
    elif method == 'rl' :
        # number of stocks to choose, test set percentage, starting money amount
        runPortfolio(*args)
    
def main2() :
    args = sys.argv[1:]
    stockHistory = StockHistory('nasdaq100')
    featurizer = Featurizer(stockHistory, *args)
    numDaysHistory=range(2, 11)
    slopeN=range(2, 11)
    averageN=range(2, 11)
    returnThreshold=[0.025 * i for i in range(-4, 5)]
    slopePos=[0.5 * i for i in range(1, 10)]
    slopeNeg=[-0.5 * i for i in range(1, 10)]
    stats=[]
    runPortfolio(stockHistory, featurizer)
    
def usage() :
    print "That's not how you use this script!"
    sys.exit(0)

if  __name__ =='__main__':main2()
