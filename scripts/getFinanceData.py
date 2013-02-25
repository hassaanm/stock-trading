#!/usr/local/bin/python
import os
import sys
import urllib
from datetime import date
from subprocess import call

START_URL = 'http://query.yahooapis.com/v1/public/yql?env=http%3A%2F%2Fdatatables.org%2Falltables.env&format=json&q='

companies = []
symbols = []
year = date.today().year
years = range(year - 5, year)

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
print "Writing to directory", outDir

# read CSV file in, format: ID,COMPANY NAME,SYMB
f = open(csvFile, 'r')
for line in f :
    parts = line.rstrip().split(",")
    companies.append(" ".join(parts[1:len(parts)-1]))
    symbols.append(parts[len(parts) - 1])

# download data and write to files
for (comp, sym) in zip(companies, symbols) :
    for year in years :
        query = 'select * from yahoo.finance.historicaldata where symbol = "'+sym+'" and startDate = "'+str(year)+'-01-01" and endDate = "'+str(year+1)+'-01-01"'
        encoded_query = urllib.quote(query)
        url = START_URL + encoded_query
        fileName = outDir + ".".join([sym, str(year), 'json'])
        print fileName, ':'
        file = open(fileName, 'w')
        call(["curl", url], stdout=file)
    
print "Done."

