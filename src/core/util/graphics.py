import matplotlib.pyplot as plt

def plot(yss, xss=None, labels=None, yerrs=None, title='', xlabel='', ylabel='', legendLoc=4, right=True) :
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