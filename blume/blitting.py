"""
==================================
Faster rendering by using blitting
==================================

This module is derived from the code for the `matplotlib tutorial on
rendering
<https://matplotlib.org/stable/tutorials/advanced/blitting.html>`__.




*Blitting* is a `standard technique
<https://en.wikipedia.org/wiki/Bit_blit>`__ in raster graphics that,
in the context of Matplotlib, can be used to (drastically) improve
performance of interactive figures. For example, the
:mod:`.animation` and :mod:`.widgets` modules use blitting
internally. Here, we demonstrate how to implement your own blitting, outside
of these classes.

Blitting speeds up repetitive drawing by rendering all non-changing
graphic elements into a background image once. Then, for every draw, only the
changing elements need to be drawn onto this background. For example,
if the limits of an Axes have not changed, we can render the empty Axes
including all ticks and labels once, and only draw the changing data later.

The strategy is

- Prepare the constant background:

  - Draw the figure, but exclude all artists that you want to animate by
    marking them as *animated* (see `.Artist.set_animated`).
  - Save a copy of the RBGA buffer.

- Render the individual images:

  - Restore the copy of the RGBA buffer.
  - Redraw the animated artists using `.Axes.draw_artist` /
    `.Figure.draw_artist`.
  - Show the resulting image on the screen.

One consequence of this procedure is that your animated artists are always
drawn on top of the static artists.

Not all backends support blitting.  You can check if a given canvas does via
the `.FigureCanvasBase.supports_blit` property.

.. warning::

   This code does not work with the OSX backend (but does work with other
   GUI backends on mac).

   Update: this code now seems to work with the default OSX backend.

Minimal example
---------------

We can use the `.FigureCanvasAgg` methods
`~.FigureCanvasAgg.copy_from_bbox` and
`~.FigureCanvasAgg.restore_region` in conjunction with setting
``animated=True`` on our artist to implement a minimal example that
uses blitting to accelerate rendering

"""

import matplotlib.pyplot as plt

from matplotlib.transforms import Bbox

class BlitManager:
    def __init__(self, canvas, animated_artists=()):
        """
        Parameters
        ----------
        canvas : FigureCanvasAgg
            The canvas to work with, this only works for sub-classes of the Agg
            canvas which have the `~FigureCanvasAgg.copy_from_bbox` and
            `~FigureCanvasAgg.restore_region` methods.

        animated_artists : Iterable[Artist]
            List of the artists to manage
        """
        self.canvas = canvas
        self._bg = None
        self._base = None
        self._artists = {}

        for a in animated_artists:
            self.add_artist(a)
        # grab the background on every draw
        self.cid = canvas.mpl_connect("draw_event", self.on_draw)
        self.rid = canvas.mpl_connect("resize_event", self.on_resize)

    def on_resize(self, event):

        # tile the figure with current base
        self._tile(self._base)

        # now take a snapshot of the figure
        cv = self.canvas

        # this probably has to wait for the tile to be done???
        self._base = cv.copy_from_bbox(cv.figure.bbox)
        self._bg = self._base

    def clear(self):

        self._bg = self._base
        self._artists.clear()

    def filter(self, keepers):

        keep = [tuple(k.get_subplotspec().get_position(k.figure).extents)
                for k in keepers]

        for key in list(self._artists.keys()):
            if key not in keep:
                del self._artists[key]
        

    def _tile(self, base):
        """ Use base to tile the canvas """
        x1, y1, x2, y2 = self._base.get_extents()

        bwidth= x2 - x1
        bheight = y2 - y1

        # capture a new base background
        cv = self.canvas
        width, height = cv.get_width_height()

        xpos = 0
        while xpos < width:
            ypos = 0

            while ypos < height:
                twidth = min(bwidth, width-xpos)
                theight = min(bheight, height-ypos)
            
                bbox = Bbox([[0, 0], [xpos+twidth, xpos+theight]])
            
                cv.restore_region(self._base, bbox, (xpos, ypos))
                print('TILE', bbox)

                ypos += bheight
                
            xpos += bwidth
            
        
    def on_draw(self, event):
        """Callback to register with 'draw_event'."""
        print('DRAW EVENT', event)
        cv = self.canvas
        if event is not None:
            if event.canvas != cv:
                raise RuntimeError
            
        self.set_background()
        self._draw_animated()

    def set_background(self, bg=None):

        print('BBBBACKGROUND', self._bg)
        cv = self.canvas
        self._bg = bg or cv.copy_from_bbox(cv.figure.bbox)
        if self._base is None:
            self._base = self._bg

    def add_artist(self, art, key=None):
        """
        Add an artist to be managed.

        Parameters
        ----------
        art : Artist

            The artist to be added.  Will be set to 'animated' (just
            to be safe).  *art* must be in the figure associated with
            the canvas this class is managing.

        """

        key = key or tuple(art.get_subplotspec().get_position(art.figure).extents)
        
        if art.figure != self.canvas.figure:
            raise RuntimeError
        art.set_animated(True)
        self._artists[key] = art

    def forget_artist(self, artist):

        if artist in self._artists:
            self._artists.remove(artist)
        
    def _draw_animated(self):
        """Draw all of the animated artists."""
        fig = self.canvas.figure
        for a in self._artists.values():
            fig.draw_artist(a)

    def update(self, ax=None):
        """Update the screen with animated artists."""
        cv = self.canvas
        fig = cv.figure
        # paranoia in case we missed the draw event,
        if self._bg is None:
            self.on_draw(None)
        else:
            # restore the background
            if ax:
                cv.restore_region(self._bg)
                # draw the axis
                #print(fig.bbox.bounds)
                #print(ax.bbox.bounds)

                full_bbox = self.get_full_bbox(ax)
                #print(full_bbox)
                ss = ax.get_subplotspec()
                #print(ss)
                cv.restore_region(
                    self._base,
                    full_bbox,
                    (full_bbox.xmin, full_bbox.ymin))
                #cv.restore_region(
                #    self._base,
                #    fig.bbox, (0, 0))

                fig.draw_artist(ax)
            else:
                cv.restore_region(self._base)
                # draw all of the animated artists
                #print('animated', len(self._artists))
                self._draw_animated()

            # update the GUI state
            cv.blit(fig.bbox)
            #self._bg = cv.copy_from_bbox(fig.bbox)

        # let the GUI event loop process anything it has to do
        cv.flush_events()

    def get_full_bbox(self, ax):

        ss = ax.get_subplotspec()
        fig = self.canvas.figure
        fbbox = fig.bbox
        
        rows, cols, row, col = ss.get_geometry()

        width = fbbox.width / cols
        height = fbbox.height / rows

        xpos = width * col
        ypos = height * row

        return Bbox([[xpos, ypos], [xpos+width, xpos+height]])
