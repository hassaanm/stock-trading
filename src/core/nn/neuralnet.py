from core.util.data import StockHistory, TrainingSet, Featurizer
from core.util.graphics import plot
import pickle
from pybrain.datasets import SupervisedDataSet
from pybrain.structure import TanhLayer
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.tools.shortcuts import buildNetwork
from time import time

def trainNN(args) :
    print 'Begin training Neural Network'
    print
    print 'Reading data'
    stockHistory = StockHistory('nasdaq100')
    companies = stockHistory.compNames()
    featurizer = Featurizer(stockHistory, *args)
    nF = featurizer.numFeatures
    nO = featurizer.numTargetFeatures
    print
    
    print 'Using', str(nF), 'input features with', str(nO), 'output features'
    print 'Generating training set'
    ds = SupervisedDataSet(nF, nO)
    featureStats = [0 for i in range(nF)]
    outputStats = [0 for i in range(nO)]
    correlations = [[0 for i in range(nO)] for j in range(nF)]
    numTrainingExamples = 0
    for company in companies :
        trainingSet = TrainingSet(featurizer, company)
        for trainingExample in trainingSet :
            features = trainingExample.features
            output = trainingExample.output
            for i in range(nF) :
                featureStats[i] += features[i]
                for j in range(nO) :
                    if output[j] == 1 and features[i] == output[j] :
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
        print i, '\t', fs, '     \t', [float(c)/numTrainingExamples for c in correlations[i]]
    print
    print 'Building network'
    netStructure = [nF, nF, nF, nO]
    net = buildNetwork(*netStructure, bias=True, hiddenclass=TanhLayer)
    trainer = BackpropTrainer(net, ds, verbose=True)
    print 'Training'
    start = time()
    errorsPerEpoch = trainer.trainUntilConvergence(outFile='.'.join(['nn']+args+['info']))
    end = time()
    print 'Training time:', (end - start)
    print errorsPerEpoch
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
    f = open('.'.join(['nn']+args+['dat']), 'w')
    pickle.dump(net, f)
    f.close()
    print
    print 'Graphing errors during training'
    try:
        plot(errorsPerEpoch)
    except:
        pass
    return net
    
def retrainNN(args) :
    net = pickle.load(args[0])
    
def testNN(args) :
    net = pickle.load(args[0])
    
