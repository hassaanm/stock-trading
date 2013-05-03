#!/usr/local/bin/python

from core.nn.neuralnet import trainNN
from core.rl.portfolio import runPortfolio
import sys

def main() :
    if len(sys.argv) < 2 :
        usage()
    if sys.argv[1] == 'nn' :
        trainNN(sys.argv[2:])
    if sys.argv[1] == 'rl' :
        # number of stocks to choose, test set percentage, starting money amount
        runPortfolio(int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]))
    
def usage() :
    print "That's not how you use this script!"
    sys.exit(0)

if  __name__ =='__main__':main()
