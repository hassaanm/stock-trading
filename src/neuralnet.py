from data import StockHistory

from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer

import matplotlib.pyplot as plt


stockHistory = StockHistory('nasdaq100')
avg100 = stockHistory.nDayAverage(100, 'GOOG', 'Open')
slope100 = stockHistory.nDaySlope(100, 'GOOG', 'Open')
stddev100 = stockHistory.nDayStdDev(100, 'GOOG', 'Open')



print '\n'.join(str(i) for i in zip(stockHistory.getData('GOOG', 'Open')[100:], avg100, stddev100, slope100))