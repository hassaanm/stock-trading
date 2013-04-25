from core.util.data import StockHistory
from core.util.graphics import plot

from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer

stockHistory = StockHistory('nasdaq100')
avg100 = stockHistory.nDayAverage(100, 'GOOG', 'Open')
slope100 = stockHistory.nDaySlope(100, 'GOOG', 'Open')
stddev100 = stockHistory.nDayStdDev(100, 'GOOG', 'Open')

avg10 = stockHistory.nDayAverage(10, 'GOOG', 'Open')
slope10 = stockHistory.nDaySlope(10, 'GOOG', 'Open')
stddev10 = stockHistory.nDayStdDev(10, 'GOOG', 'Open')

print '\n'.join(str(i) for i in zip(stockHistory.getData('GOOG', 'Open')[100:], avg100, stddev100, slope100))

plot([avg100, stockHistory.getData('GOOG', 'Open')])
plot([avg10, stockHistory.getData('GOOG', 'Open')])
