#!/usr/local/bin/python

import csv
import os
import sys
import urllib
from datetime import date
from subprocess import call

# not sure which of these urls is best, but the first seems to work alright
YAHOO_URL = 'http://query.yahooapis.com/v1/public/yql?env=http%3A%2F%2Fdatatables.org%2Falltables.env&format=json&diagnostics=true&q='
YAHOO_URL2 = 'http://query.yahooapis.com/v1/public/yql?env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys&format=json&diagnostics=true&q='

# read desired year range, default to previous 6 years (current year plus 5 full years)
if len(sys.argv) > 3 :
    startYear = int(sys.argv[2])
    endYear = int(sys.argv[3])
else :
    endYear = date.today().year
    startYear = endYear - 5
years = range(startYear, endYear + 1)

# create new directory for writing json files to
csvFile = sys.argv[1]
baseOutDir = csvFile.split('/')
baseOutDir[len(baseOutDir)-1] = baseOutDir[len(baseOutDir)-1].lower().split(".")[0]
baseOutDir = '/'.join(baseOutDir)
outDir = baseOutDir + '/'
error = os.system('mkdir ' + outDir)
i = 0
while error != 0 :
    i += 1
    outDir = baseOutDir  + "_" + str(i) + '/'
    error = os.system('mkdir ' + outDir)
print 'Writing to directory', outDir

# read CSV file
fileLines = []
with open(csvFile, 'r') as f :
    fileContents = csv.reader(f)
    for line in fileContents :
        fileLines.append(line)
header = {name.lower():i for (i, name) in enumerate(fileLines[0])}
data = fileLines[1:]

companies = [row[header['name']].rstrip() for row in data]
symbols = [row[header['symbol']].rstrip() for row in data]

# download data and write to files
for sym in symbols :
    for year in years :
        query = 'select * from yahoo.finance.historicaldata where symbol = "'+sym+'" and startDate = "'+str(year)+'-01-01" and endDate = "'+str(year+1)+'-01-01"'
        encoded_query = urllib.quote(query)
        url = YAHOO_URL + encoded_query
        fileName = outDir + '.'.join([sym, str(year), 'json'])
        print fileName, ':'
        file = open(fileName, 'w')
        call(['curl', url], stdout=file)
    
print 'Done.'
