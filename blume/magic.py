"""Matplotlib plus async


mainloop()

queues of images

clients set up their own queues

draw from Q

Going round in ever decreasing circles.  

The idea is there is some sort of calculation going on that generates grids of
numbers.

You want to see what is going on without grinding the calculations to a halt.

At the same time, the more you explore the data with plots (thanks matplotlib)
the more questions appear.

Often the calculation has a number of parameters, or a selection of data
streams on which it could be run.

So my code sprouts command line arguments and then the simple U/I might allow
me to control more of the parameters.

This module aims to provide a small number of components to help asynchronous
data exploration and graphical monitoring of data processing pipelines.

It also aims to help with the process of maintenance of data streams
over time.   See metagit.py for more ideas there.

Many magic classes started as objects in other short scripts, see
examples for some of those.

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

Update
======

I am planning to re-work how objects pass between Balls.

Balls await put() and get() messages and not care where they come from.

The plan is for the GeeFarm or Shepherd to allow you to examine queue
statistics and add and delete edges to the graph, with an option
whereby it randomly connects things together until it works or melts
or something.

Make it a bit easier to view and navigate the various graphs.

Leaning to a bunch of different *Controller* objects that you can call
up for different tasks such as viewing queues, starting and stopping
processes.

Other objects, waiting on input.

In short, there is a working prototype.  

It is time to untangle the various objects and mold it into something
smaller and more powerful.

That we can then use in the farm module to build a functioning whole.

Let the balls bounce around randomly with the magic roundabout routing
the photons.

"""
import random

import math

import datetime

import io

import sys

from pathlib import Path

from collections import deque, defaultdict, Counter

import argparse

import operator

from traceback import print_exc

import inspect

import dateutil

import curio

sleep = curio.sleep
run = curio.run
spawn = curio.spawn

import numpy as np

from PIL import Image

import matplotlib

from matplotlib import figure

from matplotlib import pyplot as plt

import networkx as nx

Parser = argparse.ArgumentParser

class Ball:
    
    def __init__(self, **kwargs):

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


    def __getattr__(self, attr):
        """ Delegate to roundabout
        """
        return getattr(self.radii, attr)

    def update(self, args):
        """ Update attributes as per args 

        args is expected to be from argparse.

        Now it is super easy to write a short module that has a bunch of
        command line parameters.

        
        """
        for key, value in vars(args).items():
            setattr(self, key, value)

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

