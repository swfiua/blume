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

import functools

#import curio
import asyncio
curio = asyncio

sleep = curio.sleep
run = curio.run
spawn = curio.create_task

import numpy as np

from PIL import Image

import matplotlib

from matplotlib import figure, artist

from matplotlib import pyplot as plt

from .modnar import random_colour, random_queue

from . import table

Parser = argparse.ArgumentParser


class RoundAbout:
    """ Pass self around.
    
    Just a collection of random queues that everyone shares.

    For maximal information sharing, I'm curious what happens when 
    objects with the roundabout do something like:

    await self.put(self)

    The magic roundabout just looks after the queues.
    """

    # There is only one, initialise attributes as class attributes

    # default queue is whatever random_queue serves up.
    # 
    queues = defaultdict(random_queue)
    counts = Counter()
    
    async def put(self, item, name=None):

        qq = self.queues[name]
        self.counts.update([f'put {name}'])
        await qq.put(item)

    def put_nowait(self, item, name=None):

        qq = self.queues[name]
        self.counts.update([f'put_nowait {name}'])
        try:
            qq.put_nowait(item)
        except asyncio.queues.QueueFull:
            print(f'magic queue {name} is full.  size={qq.qsize()}')

    def get_nowait(self, name=None):

        qq = self.queues[name]
        self.counts.update([f'get_nowait {name}'])
        try:
            item = qq.get_nowait()
        except asyncio.queues.QueueFull:
            print(f'magic queue {name} is full.  size={qq.qsize()}')

        return item
    
    async def get(self, name=None):

        qq = self.queues[name]
        self.counts.update([f'get {name}'])

        result = await qq.get()

        return result


    def select(self, name=None, create=True):
        """ pick a q 
        
        create: if True, create if missing -- actually seems to create
        regardless, why not?
        """
        return self.queues[name]

    def status(self):
        """ Show some stats """
        print("Queue Stats")
        for name, qq in self.queues.items():
            print(name, qq.qsize(), qq.maxsize)

TheMagicRoundAbout = RoundAbout()
            
