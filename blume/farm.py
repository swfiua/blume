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

import curio

import numpy as np

from PIL import Image

import matplotlib

from matplotlib import figure

from matplotlib import pyplot as plt

import networkx as nx

#from .mosaic import Carpet

from .magic import Ball, RoundAbout, GeeFarm, fig2data, Shepherd, canine
from .mclock2 import GuidoClock
from .rcparms import Params
from .blitting import BlitManager

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
        self.set_subplotspec(target.get_subplotspec())

    def show(self):
        """ Show the axes """
        self.set_visible(True)
        self.carpet.show(self)

    def hide(self):
        """ Hide the axes """
        self.set_visible(False)
        #self.carpet.hide(self)

    def please_draw(self):
        """ Try to force a draw of the axes """
        self.draw_artist(self)

    def projection(self, name):
        """ Set the projection 

        Not sure if this is possible.
        """
        ax = self.delegate
        parms = dict(projection=name, visible = False)

        pax = ax.figure.subplots(subplot_kw=parms)

        self.delegate = pax
        self.position(ax)


    def simplify(self):

        self.xaxis.set_visible(False)
        self.yaxis.set_visible(False)
        

class Farm(GeeFarm):

    def __init__(self):

        super().__init__()

        # start a farm going
        carpet = Carpet()
        self.carpet = carpet

        clock = GuidoClock()

        self.add_node(carpet, background=True, hat=True)

        self.add_node(self.shep)

        self.add(clock)
        self.add(Params())

        # connections
        #self.add_edge(carpet, hat)
        
        # sheperd looking after gfarm.hub, which it is itself part of.
        self.shep.set_flock(self.hub)

        # initial path this needs more thought
        self.shep.set_path([self.shep, self.carpet])


    def add(self, item):

        #self.add_edge(item, self.carpet)
        self.add_edge(self.carpet, item)
        

