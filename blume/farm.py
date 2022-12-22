"""Split the farm from magic.

The reason for this split is a growing belief that almost everything in the farm,
and the Farm itself should be some sort of Ball.

And wanting the default Farm to have a basic structure running with
everything a typical Ball might need, it needs to import some examples
from other modules.  Since those modules use magic, the end result is
a circular import.

This splt also allows me to think about what lives where.  And how
everything relates.  

Plan
====

This Farm is currently just a directed graph.  It feels like round
abouts should be the graph nodes, with their edges being the graph
edges.

That should simplify things a little from the current code.

I would like to change how the graph connects objects dynamically, in
a similar way to the way I can change attributes of running Ball's
with the magic.Interact object.

The Farm seems the right place -- or maybe the Shepherd?

Objects with a start and a run.

That might start and run each other.

Balls can write things to a queue.

The plan in magic land is to get the magic roundabout working.

At the moment there is a magic roundabout for each Ball.

"""
import random

import math

import io

from pathlib import Path

from collections import deque, defaultdict

import datetime

#import curio
import asyncio
curio = asyncio

import numpy as np

from PIL import Image

import matplotlib

from matplotlib import figure, rc, colors, patches

from matplotlib import pyplot as plt
from matplotlib.transforms import Bbox

#from .mosaic import Carpet

from blume import magic, console
from .magic import Ball, RoundAbout, GeeFarm, fig2data, Shepherd
from .mclock2 import GuidoClock
from .rcparms import Params

class PatchColours:

    def __init__(self):
        self.colours = deque(
            ('skyblue',))
        return
        self.colours = deque(
            ('skyblue', 'lightgreen', 'yellow', 'pink', 'orange'))

        for extra in range(4):
            self.colours.append(
             [random.random()/2,
              random.random()/2,
              random.random()/2])

    def next(self):

        self.colours.rotate()
        return self.colours[0]

Colours = PatchColours()

class Axe:
    """ A matplotlib axis that has some extra methods 

    The idea is to hand these out to anyone looking for an axis.
    
    By wrapping the axis object we can carry around some meta data
    that might come in useful.

    But mostly I want an Axis that I can show and hide from the figure
    and change its layout.

    I would like to just go with show and hide, but suspect I might need 
    draw too.
    """

    def __init__(self, delegate, carpet):

        self.delegate = delegate
        self.carpet = carpet

    def __getattr__(self, attr):

        try:
            return getattr(self.delegate, attr)
        except AttributeError as e:
            # fixme:
            #raise e
            raise AttributeError

    def position(self, target):
        """ Set position to that of target """
        sps = self.get_subplotspec()
        self.set_subplotspec(target.get_subplotspec())

    def show(self):
        """ Show the axes """
        self.set_visible(True)
        if not hasattr(self, 'img'):
            self._blank()
        else:
            self.img.set_visible(True)
        self.carpet.show(self)

    def hide(self):
        """ Hide the axes """
        self.set_visible(False)
        if hasattr(self, 'img'):
            self.img.set_visible(False)
        self.carpet.hide(self)

    def please_draw(self):
        """ Try to force a draw of the axes """
        print('politely asked to draw')
        #self.draw_artist(self)

    def projection(self, name):
        """ Set the projection 

        Not sure if this is possible.
        """
        ax = self.delegate
        parms = dict(projection=name, visible = False)

        pax = ax.figure.subplots(subplot_kw=parms)

        self.delegate = pax
        self.position(ax)
        self.carpet.lookup[id(pax)] = self

        if hasattr(ax, 'img'):
            ax.img.remove()

        # now delete ax
        ax.remove()

    def simplify(self):

        #self.xaxis.set_visible(False)
        #self.yaxis.set_visible(False)
        self.axis('off')

    def colorbar(self, mappable):

        self.figure.colorbar(mappable, self)

    def hide_axes(self):

        self.get_xaxis().set_visible(False)
        self.get_yaxis().set_visible(False)

    def get_id(self):

        return id(self.delegate)

    def _blank(self):

        fig = self.figure

        bb = self.get_full_bbox()

        self.img = patches.Rectangle(
            bb.p0,
            bb.width, bb.height,
            facecolor=Colours.next()
        )

        # add patch to the background
        self.carpet.background.add_artist(self.img)
        
        
    def get_full_bbox(self):
        # FIXME -- this needs to take account of padding of the figure
        #  see toggle_expand
        ss = self.get_subplotspec()
        gs = ss.get_gridspec()

        nrows, ncols = gs.get_geometry()

        fig = self.figure
        fbbox = fig.bbox
        dpi = fig.dpi
        spp = fig.subplotpars

        # set hspace/wspace to zeo
        hspace, wspace = spp.hspace, spp.wspace
        spp.hspace, spp.wspace = 0., 0.
        
        bottoms, tops, lefts, rights = gs.get_grid_positions(fig)

        # now calculate our bottom, top, left, right
        rowstart, rowstop = ss.rowspan[0], ss.rowspan[-1]
        colstart, colstop = ss.colspan[0], ss.colspan[-1]

        top = tops[rowstart]
        left = lefts[colstart]

        bottom = bottoms[rowstop]
        right = rights[colstop]

        # adjust edge box for figure padding
        if True:
            if rowstart == 0:
                top = 1.0
            if colstart == 0:
                left = 0
            if rowstop == nrows-1:
                bottom = 0.0
            if colstop == ncols-1:
                right = 1.0

        # restore hspace, wspace in subplotparms
        spp.hspace, spp.wspace = hspace, wspace

        bbox = Bbox([[left, bottom], [right, top]])

        return bbox