class Ball:
    
    def __init__(self, **kwargs):


        if kwargs:
            self.update(kwargs)
        
        self.paused = False
        self.sleep = .8

        # ho hum update event_map to control ball?
        # this should be done via roundabout,
        # let shepherd control things?
        self.filters = defaultdict(dict)
        
        self.add_filter('z', self.sleepy)
        self.add_filter('w', self.wakey)
        #self.add_filter(' ', self.toggle_pause)
        self.add_filter('W', self.dump_roundabout)
        self.add_filter('j', self.status)

    def add_filter(self, key, coro, name='keys'):

        self.filters[name][key] = coro


    async def dump_roundabout(self):

        print('DUMPING ROUNDABOUT')
        print(TheMagicRoundAbout.counts)
        #await self.put(TheMagicRoundAbout.counts, 'help')
        counts = TheMagicRoundAbout.counts.most_common()
        ax = await self.get()
        
        ax.bar(range(len(counts)),
            height=[x[1] for x in counts],
            tick_label = [x[0] for x in counts])
        for tick in ax.get_xticklabels():
            tick.update(dict(rotation=45))
        ax.show()

    def __getattr__(self, attr):
        """ Delegate to TheMagicRoundAbout
        """

        return getattr(TheMagicRoundAbout, attr)


    def update(self, args):
        """ Update attributes as per args 

        args is expected to be from argparse.

        Now it is super easy to write a short module that has a bunch of
        command line parameters.

        
        """
        for key, value in vars(args).items():
            setattr(self, key, value)

    def sleepy(self):
        """ Sleep more between updates """
        self.sleep *= 2
        print(f'sleepy {self.sleep}')

    def wakey(self):
        """ Sleep less between updates """
        self.sleep /= 2
        print(f'wakey {self.sleep}')

    def toggle_pause(self):
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
        self.add_filter('c', self.shorten)

        self.add_filter('.', self.next_attr)
        self.add_filter(',', self.prev_attr)
        self.add_filter('enter', self.re_interact)
        self.add_filter('escape', self.back)

        self.add_filter('i', self.interact)

    async def run(self):
        """When this is triggeredit usually means I
        want to run self.ball, not myself

        for now, achieve this by waiting for self.back()
        and then pushing an r to trigger a run

        wonder if this works?
        I wonder how far the magic roundabout can go before
        descending into chaos

        the real reason this is here is it is the Sheperd that looks
        after running things.

        I think I will have it listen to a 'run' queue.

        ... added a run queue i think .... let's see
        """
        
        await self.put(self.ball, 'run')

    def set_ball(self, ball):

        try:
            if isinstance(ball, dict):
                attrs = deque(ball.keys())
                ball = Wrapper(ball)
            else:
                attrs = deque(sorted(vars(ball).keys()))
                
            if len(attrs) == 0:
                print(vars(ball))
                print(f'{ellipsis(repr(ball))} has no attributes to interact with')
                return
            
        except Exception as e:
            print(e)
            print('oops no can interact', ball)
            return

        self.attrs = attrs
        self.ball = ball



    async def back(self):
        """ pop back in history """

        if not self.history:
            return
        
        ball = self.history.pop()
        self.set_ball(ball)


    def interact(self):
        """ Go into interactive mode 
        
        hmm.... worm can time
        """
        from pprint import pprint
        for key, value in sorted(vars(self.ball).items()):
            rep = ellipsis(repr(value))
            print(key, rep, type(value))
            

        print()
        self.show_current()
        print()


    async def re_interact(self):
        """ Recursively interact mode 
        
        hmm.... bigger worm can time

        Idea is to interact on current attribute of whatever current is
        """
        print('XXXXX re_interact')
        current = self.current()
        obj = getattr(self.ball, current)

        self.history.append(self.ball)
        self.set_ball(obj)
        self.show_current()

        
    def show_current(self):

        attr = self.current()
        value = repr(getattr(self.ball, attr))
        result = (attr, ellipsis(value))
        print(*result)
        #self.put_nowait(str(result), 'help')


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

        try:
            items = list(value)
            for ix, item in enumerate(items):
                if b is not None:
                    value[ix] = op(item, b)
                else:
                    value[ix] = op(item)

        except TypeError:
            if b is not None:
                value = op(value, b)
            else:
                value = op(value)

            setattr(self.ball, key, value)

        print(f'{key}: {value}')
        self.show_current()

    def double(self):
        """ i double """
        self.operate(operator.mul, 2) 
        
    def half(self):
        """ i half """
        self.operate(operator.mul, 1/2)

    def tenx(self):
        """ i ten x """

        self.operate(operator.mul, 10)
        
    def tenth(self):
        """ i one tenth """

        self.operate(operator.mul, 1/10)
        
    def add_one(self):
        """ i one more """

        self.operate(operator.add, 1)

    def add_m(self):
        """ i one thousand more """

        self.operate(operator.add, 1000)

    def sub_one(self):
        """ i one less """
        self.operate(operator.add, -1)

    def toggle(self):
        """ i toggle """
        self.operate(operator.not_, None)
        
    def flipsign(self):
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

    def cycle(self):
        """ i cycle """
        self.acycle()
        
    def rcycle(self):
        """ i cycle back """
        self.acycle(-1)

    def shorten(self):

        key = self.current()
        
        value = getattr(self.ball, key)
        if len(value) > 1:
            print(f'popping {value[0]}')
            value.popleft()
            print(f'new head {value[0]}')

class Wrapper:

    def __init__(self, ball):

        self.__dict__.update(ball)

        
            
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
        
        
    def spell(self, data):
        """ Apply casts to data
        
        Would like this to be dynamic, updating the casts as we go """

        # short hand for:  for xx in self.cast_data(data); yield xx
        yield from self.cast_data(data)
        
        
    def find_casts(self, data, sniff=10):

        sniff = sniff or self.sniff

        keys = data[0].keys()

        casts = self.casts
        
        upcast = self.upcast
        
        for row in data[-self.sniff:]:
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
        hub = hub or DiGraph()

        hub.add_nodes_from(nodes or set())
        hub.add_edges_from(edges or set())

        print('OK to here')
        self.hub = hub
        self.shep = Shepherd()

        # register quit event with shepherd
        self.shep.add_filter('q', self.quit)
        print('OK to here2')


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
        self.superdog = spawn(canine(self.shep))

        # set the shepherd to pause 
        self.shep.pause = True

        # figure out an initial path


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

    return Image.open(image)

