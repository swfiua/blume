"""This could be legendary,  boom, boom!

It occurs to me that legends are tables too.

Or tables are legends, if you prefer.

Both arrange text and patches, in some sort of grid.

Rows and columns, some text and a patch of colour.  Or color?

The legend, has magic capabilities, including being able to inspect
a plot and figure out what to use for the various labels and patches.

The legend uses objects from `matplotlib.offsetbox` to do all the drawing.

These look to be the pieces that the table ought to be using.

If you think as legends as meta data regarding a plot, the row and
column headings of a table, if you like, with their associated
timelines, then the association with tables is stronger still.

The legend probes around in the plot data to uncover meta-data.

The legend code has some specific restrictions::

* each column is a pair (patch/text) or (text/patch).
* you can specify the number of columns
* rows calculated from the data
* some columns may be short.

The objects in `matplotlib.offsetbox` are more general.


notes
=====

`matplotlib.subplot_mosaic` introduces an interesting ways of
specifying table layouts.

"""

from matplotlib import offsetbox, pyplot, artist

from matplotlib.offsetbox import TextArea, HPacker, VPacker, DrawingArea
offsetbox.DEBUG = True

from blume import magic
from blume.table import Cell

class LegendArray(magic.Ball):
    """ Draw a table from a dictionary of ...

    dictionaries of artists?

    dictionaries of dictionaries

    list of dictionaries with lists of dictionaries as values.

    and so on, ad infinitum.
    
    I think the answer will be to make this all recursive.

    So hang on and lets see what goes boom!
    """
    def __init__(self, data):

        self.inner = HPacker
        self.outer = VPacker
        self.grid = Grid(data)
        pass

class Cell(offsetbox.OffsetBox):
    pass

class Grid(offsetbox.AnchoredOffsetbox):
    """ A grid of cells.

    What I really need here is just create a grid of
    nested [HV]Packers.

    But you cannot create the Packers until you have it's children.

    The way forward is less clear.

    For now, just create something, so we can explore the mode
    """
    def __init__(self,
                 data,
                 inner=None,
                 outer=None,
                 align=None,
                 mode=None,
                 transpose=False,
                 bbox=None,
                 loc=None,
                 prop=None):

        if inner is None: inner = HPacker
        if outer is None: outer = VPacker
        if transpose:
            inner, outer = outer, inner

        align = align or 'baseline'
        mode = mode or 'equal'
        loc = loc or 1
        hboxes = []

        textprops = prop.copy()
        for row in data:
            #textprops = dict(horizontalalignment='right')
            #textprops = {}
            children = [TextArea(item, textprops=textprops) for item in row]
            
            hboxes.append(inner(pad=0, sep=0, mode=mode, align=align,
                                children=children))

        vbox = outer(pad=0, sep=0, align=align, mode=mode,
                     children=hboxes)
        super().__init__(loc=loc,
                         child=vbox,
                         prop=prop)


        
