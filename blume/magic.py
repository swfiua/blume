"""
Matplotlib plus async


mainloop()

queues of images

clients set up their own queues

draw from Q

Going round in ever decreasing circles.  

The idea is there is some sort of calculation going on that generates grids of
numbers.

You want to see what is going on without grinding the calculations to a halt.

At the same time, the more you explore the dyata with plots (thanks matplotlib)
the more questions appear.

Often the calculation has a number of parameters, or a selection of data
streams on which it could be run.

So my code sprouts command line arguments and then the simple U/I might allow
me to control more of the parameters.

This module aims to provide a small number of components to help asynchronous
data exploration and graphical monitoring of data processing pipelines.

It is particularly focussed on global climate data that typically comes in a
lat/lon grid of values.

Internals?
==========

I have gone with Tk because it is usually around and I don't need much here.

But I will be thinking about raspberry pi's with sense hats and a mini joy
stick too.

All the user interface and display handling are ultimately done by the
EventLoop object, so a place to start when thinking beyond the current.

For in put the focus is very much on keyboard, so things should work well with
anything that can create a stream of key characters.

I am also using David Beazeley's *curio* module to help me use python3.6+ async
features.  

I am starting off here with some pieces from my project *karmapi*.  

So there will be Pig Farms, Piglets and widgets all mixed up for a while.

Objects with a start and run.

Some writing to queues where viewers are polling.

"""
import random

import math

import io

from pathlib import Path

from collections import deque, defaultdict, Counter

import curio

import numpy as np

from PIL import Image

import matplotlib

from matplotlib import figure

from matplotlib import pyplot as plt

import networkx as nx


class Ball:
    
    def __init__(self):

        self.paused = False
        self.sleep = .1

        # let roundabouts deal with connections
        self.radii = RoundAbout()

        # ho hum update event_map to control ball?
        # this should be done via roundabout,
        # let shepherd control things?
        self.event_map = dict(
            s=self.sleepy,
            w=self.wakey)
        self.event_map[' '] = self.toggle_pause

    async def sleepy(self):
        """ Sleep more between updates """
        self.sleep *= 2
        print(f'sleepy {self.sleep}')

    async def wakey(self):
        """ Sleep less between updates """
        self.sleep /= 2
        print(f'wakey {self.sleep}')

    async def toggle_pause(self):
        """ Toggle pause flag """
        print('toggle pause')
        self.paused = not self.paused

    async def get(self, name='stdin'):

        return await self.radii.get(name)

    async def put(self, data, name='stdout'):

        return await self.radii.put(data, name)

    async def start(self):
        pass

    async def run(self):
        pass


class GeeFarm(Ball):
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
        self.hub = hub or nx.DiGraph()

        self.hub.add_nodes_from(nodes or set())
        self.hub.add_edges_from(edges or set())

        self.shep = Shepherd()


    def __getattr__(self, attr):
        """ Delegate to hub
        """
        return getattr(self.hub, attr)
        

    def dump(self):

        print(f' nodes: {self.hub.number_of_nodes()}')
        print(f' edges: {self.hub.number_of_edges()}')

        hub = self.hub
        for item in hub.nodes:
            print('degree', hub.degree[item], hub[item])

        for edge in hub.edges:
            print(edge, hub.edges[edge])

    async def start(self):
        """ Traverse the graph do some plumbing? 

        Let the shepherd look after the components
        """
        for component in nx.connected_components(nx.to_undirected(self)):
            print('Component', component)
            print(type(component))
            # get the shepherd to manage the component
            self.shep.add(component)
    
    async def run(self):
        """ Run the farm 

        For now, just plot the current graph.
        """
        print('MAGIC TREE FARM')

        # delegated to hub
        fig = plt.figure()
        nx.draw(self.hub)

        await self.put(fig2data(plt))
        print('qsize', self.outgoing.qsize())

def fig2data(fig):
    """ Convert a Matplotlib figure to a PIL image.

    fig: a matplotlib figure
    return: PIL image

    FIXME? return numpy array of image pixels?
    """

    facecolor = 'black'
    #facecolor = 'white'
    if hasattr(fig, 'get_facecolor'):
        facecolor = fig.get_facecolor()
        print('facecolor', facecolor)

    # no renderer without this
    image = io.BytesIO()
       
    fig.savefig(image, facecolor=facecolor, dpi=200)

    return Image.open(image)


