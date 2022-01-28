"""
=========
 rcparms
=========



"""

from matplotlib import rcParams

from collections import defaultdict, deque

from .magic import Ball


class Params(Ball):

    def __init__(self):

        super().__init__()
        self.params = rcParams
        self.groups = {}
        self.group_names = deque()

        self.groups = self._groups()
        self.add_filter('G', self.show_group)

    def __getitem__(self, item):

        return self.params[item]
    
    def _groups(self):

        groups = defaultdict(list)
        
        for k in self.params.keys():
            path = k.split('.')
            key = path[0]
            groups[key].append(k)

            if key not in self.group_names:
                self.group_names.append(key)

        return groups

    def show_group(self):

        name = self.group_names[0]

        for x in self.groups[name]:
            print(x, self[x])

    def group(self, name):

        return self.groups[name]
