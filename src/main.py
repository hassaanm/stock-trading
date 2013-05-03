#!/usr/local/bin/python

from core.nn.neuralnet import trainNN
import sys

def main() :
    if len(sys.argv) < 2 :
        usage()
    if sys.argv[1] == 'nn' :
        trainNN(sys.argv[2:])
    
def usage() :
    print "That's not how you use this script!"
    sys.exit(0)

if  __name__ =='__main__':main()