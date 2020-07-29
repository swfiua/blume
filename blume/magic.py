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

import sys

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
        self.sleep = .3

        # let roundabouts deal with connections
        self.radii = RoundAbout()

        # ho hum update event_map to control ball?
        # this should be done via roundabout,
        # let shepherd control things?
        self.radii.add_filter('s', self.sleepy)
        self.radii.add_filter('w', self.wakey)
        self.radii.add_filter(' ', self.toggle_pause)
        self.radii.add_filter('i', self.interact)


    def __getattr__(self, attr):
        """ Delegate to roundabout
        """
        return getattr(self.radii, attr)

    async def interact(self):

        from pprint import pprint
        pprint(vars(self))
        

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
        self.pause = True
        self.hub = hub or nx.DiGraph()

        self.hub.add_nodes_from(nodes or set())
        self.hub.add_edges_from(edges or set())

        self.shep = Shepherd()

        # register quit event with shepherd
        self.shep.add_filter('q', self.quit)


    def __getattr__(self, attr):
        """ Delegate to hub

        self.hub is a directed graph, so we're a Ball that is a graph
        """
        return getattr(self.hub, attr)

    def status(self):

        print(f' nodes: {self.hub.number_of_nodes()}')
        print(f' edges: {self.hub.number_of_edges()}')

        hub = self.hub
        for item in hub.nodes:
            print(hub[item])

        for edge in hub.edges:
            print(edge, hub.edges[edge])

    async def start(self):
        """ Traverse the graph do some plumbing? 

        Let the shepherd look after the running of everything
        """

        # Tell the shepherd what to look after
        self.shep.flock = self.hub

        print('starting shep')
        await self.shep.start()

        # create a task which is a dog watching the shepherd
        self.superdog = await curio.spawn(canine(self.shep))
        print('start superdog', self.superdog)
        await self.shep.toggle_pause()


    async def run(self):
        """ Run the farm 

        For now, just plot the current graph.
        """
        print('MAGIC TREE FARM')

        # wait for the super dog
        await self.superdog.wait()

    async def quit(self):
        """ quit the farm """

        await self.superdog.cancel()



def fig2data(fig):
    """ Convert a Matplotlib figure to a PIL image.

    fig: a matplotlib figure
    return: PIL image

    There has to be an easier way to do this.

    FIXME -- turning matplotlib figures into PIL or numpy
    """
    facecolor = 'white'
    facecolor = 'grey'
    facecolor = 'black'
    if hasattr(fig, 'get_facecolor'):
        facecolor = fig.get_facecolor()
        #print('facecolor', facecolor)

    # no renderer without this
    image = io.BytesIO()
       
    fig.savefig(image, facecolor=facecolor, dpi=200)
    try:
        fig.close()
    except AttributeError:
        print('cannot close figure')


    return Image.open(image)


