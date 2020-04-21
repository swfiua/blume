"""
Split the farm from magic.

"""
import random

import math

import io

from pathlib import Path

from collections import deque, defaultdict

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
    """ Connections to the outside world """

    def __init__(self):

        super().__init__()

        # start the farm going
        hat = Hat()
        carpet = Carpet()
        self.carpet = carpet
        clock = GuidoClock()

        self.add(carpet, with_carpet=False)

        self.add(self.shep)
        self.add(hat, hat=True)

        # sheperd looking after gfarm.hub, which it is itself part of.
        self.shep.set_flock(self.hub)

        # initial path this needs more thought
        self.shep.set_path([self.shep])

        # mapping of events to co-routines

        # register quit event with shepherd
        self.shep.add_filter('q', self.quit)

        self.add(clock)

        
    def status(self):

        self.show()


    def add(self, item, run=True, with_carpet=True, hat=False):

        self.add_node(item, background=run, hat=hat)
        if with_carpet:
            self.add_edge(item, self.carpet)
        

    async def start(self):
        """ Start the farm running 
        
        This should do any initialisation that has to
        wait for async land.
        """
        print('starting shepherd')
        await self.shep.start()

            
    async def quit(self):
        """ quit the farm """

        await self.quit_event.set()


    async def run(self):

        # using a dog to run the shepherd, this makes no  sense
        # let's wait and see what happens
        print('Waiting for shepherd dog watching shepherd ')
        await curio.spawn(canine(self.shep))
        #return

        
        print('Farm starting to run')
        self.quit_event = curio.Event()

        # select next node
        await self.quit_event.wait()

        await self.shep.quit()

        print('over and out')



class Carpet(Ball):

    def __init__(self):

        super().__init__()

        # grid related
        self.size = 1
        self.pos = 0

        self.image = None

        self.add_filter('m', self.more)
        self.add_filter('l', self.less)

        
    async def more(self):
        """ Show more pictures """
        self.size += 1
        self._update_pos()
        self.image = None
        print(f'more {self.size}')

    async def less(self):
        """ Show fewer pictures """
        if self.size > 1:
            self.size -= 1
        self._update_pos()
        self.image = None
        print(f'less {self.size}', id(self))


    async def start(self):
        
        pass

    async def run(self):
        """ Run the farm forever """

        # loop forever, calling self.arun()
        while True:

            await self.arun()

    async def arun(self):

        # hmm. need to re-think what belongs where
        # also maybe this method is "runner" and "run" is just
        # the inner loop?
        ball = await self.get()
        
        if ball is None:
            print('carpet got no ball')
            return
        
        sz = self.size

        if self.image is None:
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

        #print('displayed ball', ball.width, ball.height)


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
    clock = GuidoClock()
    farm.add(magic_plotter)
    farm.add(clock)

    print('set up the farm .. move to start for added thrills? or not?') 
    #farm.setup()

    print()
    print('DUMP')
    farm.dump()


    fstart = await curio.spawn(farm.start())

    print('farm running')
    runner = await farm.run()

    
        
if __name__ == '__main__':
    
    
    curio.run(run(), with_monitor=True)
