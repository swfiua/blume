"""
 A new table
"""

import numpy as np

class Table:

    def __init__(self, data):

        self.data = data


    def summarise(self):

        header = []
        cols = []
        rows = []
        for key, values in self.data:
            pass

def tokens(line, sep=','):
    """ Split line into tokens """
    return [x.strip() for x in line.split(sep)]
        

def read(infile, tokens=tokens):
    """ parse items in infile

    first line a header, hope it gives useful dictionary keys
    """
    header = tokens(infile.readline())
    print(header)
    for row in infile:
        fields = tokens(row)
        yield dict(zip(header, fields))


            
