from core.util.data import StockHistory, TrainingSet
from core.util.graphics import plot
from pybrain.datasets import SupervisedDataSet
from pybrain.structure import TanhLayer
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.tools.shortcuts import buildNetwork
from time import time

HIDDEN_LAYERS = 2

print 'Begin training Neural Network with', str(HIDDEN_LAYERS), 'hidden layers'
print
print 'Reading data'
stockHistory = StockHistory('nasdaq100')
companies = stockHistory.compNames()
nF = TrainingSet.numFeatures
nO = TrainingSet.numTargetFeatures
print

print 'Using', str(nF), 'input features with', str(nO), 'output features'
print 'Generating training set'
ds = SupervisedDataSet(nF, nO)
featureStats = [0 for i in range(nF)]
outputStats = [0 for i in range(nO)]
correlations = [[0 for i in range(nO)] for j in range(nF)]
numTrainingExamples = 0
for company in companies :
    trainingSet = TrainingSet(stockHistory, company)
    for trainingExample in trainingSet :
        features = trainingExample.features
        output = trainingExample.output
        for i in range(nF) :
            featureStats[i] += features[i]
            for j in range(nO) :
                if features[i] == output[j] :
                    correlations[i][j] += 1
        for i in range(nO) :
            outputStats[i] += output[i]
        numTrainingExamples += 1
        ds.addSample(features, output)
        
print 'Training set statistics:'
print 'Number of training examples:', numTrainingExamples
print 'Percent of examples with output:', [float(i)/numTrainingExamples for i in outputStats]
print 'i, Percent with feature, Correlation with output:'
for i in range(len(correlations)):
    fs = float(featureStats[i])/numTrainingExamples
    print i, '\t', fs, '\t', [float(c)/numTrainingExamples for c in correlations[i]]
print
print 'Building network'
net = buildNetwork(nF, HIDDEN_LAYERS, nO, bias=True, hiddenclass=TanhLayer)
trainer = BackpropTrainer(net, ds)
print 'Training'
start = time()
errorsPerEpoch = trainer.trainUntilConvergence()
end = time()
print 'Training time:', (end - start)
print
print 'Graphing errors during training'
plot(errorsPerEpoch)
print
for mod in net.modules:
    print "Module:", mod.name
    if mod.paramdim > 0:
        print "--parameters:", mod.params
    for conn in net.connections[mod]:
        print "-connection to", conn.outmod.name
        if conn.paramdim > 0:
            print "- parameters", conn.params
    if hasattr(net, "recurrentConns"):
        print "Recurrent connections"
        for conn in net.recurrentConns:             
            print "-", conn.inmod.name, " to", conn.outmod.name
            if conn.paramdim > 0:
                print "- parameters", conn.params
print
print 'Done'