class Shepherd(Ball):
    """Watches things nobody else is watching 

    This currently sets up all the message handling and
    runs everything.

    To route messages between balls it is seems to be necessary to
    have access to the graph of relationships.

    In the current setup this is GeeFarm, but this leaves everything to 
    the Shepherd.

    The Shepherd in turn does it's work by setting up relays for each
    edge in the graph, watching all the roundabout queues and passing
    messages along.

    There is one relay per edge in the graph and it just connects the
    output and input queues of objects along that edge.

    There is a whole other chunk of code dealing with passing keyboard
    events along a path of objects, and all the related key binding fun.

    Again, the roundabout holds the data and every Ball has a Roundabout.
    
    It might be good to have just one RoundAbout, managed by the Shepherd.

    Dynamic graph?

    """

    def __init__(self):

        super().__init__()

        self.flock = None
        self.running = {}
        self.relays = set()
        self.path = [self]

        self.interaction = Interact(self.path[-1])

        self.add_filter('h', self.show_help)
        self.add_filter('n', self.next_ball)
        self.add_filter('p', self.previous_ball)
        
        #self.add_filter('u', self.up)
        #self.add_filter('d', self.down)
        self.add_filter('r', self.toggle_run)
        self.add_filter('b', self.start)
        self.add_filter('I', self.edit_current)

        self.add_filter('x', self.status)

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

        self.interaction.interact()

        if self.interaction not in self.path:
            self.path.append(self.interaction)
            self.generate_key_relays()
            self.put_nowait('interact', 'gkr')

        
    def current(self):

        return self.path[-1]


    async def status(self):
        """ Show current status of object graph """
        #await self.put(id(TheMagicRoundAbout), 'status')
        #await self.put(id(TheMagicRoundAbout), 'help')
        #qsize = self.select('status').qsize()
        #await
        helps = []
        helps += str(TheMagicRoundAbout.counts).split(',')

        #for item in self.flock.nodes:
        #    helps.append(str(item))
        #                  
        #    if item is not self:
        #        try:
        #            stat = item.status()
        #            if inspect.iscoroutine(stat):
        #                await stat
        #        except:
        #            pass
        #    print()

        helps.append('')
        helps += [str(x.__class__) for x in self.path]

        helps.append('PATH')
        for item in self.path:
            helps.append(str(item))
        print('\n'.join(helps))
        self.put_nowait('\n'.join(helps), 'help')


    def set_flock(self, flock):
        """  Supply the flock to be watched """
        self.flock = flock

    def set_path(self, path=None):
        
        self.path = path or [self]


    def generate_key_relays(self, name='keys'):

        for rly in self.relays:
            rly.cancel()

        self.relays.clear()
        for target, key, callback in self.generate_key_bindings():
            listener = spawn(relay(key, callback))
            self.relays.add(listener)

        self.put_nowait('gkr', 'oldgrey')

    def generate_key_bindings(self, name='keys'):

        keys = set()
        for sheep in reversed(self.path):
            #msg += repr(sheep) + '\n'
            lu = sheep.filters[name]
        
            for key, value in lu.items():
                if key in keys:
                    continue
                yield sheep, key, value

                keys.add(key)


    async def show_help(self, name='keys'):
        """ Show what keys do what """
        print('HELP', self.path)

        # FIXME? 
        msg = ''
        for sheep, key, callback in self.generate_key_bindings(name=name):
            msg += '{} {}\n'.format(
                key,
                self.doc_firstline(callback))

        print(msg)
        # hmm -- there's a queue of help messages somewhere
        # maybe should use that for some other display.

        hq = self.select('help')
        if hq.qsize() < hq.maxsize - 1:
            # if the queue is getting full, then we don't want to hang here.
            # curiously, maxsize - 1 is the critical size at which it seems
            # to hang.
            self.put_nowait(msg, 'help')

    def doc_firstline(self, value):
        """ Return first line of doc """

        doc = value.__doc__
        if doc:
            return doc.split('\n')[0]
        else:
            return repr(value)
            #return "????"

    async def helper(self):
        """ Task to run if you want help on the carpet 

        One day it will be easy to start and stop this.
        """
        from blume.legend import Grid

        print('xxHELPER STARTING UPxx')
        while True:
            msg = await self.get('help')
            ax = await self.get()
            try:
                if isinstance(msg, str):
                    msg = [[msg]]
                tab = table.table(
                    ax.delegate, cellText=msg, bbox=(0,0,1,1),
                    cellLoc='center')

                foo = tab[0,0]
                foo.set_text_props(multialignment='left')
            except:
                print("HELPER CAUGHT AN EXCEPTION")
                print_exc()
                continue

            ax.axis('off')
            ax.show()
            continue
            
            fontsize = 6
            prop = dict(size=fontsize)
            grid = Grid([[msg]], prop=prop)
            #grid.set_visible(False)
            #ax.text(0., 0., msg)
            #        verticalalignment='center',
            #        horizontalalignment='center',
            #        transform=ax.transAxes)
            #ax.axis('off')
            renderer = ax.figure._cachedRenderer

            grid.figure = ax.figure
            ax.axis('off')
            ax.add_artist(grid)
        
            if renderer:
                try:
                    #print('FONT SCALING')
                    extent = grid.get_window_extent(renderer)
                    #print('WINDOW EXTENT', extent)
                    ax_extent = ax.get_window_extent(renderer)
                    #print('AXES EXTENT  ', ax_extent)
                    #print(ax_extent.x1 - ax_extent.x0)
                    #print(extent.x1 - extent.x0)
                    xfontscale = (ax_extent.x1 - ax_extent.x0) / (extent.x1 - extent.x0)
                    yfontscale = (ax_extent.y1 - ax_extent.y0) / (extent.y1 - extent.y0)
                    fontscale = min(xfontscale, yfontscale) * 0.9

                    prop['size'] *= fontscale
                    grid.remove()
                    grid = Grid([[msg]], prop=prop)
                    ax.add_artist(grid)

                    #print('scaled by', fontscale, xfontscale, yfontscale)
                    #print('bbox after scaling')
                    #print(grid.get_window_extent(renderer))
                except:
                    print_exc()
                        
            print('showing help axes')
            ax.show()


    async def start(self):
        """ Start things going 

        FIXME: make it simple
        """
        print('STARTING SHEPHERD')
        for sheep, info in self.flock.nodes.items():
            if sheep is self:
                print("skipping starting myself")
                #self.running[self] = True
                continue
                
            print('starting', sheep)
            # just start all the nodes 
            dolly = sheep.start()
            if inspect.iscoroutine(dolly):
                await dolly
            
            print('info', info)
            if info.get('background'):
                # run in background
                runner = spawn(canine(sheep))
                self.running[sheep] = runner
            else:
                self.path.append(sheep)

        spawn(relay('gkr', self.generate_key_relays))
        spawn(relay('run', self.toggle_run, with_message=True))

        # add a task to watch tasks
        self.watcher = spawn(self.task_watcher())

        print('sending out ready message to oldgrey')
        self.put_nowait('ready', 'gkr')
        #await self.watch_roundabouts()

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
        self.running['helper'] = spawn(self.helper())


    async def task_watcher(self):

        while True:
            print('Task q size', self.select('task').qsize())
            task = await self.get('task')
            if task.cancelled():
                continue

            if task.done():
                if task.exception():
                    print(task.exception())
            else:        
                await self.put(task, 'task')
            
        
    async def next_ball(self):
        """ Move focus to next 

        path management.
        """
        print(f'what is next?: {self.path}')
        print(f'wtf is going on?')
        current = self.current()
        print(f'current is {current}')
                
        print(f'doing nodes manipulation')
        nodes = [n for n in self.flock.nodes if n not in self.path]

        if nodes:
            self.path.append(nodes[0])
        
        #print('oldgrey', self.current())
        #await self.generate_key_relays()
        self.put_nowait('done', 'gkr')
        
        self.put_nowait(str(self.current()), 'help')

    async def previous_ball(self):
        """ Move focus to previous """
        await self.up()

    async def up(self):
        """ Move up path """
        if len(self.path) > 1:
            del self.path[-1]
        print(f'up new path: {self.path}')
        self.generate_key_relays()
        self.put_nowait(str(self.current()), 'help')
        self.put_nowait('done', 'gkr')

    async def down(self):
        """ Move focus to next node """
        await self.next_ball()

        #print(f'down new path: {self.path}')
        #await self.put(str(self.current()), 'help')
        #await self.put('done', 'oldgrey')

    async def toggle_run(self, sheep=None):
        """ Toggle run status of sheep """

        sheep = sheep or self.current()
        
        # run it if not already running
        if sheep not in self.running:
            self.running[sheep] = spawn(canine(sheep))
        else:
            task = self.running[sheep]
            try:
                await task.cancel()
            except:
                print(task)
                print(type(task))
            del self.running[sheep]

    async def edit_current(self):
        """ open code for current in idle 

        FIXME: what to do with no idle, eg in pyscript land?
        """

        sheep = self.current()

        filename = inspect.getsourcefile(sheep.__class__)

        sub = await asyncio.create_subprocess_shell(f'idle {filename}')

        # idle seems to want an _W
        #self._w = None

        
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
        #print('shepstart')
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
            
        #ax = await self.get()
        
        #nx.draw_networkx(self.flock, node_color=colours, ax=ax)

    async def quit(self):
        """ Cancel all the tasks """

        print('Cancelling runners and relays')
        tocancel = set(self.running.values())
        tocancel.update(self.relays)
        for task in tocancel:
            try:
                task.cancel()
            except Exception as e:
                print(f'cancel failed for {task}')
                print(e)

        #print('remaining tasks')
        #for task in asyncio.all_tasks():
        #    if not task.cancelled():
        #        print(task)
        

    def __str__(self):

        return f'shepherd of flock degree {len(self.flock)}'

