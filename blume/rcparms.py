"""
=========
 rcparms
=========



"""

from matplotlib import rcParams, rc

from collections import defaultdict, deque

from .magic import Ball


class Params(Ball):

    def __init__(self):

        super().__init__()
        self.params = rcParams

        self.groups = {}
        self.group_names = deque()

        self.groups = self._make_groups()

        self.add_filter('G', self.show_group)
        self.add_filter('N', self.next_group)

        self.add_filter('g', self.next_group)

    def next_group(self):

        self.group_names.rotate()
        self.show_group(self.group_names[0])
        
    def __getitem__(self, item):

        return self.params[item]

    def __setitem__(self, item, value):

        self.params[item] = value

    
    def _make_groups(self):

        groups = defaultdict(dict)
        
        for k, v  in self.params.items():
            path = k.split('.')
            key = path[0]
            groups[key][k] = v

            if key not in self.group_names:
                self.group_names.append(key)

        self.groups = groups

        self.group_names = deque(sorted(self.groups.keys()))
        
        return groups

    def next_group(self):

        self.groups.rotate()

    def show_group(self):

        name = self.group_names[0]

        for x in self.groups[name]:
            print(x, self[x])

    def group(self, name):

        return self.groups[name]
