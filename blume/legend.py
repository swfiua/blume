"""This could be legendary,  boom, boom!

It occurs to me that legends are tables too.

Or tables are legends, if you prefer.

Both arrange text and patches, in some sort of grid.

Rows and columns, some text and a patch of colour.  Or color?

The legend, has magic capabilities, including being able to inspect
a plot and figure out what to use for the various labels and patches.

The patches for the legend are just `handles` for which there are a
number of magic functions that turn the handle into an `Artist` to
represent that handle in the legend.

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

After more digging around in matplotlib inards I discovered the
LayoutGrid class.

`_layoutgrid`

This one uses constraints and a solver to deal with layouts.

There's a lot of offsetbox code that would not be needed.

The key thing about an `offsetbox.Artist` that it knows the fontsize
and should aim to ensure that it's size is proportional to the
fontsize.  This is achieved by making things such as padding a
multiple of the fontsize.

This is desirable for packing tables with text and provides a way to
scale the whole image by adjusting a single fontsize variable.

It can save a lot of work over the current table, constantly measuring
text.

Presumably we can add the fontsize into the whole thing as a
constraint of some sort?

In short, I think I have another module to take a look at.

Update: the subplot_mosaic code has some great ideas.

It is very much focussed on axes.

Nested mosaic's of axes open up a lot of interesting opportunities,
here's hoping we can transform these mosaics and keep track of all the
axes.

`subplot_mosaic` gives us a figure and a dictionary of axes.



"""
import traceback
from matplotlib import offsetbox, pyplot, artist, transforms, figure
from matplotlib import _layoutgrid as layoutgrid

from matplotlib.offsetbox import TextArea, HPacker, VPacker, DrawingArea
#offsetbox.DEBUG = True

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

        textprops = None
        if prop:
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
                         #bbox_to_anchor=(0, 0, 1, 1),
                         child=vbox,
                         prop=prop)

    def scale(self, factor):

        for child in self._children:
            for gchild in child._children:
                t = gchild._text
                t.set_size(t.get_size() * factor)
                

    def get_window_extent(self, renderer):
        """Return the bounding box of the table in window coords."""

        boxes = []
        for child in self.get_children():
            boxes += [x.get_window_extent(renderer) for x in child.get_children()]
        
        return transforms.Bbox.union(boxes)

    def xdraw(self, renderer):

        self.facecolor = COLORS[0]
        COLORS.rotate()
        print(f'drawing grid {id(self)} color {self.facecolor}')
        print(f'drawing grid {id(self)} axes {self.axes}')
        #traceback.print_stack()
        from matplotlib.patches import bbox_artist
        props= dict(pad=20)
        bbox_artist(self, renderer, props=props, fill=True)
        #print('drawn', self.get_window_extent(renderer))
        super().draw(renderer)

from collections import deque
import random
        
COLORS = deque(['skyblue', 'green', 'yellow', 'pink', 'orange',
                [random.random()/2,
                 random.random()/2,
                 random.random()/2]])

        
class LayoutGrid(layoutgrid.LayoutGrid):
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
                 loc=None):


        if inner is None: inner = HPacker
        if outer is None: outer = VPacker
        if transpose:
            inner, outer = outer, inner

        align = align or 'baseline'
        mode = mode or 'equal'
        loc = loc or 1
        hboxes = []

        super().__init__(nrows=len(data), ncols=len(data[0]))

        for rix, row in enumerate(data):
            for cix, col in enumerate(row):
                self.add_child(TextArea(col), rix, cix)



    def draw(self, renderer):

        x0, y0, x1, y1 = self.get_extent(renderer)

        bbox = transforms.Bbox(((x0,y0), (x1,y1)))
        print(bbox.p0, bbox.p1)
        print(renderer.dpi)
        print(f'{bbox}')
        super().draw(renderer)


class Carpet:
    """ A figure to manage a bunch of axes in a mosaic.
    """
    def __init__(self):

        self.fig = pyplot.figure()
        self.gs = self.fig.add_gridspec(1,1)
        self.axes = {}

        
    def set_mosaic(self, mosaic, axes=None):
        """Set the figures mosaic 

        Aim to do this in a way we can keep track of the axes.

        Returns a dictionary of newly added axes and the (updated)
        existing dictionary of all axes.
        """

        fig = self.fig
        
        # delete what is there
        for ax in fig.axes:
            fig.delaxes(ax)

        fig._gridspecs = []
        new_axes = fig.subplot_mosaic(mosaic)

        newones = {}
        for key, nax in new_axes.items():
            ax = self.axes.get(key)

            if ax:
                #print('switching old to new spec', key)
                ax.set_subplotspec(nax.get_subplotspec())

                fig.delaxes(nax)
                fig.add_subplot(ax)
            else:
                self.axes[key] = nax
                newones[key] = nax

        
        return newones,  self.axes
    