class IdleRunner:

    def __init__(self, filename):

        self.filename = filename

    def __call__(self):

        import subprocess

        asyncio.subprocess.run(('idle', self.filename))
    

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

class Carpet(Ball):

    def __init__(self):

        super().__init__()

        self.fig = plt.figure(layout='constrained')

    def __getattr__(self, attr):

        return getattr(self.fig)

    async def run(self):

        await self.put(self)


async def canine(ball):
    """ A sheep dog, something to control when it pauses and sleeps

    runner for node.run and more

    This was an an attempt to factor out some boiler plate from 
    run methods.

    so run has turned into "do one iteration of what you do"

    and `canine` here is managing pausing and sleep

    
    
    Now we could loop round doing timeouts on queues and then firing
    off runs.

    With a bit more work when building things ... TheMagicRoundAbout time?

    Update: trying to accommodate balls where run is just a function.
    
    """

    print('dog chasing ball:', ball)
    runs = 0
    while True:
        if not ball.paused:

            try:
                result = ball.run()
                if inspect.iscoroutine(result):
                    #print(f'canine awaits result {runs} for {ball}')
                    await result
            
                runs += 1

                await sleep(ball.sleep)
            except asyncio.CancelledError:
                print(f'cancelled running of {ball}')
                raise

            except:
                print_exc()
                raise


async def runme():

    farm = GeeFarm()

    a = Ball()
    b = Ball()
    
    farm.add_edge(a, b)

    print('starting farm')
    await farm.start()

    print('running farm')
    await farm.run()



def ellipsis(string, maxlen=200, keep=10):
    
    if len(string) > maxlen:
        string = string[:keep] + ' ... ' + string[-keep:]

    return string

async def relay(channel, callback, with_message=False):

    import traceback
    while True:
        msg = await TheMagicRoundAbout.get(channel)
        try:
            if with_message:
                result = callback(msg)
            else:
                result = callback()

        except Exception as e:
            print(f'{channel} relay exception for {callback}')
            traceback.print_exc()
            continue
            
        if inspect.iscoroutine(result):
            try:
                await result
            except:
                traceback.print_exc()

if __name__ == '__main__':
    
    
    run(runme(), with_monitor=True)
