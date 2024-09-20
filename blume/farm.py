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
import sys

import inspect

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

from matplotlib import figure, rc

from matplotlib import pyplot as plt

from blume import magic, console
from .magic import Ball, RoundAbout, Shepherd, Carpet, spawn

from .mclock2 import GuidoClock
from .rcparms import Params
from .console import Console


class Farm(Ball):
    """ A farm, for now.. 

    A network of things running around.

    Magic round-abouts of queues connecting it all.

    Displays, keyboards, human input, outputs.

    A graph of tools.

    And something to help it run.
    """

    def __init__(self, hub=None, nodes=None, edges=None):
        """ Turn graph into a running farm """
        super().__init__()
        self.pause = True
        hub = hub or DiGraph()

        hub.add_nodes_from(nodes or set())
        hub.add_edges_from(edges or set())

        print('OK to here')
        self.hub = hub
        self.shep = Shepherd()

        # register quit event with shepherd
        self.shep.add_filter('q', self.quit)
        print('OK to here2')

        # start a farm going
        carpet = Carpet()
        self.carpet = carpet

        clock = GuidoClock()

        self.shell = console.Console(
            farm=self,
            carpet=carpet,
            shepherd=self.shep,
            tmra=magic.TheMagicRoundAbout,
        )

        #background = sys.platform != 'emscriptem'
        background = True
        self.add_node(self.shell, background=background)
        self.add_node(carpet, background=True)

        self.add_node(self.shep)

        #self.add(Params())
        self.add(clock)

        # connections
        #self.add_edge(carpet, hat)
        
        # sheperd looking after gfarm.hub, which it is itself part of.
        self.shep.set_flock(self.hub)

        # initial path this needs more thought - let's do it in start()
        self.shep.set_path([self.shep, self.carpet])
        self.shep.carpet = carpet


        

    def __getattr__(self, attr):
        """ Delegate to hub

        self.hub is a directed graph, so we're a Ball that is a graph
        """
        #print(f'farm looking for {attr}')
        if attr == 'hub':
            raise AttributeError
        return getattr(self.hub, attr)

    def status(self):

        print(f' nodes: {self.hub.number_of_nodes()}')
        print(f' edges: {self.hub.number_of_edges()}')

        hub = self.hub
        for item in hub.nodes:
            print(hub[item])

        for edge in hub.edges:
            print(edge, hub.edges[edge])

    def add(self, item):

        #self.add_edge(item, self.carpet)
        self.add_edge(self.carpet, item)

    async def start(self):
        """ Traverse the graph do some plumbing? 

        Let the shepherd look after the running of everything
        """

        # Tell the shepherd what to look after
        self.shep.flock = self.hub

        print('GEEEFAR starting shep')
        result = self.shep.start()
        if inspect.iscoroutine(result):
            await result

        # create a task which is a dog watching the shepherd
        print('GEEEFAR spawning superdog')
        self.superdog = spawn(magic.canine(self.shep))

        # set the shepherd to pause 
        self.shep.pause = True

        # figure out an initial path
        await self.shep.show_help()


    async def run(self):
        """ Run the farm 

        For now, just plot the current graph.
        """
        print('MAGIC TREE FARM')

        # wait for the super dog
        try:
            await self.superdog

        except asyncio.CancelledError:
            print('Farm shutting down')


    async def quit(self):
        """ quit the farm """

        await self.shep.quit()

        self.superdog.cancel()


class DiGraph:

    def __init__(self):

        self.nodes = defaultdict(dict)
        self.edges = defaultdict(dict)

    def add_nodes_from(self, nodes):

        for node in nodes:
            self.add_node(node)

    def add_edges_from(self, edges):

        for edge in edges:
            self.add_edge(*edge)

    def add_node(self, node, **keyw):

        self.nodes[node].update(**keyw)
    
    def add_edge(self, a, b, **keyw):
        
        self.edges[(a, b)].update(**keyw)
        for node in a, b:
            if node not in self.nodes:
                self.nodes[node].update(**keyw)

    def succcessors(self, node):

        result = []
        for a, b in self.edges.keys():
            if a is node:
                result.append(b)

    def predecessors(self, node):

        result = []
        for a, b in self.edges.keys():
            if b is node:
                result.append(a)

    def __iter__(self):

        return iter(self.nodes)

    def __len__(self):

        return len(self.nodes)




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


            

async def start_and_run(farm):

    print('starting farm')
    await farm.start()

    print('running farm')
    runner = await farm.run()

        
def run(farm=None, balls=None, dump=False):

    """ Start a Farm running

    balls: list of balls to add to the farm

    farm: existing farm, new one is created for you.
    """
    if farm is None:
        farm = Farm()

        if balls is None:
            balls = MagicPlot()

        try:
            balls = iter(balls)
        except TypeError:
            balls = [balls]         # cope with single ball

        for ball in balls:
            farm.add(ball)

    print('set up the farm .. move to start for added thrills? or not?') 
    #farm.setup()

    if dump:
        print()
        print('DUMP')
        farm.dump()

    magic.run(start_and_run(farm))  


if __name__ == '__main__':
    
    
    run()
