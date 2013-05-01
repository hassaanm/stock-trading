class Writer :
    def __init__(self, fname, append=False) :
        self.fname = fname
        self.text = []
        self.append = append
    
    def add(self, s, newline=True) :
        if newline :
            self.text.append(str(s))
        else :
            self.text[-1] = self.text[-1] + str(s)
    
    def write(self, append=False) :
        f = open(self.fname, 'a' if append else 'w')
        f.write('\n'.join(self.text))
        f.close()