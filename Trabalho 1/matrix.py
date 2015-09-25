class M:
    def __init__(self, m):
        self.m = m
        self.c = []
        self.l = []
        mm = m
        while isinstance(mm, list):
            self.c.append(0)
            self.l.append(len(mm))
            mm = mm[0]
    def next(self):
        pc = []
        for i in self.c:
            pc.append(i)
        it = (self.__get_element(self.m, self.c), pc)
        i = len(self.c) - 1
        while(i >= 0):
            if(self.c[i] == self.l[i] - 1):
                self.c[i] = 0
                i -= 1
            else:
                self.c[i] += 1
                i = -1
        return it
    def __get_element(self, m, c):
        if isinstance(c, list) and len(c) > 1:
            return self.__get_element(m[c[0]], c[1:len(c)])
        else:
            return m[c[0]]