class Interact(Ball):

    def __init__(self, ball):

        super().__init__()
        
        self.history = deque()
        self.set_ball(ball)

        self.add_filter('0', self.toggle)
        self.add_filter('1', self.add_one)
        self.add_filter('3', self.sub_one)
        self.add_filter('2', self.double)
        self.add_filter('4', self.half)
        self.add_filter('5', self.flipsign)
        self.add_filter('8', self.rcycle)
        self.add_filter('9', self.cycle)
        self.add_filter('x', self.tenx)
        self.add_filter('z', self.tenth)
        self.add_filter('m', self.add_m)
        self.add_filter('\177', self.shorten)

        self.add_filter(' ', self.next_attr)
        self.add_filter('\b', self.prev_attr)
        self.add_filter('\r', self.re_interact)
        self.add_filter('Left', self.back)

        self.add_filter('i', self.interact)


    def set_ball(self, ball):

        try:
            self.attrs = deque(sorted(vars(ball).keys()))
        except:
            print('oops no can interact')
            return

        self.ball = ball



    async def back(self):
        """ pop back in history """

        if not self.history:
            return
        
        ball = self.history.pop()
        self.set_ball(ball)


    async def interact(self):
        """ Go into interactive mode 
        
        hmm.... worm can time
        """

        from pprint import pprint
        for key, value in sorted(vars(self.ball).items()):
            rep = repr(value)
            if len(rep) > 200:
                rep = rep[:10] + ' ... ' + rep[-10:]
            print(key, rep, type(value))

        print()
        self.show_current()
        print()


    async def re_interact(self):
        """ Recursively interact mode 
        
        hmm.... bigger worm can time

        Idea is to interact on current attribute of whatever current is
        """
        
        current = self.current()
        obj = getattr(self.ball, current)

        self.set_ball(obj)
        self.show_current()

        
    def show_current(self):
        
        attr = self.current()
        print(attr, getattr(self.ball, attr))


    def current(self):
        """ Return current attr """
        return self.attrs[0]

    async def next_attr(self):

        self.attrs.rotate(-1)

        self.show_current()

    async def prev_attr(self):

        self.attrs.rotate()
        attr = self.attrs[0]

        self.show_current()


    def operate(self, op=operator.add, b=2):
        
        key = self.current()
        value = getattr(self.ball, key)
        if b is not None:
            value = op(value, b)
        else:
            value = op(value)

        setattr(self.ball, key, value)

        print(f'{key}: {value}')

    async def double(self):
        """ i double """
        self.operate(operator.mul, 2) 
        
    async def half(self):
        """ i half """
        self.operate(operator.mul, 1/2)

    async def tenx(self):
        """ i ten x """

        self.operate(operator.mul, 10)
        
    async def tenth(self):
        """ i one tenth """

        self.operate(operator.mul, 1/10)
        
    async def add_one(self):
        """ i one more """

        self.operate(operator.add, 1)

    async def add_m(self):
        """ i one thousand more """

        self.operate(operator.add, 1000)

    async def sub_one(self):
        """ i one less """
        self.operate(operator.add, -1)

    async def toggle(self):
        """ i toggle """
        self.operate(operator.not_, None)
        
    async def flipsign(self):
        """ i flip """
        self.operate(operator.mul, -1)

    def acycle(self, howmuch=1):

        key = self.current()
        value = getattr(self.ball, key)
        
        try:
            value.rotate(howmuch)
            if value:
                print(value[0])
        except:  
            print(value)
            try:
                if howmuch > 0:
                    split = -1 * (1 + howmuch)
                    value = value[:] + value[:howmuch]
            except:
                print('no cycle for you', howmuch)

    async def cycle(self):
        """ i cycle """
        self.acycle()
        
    async def rcycle(self):
        """ i cycle back """
        self.acycle(-1)

    async def shorten(self):

        key = self.current()
        
        value = getattr(self.ball, key)
        if len(value) > 1:
            print(f'popping {value[0]}')
            value.popleft()
            print(f'new head {value[0]}')

class Spell:
    """ A magic spell, or cast if you like, if it works

    For help processing lists of dictionaries.

    Or csv files, where we have to turn strings into values.

    The game is guessing the types of the columns in a csv file.

    Use a magic.Spell.

    
    """

    def __init__(self, cache=None):
        """  
        
        Older idea, updated::

        Cache size is how much rewind we get if a type changes

        If None, everything gets cached.

        It would make sense to coordinate this with
        functools.lru_cache, now known as functools.cache (python 3.9).
        
        For small datasets this might be what you want.

        """

        # casts by keyword
        self.casts = {}
        self.date_parse = date_parse = dateutil.parser.parser().parse
        self.upcast = {None: int, int: float, float: date_parse, date_parse: str}
        self.fill = {None: None, int: 0, float: 0.0, date_parse: None, str: ''}

        # how much data to look at to find casts
        self.sniff = 10
        
        
        # i don't think this bit is implemented yet -- see comment above
        self.cache = deque(maxlen=cache)


    def spell(self, data, sniff=10):
        """ Apply casts to data
        
        Would like this to be dynamic, updating the casts as we go """

        # short hand for:  for xx in self.cast_data(data); yield xx
        yield from self.cast_data(data)
        
        
    def find_casts(self, data, sniff=10):

        sniff = sniff or self.sniff

        keys = data[0].keys()

        casts = self.casts
        
        upcast = self.upcast
        
        for row in data[self.sniff:]:
            for key in keys:
                value = row[key].strip()
                if value:
                    try:
                        casts.setdefault(key, int)(value)
                    except:
                        casts[key] = upcast[casts[key]]
                    
        # look for a (first) date key - probably should looke
        # for all dates, really we are looking for an index here
        self.datekey = None
        for key, cast in self.casts.items():
            if cast is self.date_parse:
                self.datekey = key
                return


    def check_casts(self, data, sniff=10):

        self.find_casts(data, sniff)

    def cast_data(self, data):

        casts = self.casts

        fill = self.fill

        for row in data:

            result = {}
            for key, value in row.items():
                if key not in casts:
                    print(key)
                    continue
                
                cast = casts[key] 
                if not value.strip():
                    value = fill.setdefault(cast)

                result[key] = cast(value)
            yield result

    def fields(self):

        return self.casts.keys()

