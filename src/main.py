#!/usr/local/bin/python

from core.nn.neuralnet import trainNN
from core.rl.portfolio import runPortfolio
import sys

def main() :
    if len(sys.argv) < 2 :
        usage()
        sys.exit(0)
    if sys.argv[1] == 'nn' :
        trainNN(sys.argv[2:])
    if sys.argv[1] == 'rl' :
        runPortfolio()
    
def usage() :
    print "That's not how you use this script!"

if  __name__ =='__main__':main()
