#!/usr/local/bin/python

from core.nn.neuralnet import *
from core.rl.portfolio import evalLinUCB
from core.rl.policyGradient import policyGradient
from core.util.data import StockHistory
import sys

def main() :
    if len(sys.argv) < 2 :
        usage()
    method = sys.argv[1]
    args = sys.argv[2:]
    argDict = {arg.split('=')[0]:arg.split('=')[1] for arg in args}
    if method == 'nn' :
        trainNN(**argDict)
    elif method == 'retrainNN' :
        testNN(**argDict)
    elif method == 'testNN' :
        testNN(loadNN(**argDict))
    elif method == 'rl' :
        # number of stocks to choose, test set percentage, starting money amount
        evalLinUCB(None, None, **argDict)
    elif method == 'pg' :
        policyGradient(**argDict)
    
def usage() :
    print "That's not how you use this script!"
    sys.exit(0)

if  __name__ =='__main__':main()