class Carpet(Ball):
    """ FIXME This should of course be in the magic module.
        I Can't remember why it needed to be here - probably worth
        moving it back there, but that requires making it magic!

        Current status: history just added, wormholes opened.
    """
    def __init__(self):

        super().__init__()

        self.sleep = 0.01

        # grid related
        self.size = 1
        self.pos = 0
        self.simple = False

        self.history = deque(maxlen=random.randint(20, 50))

        self.axes = {}

        #width, height = ball.width, ball.height
        self.image = plt.figure(constrained_layout=True, facecolor='grey')
        plt.show(block=False)
        self.bm = BlitManager(self.image.canvas)

        # keyboard handling
        self.image.canvas.mpl_connect('key_press_event', self.keypress)

        self.add_filter('+', self.more)
        self.add_filter('=', self.more)
        self.add_filter('-', self.less)

        self.add_filter('[', self.history_back)
        self.add_filter(']', self.history_forward)

        self.add_filter('S', self.save)

    def keypress(self, event):
        """ Take keypress events put them out there """

        #print('mosaic carpet handling', event)
        # use select here to get actual magic curio queue
        # where put can magically be a coroutine or a function according
        # to context.
        print('key press event', event, event.key)
        qq = self.select('keys')
        qq.put(event.key)


    async def save(self):
        """ Save current image

        This one saves the current data, not the PIL file
        so can be used to make transforms along the way.
        """
        self.image.savefig(f'carpet{datetime.datetime.now()}.png')
        
    async def more(self):
        """ Show more pictures """
        self.size += 1
        self.pos = 0
        self.hideall()
        self.generate_mosaic()
        self.bm.clear()
        await self.replay_history()


    async def less(self):
        """ Show fewer pictures """
        if self.size > 1:
            self.size -= 1
        self.pos = 0
        self.hideall()
        self.generate_mosaic()
        self.bm.clear()
        await self.replay_history()

    def hideall(self):

        for ax in self.image.axes:
            print('hiding', type(ax), id(ax))
            ax.set_visible(False)


    async def history_back(self):

        await self.history_rotate(1)

    async def history_forward(self):

        await self.history_rotate(-1)

    async def history_rotate(self, n=1):

        print('history', len(self.history), 'rotate', n)

        if len(self.history) == 0:
            return
        
        self.history.rotate(n)

        # we want to replace the current axes with the value we pop
        for axx in self.history:
            print('hist', axx.title)

        ax = self.history.popleft()
        print('popping', ax.title)
        #self.hideall()
        pos = await self.get()

        ax.position(pos)
        ax.show()
        print("history len", len(self.history))

        self.image.delaxes(pos.delegate)
        self._update_pos()

    async def add_axis(self, nax):

        self.bm.add_artist(nax)
        self.bm.update()
        return

        fig = self.image
        ax = self.axes[self.pos]

        self.axes[self.pos] = nax
        
        # set the sublotspec to match the one we are replacing
        nax.position(ax)

        # hide the old axis
        ax.hide()

        nax.show()
        
    async def replay_history(self):

        # take a copy of the current history
        hlen = len(self.history)

        for hh in range(hlen):
            self.history.rotate()
        
            
    async def poll(self):
        """ Gui Loop """

        # Experiment with sleep to keep gui responsive
        # but not a cpu hog.
        event = 0

        nap = 0.05
        canvas = self.image.canvas
        while True:
            
            #canvas.draw_idle()
            canvas.flush_events()
            canvas.start_event_loop(self.sleep)

            # Would be good to find a Tk file pointer that
            # can be used as a source of events

            await curio.sleep(self.sleep * 10)

    async def start(self):
        
            
        # start some tasks to keep things ticking along
        #watch_task = await curio.spawn(self.watch())
        print("carpet starting tasks")
        poll_task = await curio.spawn(self.poll())

        self.tasks = curio.TaskGroup([poll_task])
        print("DONE STARTED carpet")

    def generate_mosaic(self):

        # set up the square mosaic for current size
        mosaic = []
        mosaic = np.arange(self.size * self.size)
        mosaic = mosaic.reshape((self.size, self.size))

        # position within the mosaic
        self.pos = 0

        print(mosaic)

        # first hide existing axes
        #for ax in self.axes.values():
        #    ax.set_visible(False)

        keys = dict(visible=False)

        picture = self.image.subplot_mosaic(mosaic, subplot_kw=keys)

        for key, ax in picture.items():
            axe = Axe(ax, self)
            if self.simple:
                axe.simplify()
                axe.grid(True)
            axe.meta = dict(key=key)
            self.axes[key] = axe

        self.bm.filter(self.axes.values())
        #self.image.clear()

        #assert len(self.image.axes) == self.size * self.size

    async def run(self):

        # nobody waiting for axes, don't add to the queue
        if self.select().qsize() > 0:
            return

        if not self.axes:
            self.generate_mosaic()
            self.pos=0
            
        ax = self.axes[self.pos]

        # put out the axis
        await self.put(ax)

        self._update_pos()
        

    def _update_pos(self):

        self.pos += 1
        if self.pos >= self.size * self.size:
            self.generate_mosaic()

    def show(self, axe):

        axe.set_visible(True)
        self.history.appendleft(axe)

        self.bm.add_artist(axe)
        self.bm.update()
        
        
    def hide(self, axe):

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

        ax = self.ax
        ax.clear()
        data = np.random.randint(50, size=100)
        ax.plot(data)

        await self.put(fig2data(self.fig))


            
def run(farm=None, dump=False):

    if farm is None:
        farm = Farm()

        magic_plotter = MagicPlot()
        farm.add(magic_plotter)

    print('set up the farm .. move to start for added thrills? or not?') 
    #farm.setup()

    if dump:
        print()
        print('DUMP')
        farm.dump()

    curio.run(start_and_run(farm))  

async def start_and_run(farm):

    print('starting farm')
    await farm.start()

    print('running farm')
    runner = await farm.run()

        
if __name__ == '__main__':
    
    
    run()
