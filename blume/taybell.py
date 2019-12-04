"""
 A new table
"""

from numpy import numpy

class Table:

    def __init__(self, data):

        self.data = data


    def summarise(self):

        header = []
        cols = []
        rows = []
        for key, values in self.data:
            pass
            
