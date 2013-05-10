#!/usr/local/bin/python

import sys
import random

fname = sys.argv[1]
f = open(fname, 'r')
filteredLines = [line for line in f.readlines() if not "^" in line]
randomLines = random.sample(filteredLines, 100)
for line in randomLines :
	print line,