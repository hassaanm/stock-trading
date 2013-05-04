graphing = False
try :
    import matplotlib.pyplot as plt
    graphing = True
except :
    pass

def plot(yss, xss=None, labels=None, yerrs=None, title='', xlabel='', ylabel='', legendLoc=4, right=True, scale=False) :
    if not graphing :
        print 'Graphing is not available'
        return
    if scale :
        # the set of ys with the largest range is assummed to be at the end
        scaleYs = yss[-1]
        largeRange = max(scaleYs) - min(scaleYs)
        nextLargestRange = 0
        for i in range(len(yss) - 1) :
            ys = yss[i]
            r = max(ys) - min(ys)
            if r > nextLargestRange :
                nextLargestRange = r
        multiplier = float(largeRange) / nextLargestRange
        for i in range(len(yss) - 1) :
            ys = yss[i]
            for j in range(len(ys)) :
                ys[j] *= multiplier
    if labels == None :
        labels = [str(i) for i in range(len(yss))]
    if yerrs != None :
        for i in range(len(yerrs)) :
            ys = yss[i]
            yerr = yerrs[i]
            label = labels[i]
            if yerr != None :
                yss.append([y+e for (y,e) in zip(ys, yerr)])
                yss.append([y-e for (y,e) in zip(ys, yerr)])
                labels.append(label + ' +err')
                labels.append(label + ' -err')
    if xss == None :
        if right :
            maxYLen = max(len(ys) for ys in yss)
            xss = [range(maxYLen - len(ys), maxYLen) for ys in yss]
        else :
            xss = [range(len(ys)) for ys in yss]
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    ax = plt.subplot(111)
    for (xs, ys, l) in zip(xss, yss, labels) :
        ax.plot(xs, ys, label=l)
    ax.legend(loc=legendLoc)
    plt.show()
    
def plotDistribution(values, chop, r) :
    graphVals = {}
    for v in values :
        rv = round(v, r)
        if rv in graphVals :
            graphVals[rv] += 1
        else :
            graphVals[rv] = 1
    xs = sorted(graphVals.keys())[:chop]
    ys = [graphVals[x] for x in xs]
    print zip(xs, ys)
    plot([ys], [xs])
