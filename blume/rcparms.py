"""
=========
 rcparms
=========



"""

from matplotlib import rcParams

from collections import defaultdict

from .magic import Ball


class Params(Ball):

    def __init__(self):

        super().__init__()
        self.params = rcParams
        self.groups = self._groups()

    def __getitem__(self, item):

        return self.params[item]
    
    def _groups(self):

        groups = defaultdict(list)
        
        for k in self.params.keys():
            path = k.split('.')
            groups[path[0]].append(k)

        return groups

    def show_group(self, name):

        for x in self.groups[name]:
            print(x, self[x])

    def group(self, name):

        return self.groups[name]
