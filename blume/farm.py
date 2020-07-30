"""
Split the farm from magic.

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

from .teakhat import Hat, Help

from .magic import Ball, RoundAbout, GeeFarm, fig2data, Shepherd, canine
from .mclock2 import GuidoClock


class Farm(GeeFarm):

    def __init__(self):

        super().__init__()

        # start a farm going
        hat = Hat()
        carpet = Carpet()
        self.carpet = carpet

        clock = GuidoClock()

        self.add_node(carpet, background=True)

        self.add_node(hat, hat=True)

        self.add(self.shep)

        self.add(clock)

        # connections
        self.add_edge(carpet, hat)
        
        # sheperd looking after gfarm.hub, which it is itself part of.
        self.shep.set_flock(self.hub)

        # initial path this needs more thought
        self.shep.set_path([self.shep, self.carpet])


    def add(self, item):

        self.add_edge(item, self.carpet)
        

class Carpet(Ball):
    """ FIXME This should of course be in the magic module.
        I Can't remember why it needed to be here - probably worth
        moving it back there, but that requires making it magic!

        Current status: history just added, wormholes opened.
    """
    def __init__(self):

        super().__init__()

        self.sleep = 0

        # grid related
        self.size = 1
        self.pos = 0

        self.history = deque(maxlen=random.randint(20, 50))

        self.image = None

        self.add_filter('+', self.more)
        self.add_filter('=', self.more)
        self.add_filter('-', self.less)
        self.add_filter('S', self.save)

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
        self.image = None
        await self.rewind_history()
        print(f'more {self.size}')

    async def less(self):
        """ Show fewer pictures """
        if self.size > 1:
            self.size -= 1
        self._update_pos()
        self.image = None
        await self.rewind_history()
        print(f'less {self.size}', id(self))


    async def rewind_history(self):
        
        while len(self.history):
            await self.put(self.history.popleft(), 'stdin')

    async def start(self):
        
        pass

    async def erun(self):
        """ Run the farm forever """

        # loop forever, calling self.arun()
        while True:

            await self.arun()

    async def run(self):

        # hmm. need to re-think what belongs where
        # also maybe this method is "runner" and "run" is just
        # the inner loop?


        print('carpet waiting on ball')
        ball = await self.get()
        if ball is None:
            print('carpet got no ball')
            return

        print('carpet got ball')

        sz = self.size

        if self.image is None:
            qq = self.select('stdin')

            width, height = ball.width, ball.height
            self.image = Image.new(mode='RGB', size=(width * sz, height * sz))

        width = int(self.image.width / sz)
        height = int(self.image.height / sz)

        #print('WWW', width, ball.width)
        #print('HHH', height, ball.height)

        # now paste current image in according to self.pos and size
        ps = self.pos
        self._update_pos()
        xx = ps // self.size
        yy = ps % self.size
        offx = xx * width
        offy = yy * height
        self.image.paste(ball.resize((width, height)),
                         (offx,  offy, offx + width, offy + height))

        # put out in queue for displays
        await self.put(self.image)

        self.history.append(ball)
        

    def _update_pos(self):

        self.pos += 1
        if self.pos >= self.size * self.size:
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


            
async def run():


    farm = Farm()

    magic_plotter = MagicPlot()
    farm.add(magic_plotter)

    print('set up the farm .. move to start for added thrills? or not?') 
    #farm.setup()

    print()
    print('DUMP')
    farm.dump()


    print('starting farm')
    await farm.start()

    print('running farm')
    runner = await farm.run()

    
        
if __name__ == '__main__':
    
    
    curio.run(run(), with_monitor=True)
