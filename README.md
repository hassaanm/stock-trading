## Required libraries:

* [numpy](http://www.numpy.org/)
* [scipy](http://www.scipy.org/)
* [pyplot](http://matplotlib.org/api/pyplot_api.html)

## Running the code :

To run our main experiment on data in the NASDAQ top 100 companies:

    python src/main.py rl
Available options : dataSet, graph, verbose, pickNum, money, tradeCost, alpha
Examples:
    python src/main.py rl dataSet=nasdaqAll
    python src/main.py rl graph=1 verbose=1 pickNum=10
    python src/main.py rl alpha=0.9 tradeCost=0.005 money=100000 pickNum=15 verbose=1 graph=1 dataSet=nyse_random

To run our policy search algorithm:

    python src/main.py pg
Available options: T, maxStaticRewards, maxShift, maxIterations, alpha, dataSet

Examples:
    python src/main.py pg dataSet=nyse100
    python src/main.py pg maxStaticRewards=10 maxIterations=1000 alpha=0.9 dataSet=nyse100
    python src/main.py pg T=6 maxStaticRewards=6 maxShift=4 maxIterations=10 alpha=0.9 dataSet=nyse100