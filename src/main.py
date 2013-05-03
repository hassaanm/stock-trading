#!/usr/local/bin/python

from core.nn.neuralnet import *
from core.rl.portfolio import runPortfolio
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
        testNN(args)
    elif method == 'rl' :
        # number of stocks to choose, test set percentage, starting money amount
        runPortfolio(int(args[0]), float(args[1]), float(args[2]))
    
    
def usage() :
    print "That's not how you use this script!"
    sys.exit(0)

if  __name__ =='__main__':main()
