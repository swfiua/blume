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


class Farm(GeeFarm):

    def __init__(self):

        super().__init__()

        # start a farm going
        carpet = Carpet()
        self.carpet = carpet

        clock = GuidoClock()

        self.add_node(carpet, background=True, hat=True)

        self.add_node(self.shep)

        #self.add(clock)

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

        self.history = deque(maxlen=random.randint(20, 50))

        self.axes = {}
        self.showing = {}

        #width, height = ball.width, ball.height
        self.image = plt.figure()
        self.generate_mosaic()
        plt.show(block=False)

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
        self.dump_roundabout()
        qq = self.select('keys')
        qq.put(event.key)
        print(qq.qsize(), id(qq))
        

    async def save(self):
        """ Save current image

        This one saves the current data, not the PIL file
        so can be used to make transforms along the way.
        """
        self.image.save(f'carpet{datetime.datetime.now()}.png')
        
    async def more(self):
        """ Show more pictures """
        self.size += 1
        self._update_pos()
        self.hideall()
        self.generate_mosaic()
        await self.rewind_history()

        print(f'more {self.size}')

    async def less(self):
        """ Show fewer pictures """
        if self.size > 1:
            self.size -= 1
        self._update_pos()
        self.hideall()
        self.generate_mosaic()
        await self.rewind_history()
        print(f'less {self.size}', id(self))

    def hideall(self):

        for ax in self.axes.values():
            ax.set_visible(False)

    async def history_back(self):

        await self.history_rotate(1)

    async def history_forward(self):

        await self.history_rotate(-1)

    async def history_rotate(self, n=1):

        if len(self.history) == 0:
            return
        
        self.history.rotate(n)

        # we want to replace the current axes with the value we pop
        ax = self.history.pop()

        await self.add_axis(ax)

    async def add_axis(self, nax):

        self._update_pos()

        fig = self.image
        ax = self.axes[self.pos]

        self.axes[self.pos] = nax
        
        print(nax, 'NNNNN')
        nax.set_subplotspec(ax.get_subplotspec())

        print(fig.axes)
        if ax in fig.axes:
            fig.delaxes(ax)
        else:
            print(ax, 'AWOL')
            
        fig.add_subplot(nax)

        ax.set_visible(False)
        nax.set_visible(True)

        nax.draw_artist(nax)


    async def rewind_history(self):

        for ax in self.history:
            await self.add_axis(ax)

        print('axes after rewind', self.image.axes)
            
    async def poll(self):
        """ Gui Loop """

        # Experiment with sleep to keep gui responsive
        # but not a cpu hog.
        event = 0

        nap = 0.05
        canvas = self.image.canvas
        while True:
            
            canvas.draw_idle()
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

        keys = dict(visible=True)
        self.axes = self.image.subplot_mosaic(mosaic, subplot_kw=keys)
        # hide all the axes
        #for ax in self.axes.values():
        #    ax.set_visible(False)

        print(self.axes)
        print('III', id(self.image), self.image.axes)
        #self.image.clear()

    async def run(self):

        ax = self.axes[self.pos]

        # nobody waiting for axes, don't add to the queue
        if self.select().qsize() > 0:
            return

        # fade to this new axis, give a chanc for something to draw
        await self.fade(ax)

        self.history.append(ax)

        self._update_pos()

    async  def fade(self, ax):
        """ Fade in new axis ?"""

        pos = self.pos
        if pos not in self.showing:
            # just make ax visible
            ax.set_visible(True)
            self.showing[pos] = ax
            return

        # hand out the axis
        await self.put(ax)

        # give it a chance for something to take it
        await curio.sleep(0.1)
        
        # ok so need to fade from what's in showing to ax
        ax.set_visible(True)
        
        #await curio.sleep(0.1)

        # this needs a re-think, self.pos might have changed
        if pos in self.showing:
            print('hiding', pos)
            self.showing[pos].set_visible(False)

        # record what's now showing
        self.showing[pos] = ax
        

    def _update_pos(self):

        self.pos += 1
        if self.pos >= self.size * self.size:
            self.generate_mosaic()
            self.pos = 0
    


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
