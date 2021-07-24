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

The legend code has some specific restrictions::

* each column is a pair (patch/text) or (text/patch).
* you can specify the number of columns
* rows calculated from the data
* some columns may be short.

The objects in `matplotlib.offsetbox` are more general.


`matplotlib.subplot_mosaic`

"""
