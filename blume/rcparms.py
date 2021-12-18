"""
=========
 rcparms
=========



"""

from matplotlib import rcParams


from .magic import Ball


class Params(Ball):

    def __init__(self):

        super().__init__()
        self.params = rcParams

    