class RoundAbout:
    """ 
    A magic queue switch.

    Processes waiting on something.

    Input from queues.

    Balls, outputs, inputs.

    Time for bed, said zebedee 
    """
    def __init__(self):

        self.qsize = random.randint(30, 50)
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

    async def get(self, name='stdin'):

        self.counts.update([('get', name)])
        return await self.select(name).get()

    async def status(self):

        result = {}
        result['counts'] = self.counts
        
        for qname, qq in self.qs.items():
            result[qname] = qq.qsize()

        from pprint import pprint
        pprint(result)
        return result

    def add_filter(self, key, coro, name='keys'):

        self.filters[name][key] = coro


    def add_queue(self, name=None):

        qq = curio.UniversalQueue(maxsize=self.qsize)
        self.qs[name] = qq

        return qq


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

        self.flock = None
        self.running = {}
        self.whistlers = {}
        self.relays = {}
        self.path = [self]

        self.add_filter('h', self.help)
        self.add_filter('n', self.next)
        self.add_filter('p', self.previous)
        
        self.add_filter('u', self.up)
        self.add_filter('d', self.down)
        self.add_filter('R', self.toggle_run)

        self.add_filter('T', self.status)

        # make a little sleepy
        self.sleep *= 10


    async def status(self):

        print('PATH')
        for item in self.path:
            print(item)

        for item in self.flock.nodes:
            print(item)
            if item is not self:
                await item.status()
            print()

    def set_flock(self, flock):
        """  Supply the flock to be watched """
        self.flock = flock

    def set_path(self, path=None):
        
        self.path = path or [self]

    async def whistler(self, queue, name='keys'):
        """ Send out whistles fromm a queue """
        while True:
            key = await queue.get()
            #print('WOOOHOO whistle time', key)
            await self.whistle(key, name)
    
    async def whistle(self, key, name='keys'):
        """ send out a message 
         
        follow the graph to see who's interested


        feels like this should be some sort of broadcast

        or perhaps directional if there's a name?

        or just send it to anything that is running and seems to care?
        """
        print('whsitle', key, name)
        
        for sheep in reversed(self.path):
            lu = sheep.radii.filters[name]
            #print('whistle', sheep, lu)
            if key in lu.keys():
                print('sending message', key, name, sheep)
                await lu[key]()

                # first one gets it?
                return True

        # nobody cares :(
        print('nobody cares :(')
        return False

    async def help(self, name='keys'):
        """ Show what keys do what 

        whistle help: these two need to be kept in sync.
        """
        print('HELP', self.path)

        # FIXME? 
        msg = ''
        keys = set()
        for sheep in reversed(self.path):
            #msg += repr(sheep) + '\n'
            lu = sheep.radii.filters[name]
        
            for key, value in lu.items():
                if key in keys: continue

                keys.add(key)
                msg += '{} {}\n'.format(
                    key,
                    self.doc_firstline(value.__doc__))
        print(msg)
        await self.put(msg, 'help')
        from blume import teakhat
        teakhat.Help(msg)


    def doc_firstline(self, doc):
        """ Return first line of doc """
        if doc:
            return doc.split('\n')[0]
        else:
            return "????"


    async def start(self):
        """ Start things going """
        print('STARTING SHEPHERD')
        for sheep in self.flock:
            if sheep is self:
                print("skipping starting myself")
                #self.running[self] = True
                continue
                
            print('starting', sheep)
            # just start all the nodes
            await sheep.start()
            
            info = self.flock.nodes[sheep]
            print('info', info)
            if info.get('background'):
                # run in background
                runner = await curio.spawn(canine(sheep))
                self.running[sheep] = runner


            if info.get('hat'):
                # set task to whistle out output
                whistle = await curio.spawn(
                    self.whistler(sheep.select('stdout')))

                self.whistlers[sheep] = whistle

        print('whistlers', self.whistlers)
        await self.watch_roundabouts()

        # figure out current path
        #current = None
        #for sheep in self.flock:
        #    if current is None:
        #        current = sheep
        #        
        #self.path.append(current)

        # what set up is needed for run?
        # navigate the tree
        # R for run
        # S for stop
        # u/d/p/n up down previous next

    async def watch_roundabouts(self):

        print('watching roundabouts')

        for a, b in self.flock.edges:
            print('xxx', a, b)
            print(a.radii.qs.keys())
            print(b.radii.qs.keys())

            bridge = await curio.spawn(relay(a, b))
            self.relays[(a, b)] = bridge

            
        
    async def next(self):
        """ Move focus to next """
        print(f'what is next?: {self.path}')
        print(self.path[-1])

    async def previous(self):
        """ Move focus to previous """
        print(f'what is previous?: {self.path}')

    async def up(self):
        """ Move up path """
        if len(self.path) > 1:
            del self.path[-1]
        print(f'up new path: {self.path}')

    async def down(self):
        """ Move focus to next node """
        current = None
        
        if self.path:
            current = self.path[-1]

        succ = nx.dfs_successors(self.flock, current, 1)

        succ = list(self.flock.predecessors(current))

        if succ:
            self.path.append(random.choice(succ))

        print(f'down new path: {self.path}')

    async def toggle_run(self, sheep=None):
        """ Toggle run status of sheep """

        sheep = sheep or self.path[-1]
        
        # run it if not already running
        if sheep not in self.running:
            self.running[sheep] = await curio.spawn(canine(sheep))
        else:
            task = self.running[sheep]
            await task.cancel()
            del self.running[sheep]


    async def run(self):
        """ run the flock 

        Decide what to run.

        Manage the resulting set of roundabouts.

        Pass messages along.
        """
        #for sheep in self.flock:
            #print(f'shepherd running {sheep in self.running} {sheep}')
            #print(f'   {sheep.status()}')
        #print('SHEPHERD RUN')
        # delegated to hub
        print('shepstart')
        fig = plt.figure()
        #nx.draw(self.flock)
        colours = []
        for sheep in self.flock:
            c = 'blue'
            if sheep in self.running:
                c = 'red'

            if sheep is self.path[-1]:
                c = 'gold'
            elif sheep in self.path:
                c= 'green'

            colours.append(c)
            
        nx.draw_networkx(self.flock, node_color=colours)

        print('sheput')
        await self.put(fig2data(plt))
        print('shepend')
        #print(self.radii.counts)
        
        #print(self.radii)

        #print(self.flock)


    async def quit(self):
        """ Cancel all the tasks """

        print('Cancelling runners')
        print(self.running)
        for task in self.running.values():
            await task.cancel()

        print('Cancelling whistlers')
        print(self.whistlers)
        for task in self.whistlers.values():
            await task.cancel()

    def __str__(self):

        return f'shepherd of flock degree {len(self.flock)}'


class Table(Ball):
    """ Magic table.

    A list of dictionaries, and ways to explore them?
    """
    
    def __init__self(self, data=None):

        super(self).__init__()

        self.data = data
    

async def canine(ball):
    """ A sheep dog, something to control when it pauses and sleeps

    runner for node.run and more

    This was an an attempt to factor out some boiler plate from 
    run methods.

    so run has turned into "do one iteration of what you do"

    and `canine` here is managing pausing and sleep

    
    
    Now we could loop round doing timeouts on queues and then firing
    off runs.

    With a bit more work when building things ... self.radii time?
    
    """

    print('dog chasing ball:', ball)
    runs = 0
    while True:
        if not ball.paused:

            await ball.run()
            runs += 1

            if False:
                print(f'run {runs} for {ball}')

        await curio.sleep(ball.sleep)


async def relay(a, b):

    while True:
        value = await a.get('stdout')
        print('relay', type(value), 'from', type(a), 'to', type(b))
        
        await b.put(value, 'stdin')

async def run():

    farm = GeeFarm()

    a = Ball()
    b = Ball()
    
    farm.add_edge(a, b)

    print('starting farm')
    await farm.start()

    print('running farm')
    await farm.run()

    
def random_colour():

    return random.choice(plt.colormaps())
    

if __name__ == '__main__':
    
    
    curio.run(run(), with_monitor=True)
