"""
 A new table
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

def shortify(value, maxlen):
    """ Shorten the value 

    Ho-hum need to deal with long strings with new lines:

    shorten each line, and have a max number of rows?
    """

    size = len(value)
    if size < maxlen:
        return value

    # need to shorten and insert ...
    sluglen = (maxlen-3)//2
    return value[:sluglen] + '...' + value[-sluglen:]
        
def table(ax,
          cell=None,
          rows=None,
          cols=None,
          col_widths=None,
          row_label_width=None,
          **kwargs):

    # here wer need to turn cells, rows and cols into strings, unless they already are.
    if rows:
        srows = [str(x) for x in rows]
        if row_label_width:
            srows = shortify(srows, row_label_width)
        

    return mpl_table(
        ax,
        cellTexts=cells,
        rowLabels = rows or srows,
        colLabels = cols,
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


            
