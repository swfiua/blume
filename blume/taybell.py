"""
 A new table?
"""

import numpy as np
from .table import table as mpl_table

class Table:

    def __init__(self, data):

        self.data = data


    def summarise(self):

        header = []
        cols = []
        rows = []
        for key, values in self.data:
            pass

def shortify(values, maxlen=None, ellipsis='...'):
    """ Shorten the value 

    Ho-hum need to deal with long strings with new lines:

    shorten each line, and have a max number of rows?
    """
    
    result = []
    for value in values:
        aline = []
        for line in value.split('\n'):
            aline.append(shortify_line(line, maxlen, ellipsis))

        result.append('\n'.join(aline))

    return result

def shortify_line(value, maxlen=None, ellipsis='...'):

    size = len(value)
    if maxlen is None or size < maxlen:
        print(maxlen)
        return value
        
    # need to shorten and insert ...
    elen = len(ellipsis)

    # how many characters neet the chop?
    ncut = (size-maxlen) + elen

    # give beginning and end
    sluglen = (size-ncut)//2

    # and if there is a spare character, take it at the beginning
    spare = ncut - (2*sluglen)

    print(ncut, sluglen, spare)
    
    return value[:sluglen+spare] + '...' + value[-sluglen:]


        
def table(ax,
          cellText=None,
          rowLabels=None,
          colLabels=None,

          # new keyword arguments
          max_cell_width=None,
          cell_width=None,
          col_width=None,
          row_width=None,
          **kwargs):

    if max_cell_width:
        cell_width = cell_width or max_cell_width
        row_width = row_width or max_cell_width
        col_width = col_width or max_cell_width
        

    # here we need to turn cells, rows and cols into strings, unless they already are.
    if rowLabels:
        fields = [str(x) for x in rowLabels]
        rowLabels = shortify(fields, row_width)

    if colLabels:
        fields = [str(x) for x in colLabels]
        colLabels = shortify(fields, col_width)

    if cellText:
        cells = []

        for row in cellText:
            cells.append(shortify(row, cell_width))

        cellText = cells

    return mpl_table(
        ax,
        cellText=cellText,
        rowLabels = rowLabels,
        colLabels = colLabels,
        **kwargs)

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


            
