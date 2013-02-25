#!/usr/local/bin/python
import sys

f = open(sys.argv[1], 'r')
for line in f :
    parts = line.split(",")
    sym = parts[len(parts) - 1].rstrip()
    print sym,