class RoundAbout:
    """ 
    A magic queue switch.

    Processes waiting on something.

    Input from queues.

    Balls, outputs, inputs.

    Of course, the round about is a ball.

    Time for bed, said zebedee 
    """
    def __init__(self):

        self.qs = {}
        self.infos = defaultdict(set)
        self.add_queue()
        self.counts = Counter()
        self.filters = defaultdict(dict)

    def select(self, name=None, create=True):
        """ pick a q 
        
        create: if True, create if missing
        """
        qq = self.qs.setdefault(name)
        if qq is None:
            if create:
                qq = self.add_queue(name)
            else:
                raise ValueError(f'no queue for {name}')

        return qq

    async def put(self, value, name='stdout'):

        self.counts.update([('put', name)])
        await self.select(name).put(value)

    async def get(self, name='stdout'):

        self.counts.update([('get', name)])
        await self.select(name).get()

    def status(self):

        result = {}
        results['counts'] = self.counts
        
        for qname, qq in self.qs():
            result[qname] = qq.qsize()

        return result

    def add_filter(self, key, coro, name='stdin'):

        self.filters[name][key] = coro

    async def tend(self, queue=None, name=None, coro=None):
        """ A co-routine to mind a queue and pass stuff on to another """

        queue = queue or self.select(name)

        print('TENDING', name, coro)

        while True:
            event = await queue.get()

            await coro(event)

    async def dispatch(self, name, maps):
        """ Assume maps is a dictionary which 
        
        maps inputs to coroutines.
        """
        queue = queue or self.select(name)

        # nested co-routine to bind queue
        async def watch():

            event = await queue.get()
            if event in maps:
                result = await maps[event]()

                
        return await self.tend(coro=watch, queue=queue)
        


    def add_queue(self, name=None):

        qq = curio.UniversalQueue()
        self.qs[name] = qq

        return qq


    async def tee(self, ink, outs):
        """ Pass data on  

        Idea for here: relays.
        """
        while True:
            event = await ink.get()
            #print('hat stand event', event)
            for out in outs:
                await out.put(event)
    

    async def start(self):
        """ How do you start a magic round-a-bout? """
        pass

    async def run(self):
        """ Run the magic roundabout """

        # create an image to show what is going on?
        pass


class Shepherd(Ball):
    """ Watches things nobody else is watching """

    def __init__(self):

        super().__init__()

        self.flocks = []

    def set(self, flock):
        """  Add a flock to be watched """
        self.flock = flock

    async def whistle(self, key, name=None):
        """ send out a message 
        
        follow the graph to see who's interested

        feels like this should be some sort of broadcast

        or perhaps directional if there's a name?

        or just send it to anything with an ear?
        """
        for flock in self.flocks



    async def start(self):
        
        for flock in self.flocks:
            # make sure the roundabouts for the flock are suitably connected
            pass

            # see what inputs and outputs are missing
            pass

    async def run(self):
        """ Check the flocks """
        

        print(self.radii)

        # pick a random input and wait on it?
        self.flock = random.choice(self.flocks)
        print(self.flock)
        

    def ins_and_outs(self):
        """ Ins and outs based connections 

        This back from Farm -- may be of use for
        roundabout merging.
        """
        ins = defaultdict(set)
        outs = defaultdict(set)
        
        for flock in self.flocks:

            if hasattr(node, 'ins'):
                for item in node.ins:
                    ins[item].add(node)

            if hasattr(node, 'outs'):
                for item in node.outs:
                    outs[item].add(node)

        print(ins)
        print(outs)

        # ok. now ins and outs have who has what
        for key in ins.keys():
            if key in outs:
                for out in outs[key]:
                    for item in ins[key]:
                        if out is not item:
                            self.add_edge(out, item, name=key)
                        
        inks = set(ins.keys())
        oinks = set(outs.keys())
        for key in oinks - inks:
            for node in outs[key]:
                print(f'{node} has output nobody wants: {key}')
                self.add_edge(node, self.shep, name=key)
                self.shep.ins.add(key)

        for key in inks - oinks:
            for node in ins[key]:
                print(f'{node} wants input nobody has: {key}')
                self.add_edge(self.shep, node, name=key)
                self.shep.outs.add(key)


    def __str__(self):

        return f'shepherd of ins and outs'
            
    

async def run():

    radii = RoundAbout()

    print('do something with roundabouts and GeeFarms')
    start = await radii.start()
    runner = await radii.run()


if __name__ == '__main__':
    
    
    curio.run(run())
