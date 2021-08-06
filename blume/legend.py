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

from matplotlib import legend
from matplotlib.offsetbox import TextArea, HPacker, VPacker, DrawingArea

from blume import magic
from blume.table import Cell

def legend(data, inner=HPacker, outer=VPacker, transpose=False):
    """ Draw a table from a dictionary of ...

    dictionaries of artists?

    dictionaries of dictionaries

    list of dictionaries with lists of dictionaries as values.

    and so on, ad infinitum.
    
    I think the answer will be to make this all recursive.

    So hang on and lets see what goes boom!
    """
    if transpose:
        inner, outer = outer, inner
    hboxes = []

    for row in data:
        hboxes.append(inner(children=row))

    return outer(children=hboxes)
            

class Legend(magic.Ball):

    async def run(self):

        ax = pyplot.subplot()
        leg = legend([[]])

        await self.put()


    
if __name__ == '__main__':


    import argparse
    from blume import farm as land
    import numpy as np

    parser = argparse.ArgumentParser()
    parser.add_argument('--cols', type=int, default=6)

    args = parser.parse_args()

    cols = args.cols
    
    words = [x.strip() for x in legend.__doc__.split()]

    words = np.array(words)
    words[:cols * cols].reshape(cols, cols)
    
    leg = legend(words)

    farm = land.Farm()

    farm.add(leg)

    farm.shep.path.append(leg)

    land.start_and_run(farm)