class Farm(GeeFarm):

    def __init__(self):

        super().__init__()

        # start a farm going
        carpet = Carpet()
        self.carpet = carpet

        clock = GuidoClock()

        shell = console.Console(farm=self, carpet=carpet, shepherd=self.shep)

        self.add_node(shell, background=True)
        self.add_node(carpet, background=True)

        self.add_node(self.shep)

        self.add(Params())
        self.add(clock)

        # connections
        #self.add_edge(carpet, hat)
        
        # sheperd looking after gfarm.hub, which it is itself part of.
        self.shep.set_flock(self.hub)

        # initial path this needs more thought - let's do it in start()
        self.shep.set_path([self.shep, self.carpet])


    def add(self, item):

        #self.add_edge(item, self.carpet)
        self.add_edge(self.carpet, item)

        

class Carpet(Ball):
    """ FIXME This should of course be in the magic module.
        I Can't remember why it needed to be here - probably worth
        moving it back there, but that requires making it magic!

        Current status: history just added, wormholes opened.

        FIXME: figure out lifecycle of an Axe

        generate_mosaic creates and adds to self.axes

        Need to be able to know:
             a. Axe has been handed out
             b. Axe has been shown
             c. Axe still in history
             d. geometry -- so we can spot Axe replacing another in same spot.
        
        Cases:  
            handed out, still in history == keep
            handed out, not in history, 

        Deletion:
            a. not in history
            b. has been handed out
            c. not in current image:  ie self.showing
    """
    def __init__(self):

        super().__init__()

        self.sleep = 0.01

        # grid related
        self.size = [1, 1]  # wibni Interact operations worked sanely here
        self.simple = False
        self.expanded = None
        self.output = None
        self.showing = {}

        self.history = deque(maxlen=random.randint(10, 20))

        self.axes = deque()
        self.lookup = dict()
        #self.savefig_dpi = 3000
        #self.image = plt.figure(constrained_layout=True, facecolor='grey')
        self.image = plt.figure()
        self.background = self.image.add_axes((0,0,1,1))
        try:
            plt.show(block=False)
        except:
            # sometimes backends have show without block parameter?  
            plt.show()

        # keyboard handling
        self.image.canvas.mpl_connect('key_press_event', self.keypress)

        # let's see everything
        #self.log_events()

        self.add_filter('+', self.more)
        self.add_filter('=', self.more)
        self.add_filter('-', self.less)
        self.add_filter('a', self.add_row)
        self.add_filter('c', self.add_column)

        self.add_filter('[', self.history_back)
        self.add_filter(']', self.history_forward)

        self.add_filter('S', self.save)
        self.add_filter('E', self.toggle_expand)
        self.add_filter('F', self.toggle_expand2)
        #self.add_filter(' ', self.toggle_pause)


    def log_events(self):

        events = [
            'button_press_event',
            'button_release_event',
            'draw_event',
            'key_press_event',
            'key_release_event',
            'motion_notify_event',
            'pick_event',
            'resize_event',
            'scroll_event',
            'figure_enter_event',
            'figure_leave_event',
            'axes_enter_event',
            'axes_leave_event',
            'close_event']

        connect = self.image.canvas.mpl_connect
        from functools import partial
                    
        for event in events:
            connect(event, partial(self.log_event, name=event))

    def log_event(self, event, name=None):

         print(name, event)

    def keypress(self, event):
        """ Take keypress events put them out there """

        #print('mosaic carpet handling', event)
        # use select here to get actual magic curio queue
        # where put can magically be a coroutine or a function according
        # to context.
        qq = self.select(event.key)
        qq.put_nowait(event)

    async def save(self):
        """ Save current image """
        self.image.savefig(f'carpet{datetime.datetime.now()}.png')
        #                   dpi=self.savefig_dpi)

    async def add_row(self):
        """ add a row to the mosaic """
        self.size[0] += 1
        await self.rebuild()
        
    async def add_column(self):
        self.size[1] += 1
        await self.rebuild()

    async def more(self):
        """ Show more pictures """
        self.size[0] += 1
        self.size[1] += 1
        await self.rebuild()

    async def less(self):
        """ Show fewer pictures """
        if self.size[0] > 1:
            self.size[0] -= 1
        if self.size[1] > 1:
            self.size[1] -= 1
        await self.rebuild()    

    async def rebuild(self):
        self.hideall()
        #self.generate_mosaic()

        print('replay history', len(self.history))

        await self.replay_history()

    def hideall(self):

        # hide everything currently being shown
        for key, ax in self.showing.items():
            ax.hide()
            
        self.showing.clear()

        # drain any axes waiting in self.axes
        for ax in self.axes:
            ax.figure.delaxes(ax.delegate)
        self.axes.clear()

    async def history_back(self):

        await self.history_rotate(-1)

    async def history_forward(self):

        await self.history_rotate(1)

    async def history_rotate(self, n=1):

        print('history', len(self.history), 'rotate', n)

        if len(self.history) == 0:
            return
        
        self.history.rotate(n)

        # we want to replace the current axes with the value we pop
        qq = self.select()

        pos = await self.get()
        ax = self.history.popleft()
        ax.position(pos)
        #ax.set_visible(True)

        if pos.delegate in self.image.axes:
            self.image.delaxes(pos.delegate)
        del pos

        ax.show()

    async def replay_history(self):

        # take a copy of the current history
        hlen = len(self.history)

        # need to throw away one axis in the queue
        await self.get()
        for hh in range(hlen):
            await self.history_rotate(1)
        
    def toggle_expand2(self):
        fig = self.image

        fig.subplots_adjust(hspace=0, wspace=0)
        
    def toggle_expand(self, names=None):
        
        names = names or ["left", "bottom", "right", "top", "wspace", "hspace"]

        fig = self.image
        if not self.expanded:

            self.expanded = {}
            for name in names:
                self.expanded[name] = getattr(fig.subplotpars, name)
            
            rc('image', aspect='auto')

            fig.subplots_adjust(
               left=0, right=1,
               bottom=0, top=1,
               hspace=0, wspace=0)
        else:
            print(self.expanded)
            fig.subplots_adjust(**self.expanded)
            self.expanded = None
        
    async def poll(self):
        """ Gui Loop """

        # Experiment with sleep to keep gui responsive
        # but not a cpu hog.
        event = 0

        nap = 0.05
        canvas = self.image.canvas
        while True:
            #print('RUNNING EVENT LOOP')
            
            canvas.flush_events()
            canvas.start_event_loop(self.sleep)

            await magic.sleep(self.sleep * 10)

    async def start(self):
        
            
        # start some tasks to keep things ticking along
        #watch_task = await curio.spawn(self.watch())
        print("carpet starting tasks")
        poll_task = magic.spawn(self.poll())
        print('POLL TASK SPAWNED')
        self.tasks = [poll_task]
        print("DONE STARTED carpet")

    def generate_mosaic(self):

        # first try and delete some stuff
        self.delete_old_axes()

        # set up the square mosaic for current size
        mosaic = []
        mosaic = np.arange(self.size[0] * self.size[1])
        mosaic = mosaic.reshape(*self.size)

        keys = dict(visible=False)

        picture = self.image.subplot_mosaic(mosaic, subplot_kw=keys)

        for key, ax in picture.items():
            ax.meta = dict(key=key)
            axe = Axe(ax, self)
            self.axes.append(axe)
            self.lookup[id(ax)] = axe

    def delete_old_axes(self):

        naxes = len(self.image.axes)

        showing = self.showing.values()
        for ax in self.image.axes:
            if ax is self.background:
                continue

            try:
                axe = self.lookup[id(ax)]
            except:
                print(f'WHOA {id(ax)} {type(ax)} missing from lookup')
                raise

            if (axe not in self.history and
                axe not in showing and
                hasattr(axe, 'img')):
                
                axe.img.remove()
                ax.figure.delaxes(ax)
                del self.lookup[id(ax)]
                del ax


    async def run(self):
        # nobody waiting for axes, don't add to the queue
        if self.select().qsize() > 0:
            return

        if not self.axes:
            self.generate_mosaic()
            
        axe = self.axes.popleft()
        if self.simple:
            axe.simplify()
            axe.grid(True)
        await self.put(axe)


    def get_axe_geometry(self, axe):

        return axe.get_subplotspec().get_geometry()

    def show(self, axe):

        gg = self.get_axe_geometry(axe)

        if gg in self.showing:
            tohide = self.showing[gg]
            #print(f'Showing {id(tohide)} {tohide.get_visible()}')
            if tohide is not axe:
                tohide.hide()

        self.history.appendleft(axe)
        
        self.showing[gg] = axe

        self.image.canvas.draw_idle()
        

    def hide(self, axe):

        if axe.get_visible():
            axe.set_visible(False)


# example below ignore for now
class MagicPlot(Ball):
    """ Use a Ball to plot.
    
    FIXME: make this one more interesting.
    """
    def __init__(self):

        super().__init__()

        self.add_filter('a', self.add)
               
    async def add(self):
        """ Magic Plot key demo  """
        print('magic key was pressed')

        # now what to add?
        return math.pi + math.e

    async def start(self):

        print('magic plot started')
        self.fig = figure.Figure()
        self.ax = self.fig.add_subplot(111)

    async def run(self):

        ax = await self.get()
        ax.clear()
        data = np.random.randint(50, size=100)
        ax.plot(data)

        ax.show()


            
def run(farm=None, dump=False):

    if farm is None:
        farm = Farm()

        magic_plotter = MagicPlot()
        farm.add(magic_plotter)
        farm.shep.path.append(magic_plotter)

    print('set up the farm .. move to start for added thrills? or not?') 
    #farm.setup()

    if dump:
        print()
        print('DUMP')
        farm.dump()

    magic.run(start_and_run(farm))  

async def start_and_run(farm):

    print('starting farm')
    await farm.start()

    print('running farm')
    runner = await farm.run()

        
if __name__ == '__main__':
    
    
    run()
