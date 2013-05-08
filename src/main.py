#!/usr/local/bin/python

from core.nn.neuralnet import *
from core.rl.portfolio import runPortfolio
from core.rl.policyGradient import policyGradient
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
    stockHistory = StockHistory('nasdaq100')
    featurizer = Featurizer(stockHistory)
    initialArgs = [5, 5, 5, 0.05, -0.05, 1.5, -1.5]
    epsilons = [1, 1, 1, 0.01, 0.01, 0.1, 0.1]
    policyGradient(initialArgs, epsilons)
    
def usage() :
    print "That's not how you use this script!"
    sys.exit(0)

if  __name__ =='__main__':main2()
