#!/usr/local/bin/python

from core.nn.neuralnet import trainNN
import sys

def main() :
    if len(sys.argv) < 2 :
        usage()
        sys.exit(0)
    if sys.argv[1] == 'nn' :
        trainNN(sys.argv[2:])
    
def usage() :
    print "That's not how you use this script!"

if  __name__ =='__main__':main()