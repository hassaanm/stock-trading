import matplotlib.pyplot as plt

def plot(yss, xss=None, labels=None, title='', xlabel='', ylabel='', legendLoc=4, right=True) :
    if xss == None :
        if right :
            maxYLen = max(len(ys) for ys in yss)
            xss = [range(maxYLen - len(ys), maxYLen) for ys in yss]
        else :
            xss = [range(len(ys)) for ys in yss]
    if labels == None :
        labels = [str(i) for i in range(len(yss))]
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    ax = plt.subplot(111)
    for (xs, ys, l) in zip(xss, yss, labels) :
        ax.plot(xs, ys, label=l)
    ax.legend(loc=legendLoc)
    plt.show()