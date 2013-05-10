#!/usr/local/bin/python
import sys

from core.util.data import StockHistory

folder = sys.argv[1]
sh = StockHistory(folder)

print
print 'No data:'
for fname in sh.noData :
	print ' ', fname,

print
print 'incomplete data:'
for fname in sh.incomplete :
	if '2013' not in fname :
		print ' ', fname,

print
print len(sh.noData)
print len([i for i in sh.incomplete if '2013' not in i])