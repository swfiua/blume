"""A new table?

The current table was written with a very specific problem in mind and
the code reflects this to a large degree.

Take a grid of values, with optional row and column labels and draw
it, typically under the axes of some plot.

By default, it adjusts the font size until it finds one that best fits
the available space.

Much of the complexity of the code comes from the fact that it is only
at the time of drawing do we get a graphics context that allows us to
measure text.

Since making the font smaller is not the only option to make things
fit, it seems natural to allow other options.

I think the solution here is to split things into a few different layers.

At the core, something that just takes the grid of cells and draws them.

Wrapper classes can then do the font scaling, text eliding, or
whatever transformations might be of interest.

Wrappers around wrappers?

Another way to shrink the table is to summarise the rows, or columns.

For example, as table.describe() does for `pandas` tables.

"""

import numpy as np
from . import table as mpl_table
#from . import Cell as mpl_Cell

class Cell:
    pass

class Table:

    def __init__(self, data):

        self.data = data

    def add_cell(self, cell, *args, **kwargs):
        pass

    def summarise(self):

        header = []
        cols = []
        rows = []
        for key, values in self.data:
            pass

    def draw_table(self):
        """ Draw the table """
        pass

class MagicTable(Table):
    """ """
    pass

def shortify(values, maxlen=None, ellipsis=None, squash=None):
    """ Shorten the value 

    Ho-hum need to deal with long strings with new lines:

    shorten each line, and have a max number of rows?
    """
    
    result = []
    for value in values:
        aline = []
        for line in value.split('\n'):
            aline.append(shortify_line(line, maxlen, ellipsis, squash))

        result.append('\n'.join(aline))

    return result

def shortify_line(value, maxlen=None, ellipsis=None, squash=None):

    ellipsis = ellipsis or '...'
    size = len(value)
    if maxlen is None or size <= maxlen:
        return value

    maxlen = int(maxlen)

    # try removing space -- maybe camel case too?
    if squash:
        for key in squash:
            value = value.replace(key, '')
            if len(value) <= maxlen:
                return value

        # update size
        size = len(value)

    # how many characters neet the chop?
    ncut = size-maxlen

    while ncut < len(ellipsis) and ellipsis:
        ellipsis = ellipsis[:-1]

    elen = len(ellipsis)

    # give equal to beginning and end
    sluglen = (size-(ncut+elen))//2

    # and if there is a spare character, take it at the beginning
    spare = maxlen - ((2*sluglen) + elen)
    value = value[:sluglen+spare] + ellipsis + value[-sluglen:]
    #print('slug/spare/elen/value', sluglen, spare, elen, maxlen, size, len(value))
    return value

def taybell(ax, cells):
    """ """
    pass
        
        
def table(ax,
          cellText=None,
          rowLabels=None,
          colLabels=None,

          # new keyword arguments
          max_cell_width=None,
          cell_width=None,
          col_width=None,
          row_width=None,
          squash=None,
          **kwargs):

    if max_cell_width:
        cell_width = cell_width or max_cell_width
        row_width = row_width or max_cell_width
        col_width = col_width or max_cell_width
        

    # here we need to turn cells, rows and cols into strings, unless they already are.
    if rowLabels:
        fields = [str(x) for x in rowLabels]
        rowLabels = shortify(fields, row_width, squash=squash)

    if colLabels:
        fields = [str(x) for x in colLabels]
        colLabels = shortify(fields, col_width, squash=squash)

    if cellText:
        cells = []

        for row in cellText:
            cells.append(shortify(row, cell_width, squash=squash))

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


            
