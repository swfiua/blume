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

class LegendArray(offsetbox.AnchoredOffsetbox):
    """ Draw a table from a dictionary of ...

    dictionaries of artists?

    dictionaries of dictionaries

    list of dictionaries with lists of dictionaries as values.

    and so on, ad infinitum.
    
    I think the answer will be to make this all recursive.

    So hang on and lets see what goes boom!
    """

    def __init__(self,
                 data,
                 inner=None,
                 outer=None,
                 transpose=False):

        if inner is None: inner = HPacker
        if outer is None: outer = VPacker
        if transpose:
            inner, outer = outer, inner

        hboxes = []

        for row in data:
            hboxes.append(inner(pad=0, sep=0,
                                children=[TextArea(item) for item in row]))

        vbox = outer(pad=0, sep=0,
                     children=hboxes)
        super().__init__(loc=1,
                         child=vbox)
