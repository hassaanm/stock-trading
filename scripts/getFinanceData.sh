echo "Fetching stock history for" $1

START_URL="http://query.yahooapis.com/v1/public/yql?q="
END_URL="&env=http%3A%2F%2Fdatatables.org%2Falltables.env"
JSON="&format=json"

companies=(ATVI ADBE AKAM ALXN ALTR AMZN AMGN ADI AAPL AMAT ADSK ADP AVGO BIDU BBBY BIIB BMC BRCM CHRW CA CTRX CELG CERN CHKP CSCO CTXS CTSH CMCSA COST DELL XRAY DTV DISCA DLTR EBAY EQIX EXPE EXPD ESRX FFIV FB FAST FISV FOSL GRMN GILD GOOG HSIC INTC INTU ISRG KLAC LBTYA LINTA LIFE LLTC MAT MXIM MCHP MU MSFT MDLZ MNST MYL NTAP NWSA NUAN NVDA ORLY ORCL PCAR PAYX PRGO PCLN QCOM GOLD REGN ROST SNDK SBAC STX SHLD SIAL SIRI SPLS SBUX STRZA SRCL SYMC TXN VRSK VRTX VIAB VMED VOD WDC WFM WYNN XLNX YHOO)

years=(08 09 10 11 12 13)

for comp in "${companies[@]}"
do
for (( c=0; c<${#years[@]}-1; c++ ))
do
    COMPANY=$comp
    QUERY="select * from yahoo.finance.historicaldata where symbol = \\\"$COMPANY\\\" and startDate = \\\"20${years[c]}-01-01\\\" and endDate = \\\"20${years[c+1]}-01-01\\\""
    ENCODED_QUERY=$(php -r "echo rawurlencode(\"$QUERY\");")
    URL="$START_URL$ENCODED_QUERY$END_URL$JSON"
    FILE="$COMPANY.20${years[c]}.json"
    echo $FILE ":"
    curl "$URL" > $FILE
done
done

echo "Done"