def find_date_key(record):

    for key, value in record.items():
        try:

            date = dateutil.parser.parser(value)
            return key
        except Exception as e:
            # guess it is not this one
            print(e)
            print(key, value, 'is not a date')


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
        result = self.shep.start()
        if inspect.iscoroutine(result):
            await result

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


modes = deque(['grey', 'white', 'black'])

def fig2data(fig=None, background='grey'):
    """ Convert a Matplotlib figure to a PIL image.

    fig: a matplotlib figure
    return: PIL image

    There has to be an easier way to do this.

    FIXME -- turning matplotlib figures into PIL or numpy
    """
    #facecolor = 
    #facecolor = 
    #facecolor = 'black'
    fig = fig or plt
    facecolor = modes[0]
    if hasattr(fig, 'get_facecolor'):
        facecolor = fig.get_facecolor()
        #print('facecolor', facecolor)

    # no renderer without this
    image = io.BytesIO()

    fig.savefig(image, facecolor=facecolor, dpi=200)
    try:
        fig.close()
        pass
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

    async def put(self, value=None, name='stdout'):

        self.counts.update([('put', name)])
        await self.select(name).put(value or fig2data(plt))

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

        self.interaction = Interact(self.path[-1])

        self.add_filter('h', self.help)
        self.add_filter('n', self.next)
        self.add_filter('p', self.previous)
        
        self.add_filter('u', self.up)
        self.add_filter('d', self.down)
        self.add_filter('R', self.toggle_run)

        self.add_filter('T', self.status)

        self.add_filter('i', self.interact)

        # make a little sleepy
        self.sleep *= 10


    async def interact(self):
        """ Go into interactive mode 
        
        hmm.... worm can time
        """


        # Now if interaction has
        current = self.current()
        if current is not self.interaction.ball:
            self.interaction.set_ball(current)

        if self.interaction not in self.path:
            self.path.append(self.interaction)

        await self.interaction.interact()

        
    def current(self):

        return self.path[-1]


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
        #print('whsitle', key, name)
        
        for sheep in reversed(self.path):
            lu = sheep.radii.filters[name]
            #print('whistle', sheep, lu)
            if key in lu.keys():
                try:
                    await lu[key]()
                except:
                    print_exc()

                # first one gets it?
                return True

        # nobody cares :(
        try:
            print('nobody cares :(', key, ord(key), type(key))
        except:
            print(key)
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
        #teakhat.Help(msg)


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
            dolly = sheep.start()
            if inspect.iscoroutine(dolly):
                await dolly
            
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
        print(self.current())

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
        current = self.current()

        succ = nx.dfs_successors(self.flock, current, 1)

        succ = list(self.flock.predecessors(current))

        if succ:
            self.path.append(random.choice(succ))

        print(f'down new path: {self.path}')

    async def toggle_run(self, sheep=None):
        """ Toggle run status of sheep """

        sheep = sheep or self.current()
        
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

            if sheep is self.current():
                c = 'gold'
            elif sheep in self.path:
                c= 'green'

            colours.append(c)
            
        nx.draw_networkx(self.flock, node_color=colours)

        await self.put()
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


class Table:
    """ Magic table.

    A list of dictionaries, and ways to explore them?
    """
    
    def __init__self(self, path=None, data=None, meta_data=None):
        """ Turn what we are given into a table """

        self.path = path or Path()
        self.data = data
        self.meta_data = meta_data
        
        """ now what?  look at data with a magic spell and get meta data.
        
        
        """

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

    Update: trying to accommodate balls where run is just a function.
    
    """

    print('dog chasing ball:', ball)
    runs = 0
    while True:
        if not ball.paused:

            result = ball.run()
            if inspect.iscoroutine(result):
                await result
            
            runs += 1

        await curio.sleep(ball.sleep)


async def relay(a, b):

    while True:
        value = await a.get('stdout')
        #print('relay', type(value), 'from', type(a), 'to', type(b))
        
        await b.put(value, 'stdin')

async def runme():

    farm = GeeFarm()

    a = Ball()
    b = Ball()
    
    farm.add_edge(a, b)

    print('starting farm')
    await farm.start()

    print('running farm')
    await farm.run()

    
def random_colour():
    """ Pick a random matplotlib colormap """
    return random.choice(plt.colormaps())
    

if __name__ == '__main__':
    
    
    run(runme(), with_monitor=True)
