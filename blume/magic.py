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

import time

#import curio
import asyncio
curio = asyncio

sleep = curio.sleep
run = curio.run

spawn = curio.create_task

import numpy as np

from PIL import Image

import matplotlib

from matplotlib.transforms import Bbox

from matplotlib import figure, artist, patches, colors, rc

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

    axe = get_nowait
    
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
        self.sleep = .01
        self.tasks = Tasks()
        self.meta = {}

        # ho hum update event_map to control ball?
        # this should be done via roundabout,
        # let shepherd control things?
        self.filters = defaultdict(dict)
        
        self.add_filter('z', self.sleepy)
        self.add_filter('w', self.wakey)
        #self.add_filter(' ', self.toggle_pause)
        self.add_filter('W', self.dump_roundabout)
        #self.add_filter('j', self.status)

    def add_filter(self, key=None, coro=None, name='keys'):

        filters = self.filters[name]
        if key is None:
            # FIXME - what if name is short?
            # check rest of alphabet?
            # do these filters even belong here -- actually can be
            # handy!
            for char in coro.__name__ + coro.__name__.upper():
                if char not in filters:
                    key = char
                    
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
        try:
            data = vars(args)
        except TypeError:
            data = args
        for key, value in data.items():
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

        await self.tasks.run()

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
        self.meta = dict(x='x', y='y')

    def __getattr__(self, attr):

        try:
            return getattr(self.delegate, attr)
        except AttributeError as e:

            try:
                return getattr(plt, attr)
            except:
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
        self.set_axes(pax)
        self.meta['projection'] = name

    def set_axes(self, pax):
        """ Replace current delegate ax with pax

        Hack to help with cases where something else creates
        the axes.
        """
        ax = self.delegate
        self.delegate = pax
        self.position(ax)
        self.carpet.lookup[id(pax)] = self
        if hasattr(ax, 'img'):
            ax.img.remove()

        # now delete ax
        ax.remove()
        del ax


    def simplify(self):

        #self.xaxis.set_visible(False)
        #self.yaxis.set_visible(False)
        self.axis('off')

    async def show_colorbar(self, mappable):

        ax = await TheMagicRoundAbout.get()
        
        self.figure.colorbar(mappable, ax, self)
        ax.show()

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
        
    async def mscatter(self):
        """ still figuring this out

        does the Axe have a table?

        or nested tables.
        """
        meta = self.carpet.meta
        x = meta['x']
        y = meta['y']
        self.delegate.scatter(x, y)

    async def mplot(self, table=None):
        pass

    async def mimshow(self):
        pass

    def mlegend(self):

        from matplotlib import legend
        handles, labels = legend._get_legend_handles_labels([self])
        if len(handles) <= 10: self.legend()
        
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

    def get(self):
        """ Return a fresh axis """
        
        try:
            return TheMagicRoundAbout.get_nowait()
        except asyncio.queues.QueueEmpty:
            return self


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


class InteractBase(Ball):
    """ Base class for interactive table stuff """
    def __init__(self, ball):

        super().__init__()
        
        self.history = deque()
        self.set_ball(ball)

        # escape goes up one
        self.add_filter('escape', self.back)

    
    def set_ball(self, ball):

        self.ball = ball
        self.set_attrs()

    def set_attrs(self):

        self.attrs = deque(sorted(vars(self.ball)))

    async def run(self):
        """When this is triggered it usually means I
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

        # and switch ourself off
        #await self.put(self, 'run')

    async def back(self):
        """ pop back in history """

        if not self.history:
            return
        
        ball = self.history.pop()
        self.set_ball(ball)

    def show_attr_table(self):
        
        msg = []
        for key in self.attrs:
            value = getattr(self.ball, key)
            rep = ellipsis(repr(value))
            msg.append([key, rep, type(value)])

        self.put_nowait(msg, 'help')

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

        self.show_attr_table()
        self.show_current()

    async def prev_attr(self):

        self.attrs.rotate()
        attr = self.attrs[0]

        self.show_attr_table()
        self.show_current()

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

        # show attributes
        self.show_attr_table()

class Interact(InteractBase):

    def __init__(self, ball):

        super().__init__(ball)
        
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

        self.add_filter('i', self.interact)

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

        # show attributes
        self.show_attr_table()

    def show_attr_table(self):
        
        msg = []
        for key in self.attrs:
            value = getattr(self.ball, key)
            rep = ellipsis(repr(value))
            msg.append([key, rep, type(value)])

        self.put_nowait(msg, 'help')

    async def re_interact(self):
        """ Recursively interact mode 
        
        hmm.... bigger worm can time

        Idea is to interact on current attribute of whatever current is
        """
        current = self.current()
        obj = getattr(self.ball, current)
        print('XXXXX re_interact', current, type(obj))

        #try:
        #    obj = await self.to_table(obj)
        #except:
        #    print('hmm... not a table?')
        
        self.history.append(self.ball)
        self.set_ball(obj)
        self.show_current()
        self.show_attr_table()


    async def to_table(self, obj):
        from astropy.table import Table
        table = Table(obj)
        print(table.colnames)

        key = table.colnames[0]
        
        for col in table.colnames[1:]:
            print('plotting', col)
            try:
                ax = await self.get()

                ax.plot(table[col])
                ax.set_xlabel(col)

                ax.show()
            except:
                pass

        return table
        

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
        self.show_attr_table()

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
        self.show_attr_table()
        
    def rcycle(self):
        """ i cycle back """
        self.acycle(-1)
        self.show_attr_table()

    def shorten(self):

        key = self.current()
        
        value = getattr(self.ball, key)
        if len(value) > 1:
            print(f'popping {value[0]}')
            value.popleft()
            print(f'new head {value[0]}')


class RoutineRunner(InteractBase):

    def __init__(self, ball):

        super().__init__(ball)
        

    def set_filters(self):

        for ix, coro in enumerate(self.attrs):
            self.add_filter(str(ix), getattr(self.ball, coro))

    def set_attrs(self):
        
        coros = inspect.getmembers(self.ball, inspect.iscoroutinefunction)
        self.attrs = deque(coro[0] for coro in coros)
        self.set_filters()

    async def runner(self, coro):

        await self.put(coro, 'run')
            
class Wrapper:

    def __init__(self, ball):

        if isinstance(ball, dict):
            self.__dict__.update(ball)
            self.attrs = self.__dict__.keys()

        if hasattr(ball, 'colnames'):
            names = {}
            for name in ball.colnames:
                names[name] = ball[name]
            
            self.__dict__update(names)
            self.attrs = ball.colnames
        else:
            self.attrs = ball.__dict__.keys()

        # keep a reference to the full thing
        self.ball = ball

    def __getattr__(self, attr):

        return getattr(self.ball, attr)
        
    def __setattr__(self, attr, value):

        self.ball.__setattr__(attr, value)

    
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
        self.road_runner = RoutineRunner(self.path[-1])

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
        self.add_filter('j', self.routine_runner)

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

    async def routine_runner(self):
        """ Go into routine runner mode """

        current = self.current()

        rr = self.road_runner

        if current is not rr.ball:
            rr.set_ball(current)

        rr.interact()
        
        if rr not in self.path:
            self.path.append(rr)
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
        msg = []
        for sheep, key, callback in self.generate_key_bindings(name=name):
            doc = doc_firstline(callback)
            msg.append([key, sheep.__class__.__name__,  doc])

        textmsg = '\n'.join([' '.join(x) for x in msg])
        print(textmsg)
        # hmm -- there's a queue of help messages somewhere
        # maybe should use that for some other display.

        hq = self.select('help')
        if hq.qsize() < hq.maxsize - 1:
            # if the queue is getting full, then we don't want to hang here.
            # curiously, maxsize - 1 is the critical size at which it seems
            # to hang.
            print('submitting to help')
            self.put_nowait(msg, 'help')

    async def helper(self):
        """ Task to run if you want help on the carpet 

        One day it will be easy to start and stop this.
        """
        from blume.legend import Grid

        while True:
            msg = await self.get('help')

            try:
                if not msg: msg = 'no message'
                if isinstance(msg, str):
                    msg = [[msg]]

                widths = get_widths(msg)
                
                tab = table.table(
                    self.carpet.foreground, cellText=msg, bbox=(0,0,1,1),
                    cellLoc='center',
                    colWidths=widths)

                tab.set_alpha(0.6)
                self.carpet.add_table(tab)
                self.carpet.draw()

            except:
                print(msg)
                print("HELPER CAUGHT AN EXCEPTION")
                print_exc()
                continue



    async def start(self):
        """ Start things going 

        FIXME: make it simple
        """
        for sheep, info in self.flock.nodes.items():
            if sheep is self:
                continue
                
            # just start all the nodes 
            dolly = sheep.start()
            if inspect.iscoroutine(dolly):
                await dolly
            
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
        current = self.current()
                
        nodes = [n for n in self.flock.nodes if n not in self.path]

        if nodes:
            self.path.append(nodes[0])
        
        self.put_nowait('done', 'gkr')
        
        self.put_nowait(str(self.current()), 'help')

    async def previous_ball(self):
        """ Move focus to previous """
        await self.up()

    async def up(self):
        """ Move up path """
        if len(self.path) > 1:
            del self.path[-1]

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

        

    def __str__(self):

        return f'shepherd of flock degree {len(self.flock)}'

def doc_firstline(value):
    """ Return first line of doc """

    doc = value.__doc__
    if doc:
        return doc.split('\n')[0]
    else:
        return value.__name__

    
def get_widths(msg):

    # find max len of string for each column
    ncols = len(msg[0])

    widths = []
    for col in range(ncols):
        widths.append(max([len(str(x[col])) for x in msg]) + 3)

    # now normalise
    total = sum(widths)
    widths = [x/total for x in widths]
    return widths

    
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
    
    def __init__self(self, path=None, data=None, **meta):
        """ Turn what we are given into a table """

        self.path = path or Path()
        self.data = data or None
        self.meta = meta
        
    async def show(self):
        """ Table show yourself """
        plottype = meta['type'] or self.plot
        
    async def scatter(self, table=None):
        ax = await TheMagicRoundAbout.get()

    async def plot(self, table=None):
        pass

    async def imshow(self):
        pass


class TableCounts:
    """ Yet another table-like thing

    This one counts things in grids and shows
    images of those things, with imshow.
    """

    def __init__(self, width=512, height=512,
                 minx=0, maxx=1,
                 miny=0, maxy=1,
                 title=None,
                 xname='x', yname='y',
                 inset=None,
                 colorbar=False):
        
        self.grid = np.zeros((width, height))
        self.minx = minx
        self.maxx = maxx
        self.miny = miny
        self.maxy = maxy
        self.title = title
        self.xname = xname
        self.yname = yname
        self.inset = inset or (1, 1, -1, -1)
        self.colorbar = colorbar
        self.axes = {}

    def reset(self, width=None, height=None):

        if width is None: width = self.grid.shape[0]
        if height is None: height = self.grid.shape[1]
        self.grid = np.zeros((width, height))
        
    def update(self, xlist, ylist, weight=1):

        width, height = self.grid.shape

        xinc = (self.maxx - self.minx) / width
        yinc = (self.maxy - self.miny) / height

        for ix, (x, y) in enumerate(zip(xlist, ylist)):

            xbucket = int((x-self.minx) // xinc)
            ybucket = int((y-self.miny) // yinc)
            if xbucket <= 0 or xbucket >= width:
                continue
            if ybucket <= 0 or ybucket >= height:
                continue

            try:
                wgt = weight[ix]
            except:
                wgt = weight
                
            self.grid[ybucket, xbucket] += wgt

    async def show(self, xname=None, yname=None):

        tmra = TheMagicRoundAbout
        x, y, xx, yy = self.inset

        xname = xname or self.xname
        yname = yname or self.yname

        # take inset
        grid = self.grid[x:xx, y:yy]

        # adjust minx, maxx, miny, maxy for inset
        minx, maxx, miny, maxy = self.minx, self.maxx, self.miny, self.maxy
        height, width = self.grid.shape
        
        xinc = (maxx - minx) / width
        yinc = (maxy - miny) / height
        minx += xinc * x
        maxx += xinc * xx
        miny += yinc * y
        maxy += yinc * yy
        
        height, width = grid.shape

        xnorms = grid / (sum(grid)+1)
        ynorms = (grid.T / (sum(grid.T)+1)).T

        ax = await tmra.get()
        extent = (minx, maxx, miny, maxy)

        cmap = random_colour()
        axes = self.axes
        ax.set_xlabel(self.xname); ax.set_ylabel(self.yname)
        ax.imshow(xnorms,
                  origin='lower',
                  aspect='auto',
                  extent=extent,
                  cmap=cmap)

        title = self.title or f'{xname} v {yname}'
        ax.set_title(f'{title}, normalised by {xname}')
        ax.show()
        axes['xnorms'] = ax

        ax = await tmra.get()
        ax.imshow(ynorms,
                  origin='lower',
                  aspect='auto',
                  extent=extent,
                  cmap=cmap)
        ax.set_title(f'{title}, normalised by {yname}')
        ax.show()
        axes['ynorms'] = ax

        # see what a grid sample looks like
        csize = width * height
        choices = list(range(csize))
        weights = grid.flatten()
        
        if sum(weights):
            sample = random.choices(choices, weights=weights, k=1566)
            ax = await tmra.get()

            xinc = (maxx - minx) / width
            yinc = (maxy - miny) / height

            xx = np.array([minx + ((x%width) * xinc) for x in sample])
            yy = np.array([miny + ((int(x/width)) * yinc) for x in sample])

            ax.scatter(xx, yy)
            ax.show()
            axes['sample'] = ax

        ax = await tmra.get()
        ax.set_title(f'{title}')
        img = ax.imshow(grid,
                   origin='lower',
                   aspect='auto',
                   extent=extent,
                   cmap=cmap)
        ax.show()
        if self.colorbar:
            await ax.show_colorbar(img)
        
        axes['nonorm'] = ax

        return axes

def show():

    try:
        plt.show(block=False)
    except:
        # sometimes backends have show without block parameter?  
        plt.show()

        

class Carpet(Ball):
    """ Current status: history just added, wormholes opened.

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
        self.meta = {}

        self.history = deque(maxlen=random.randint(25, 50))

        self.axes = deque()
        self.lookup = dict()
        #self.savefig_dpi = 3000
        #self.image = plt.figure(constrained_layout=True, facecolor='grey')
        self.image = plt.figure()

        self.background = self.image.add_axes((0,0,1,1))
        self.foreground = self.image.add_axes((0.1,0.1,.8, .8), zorder=1)
        self.foreground.patch.set_alpha(0.)
        self.foreground.axis('off')
        self.foreground.set_alpha(.8)
        self.table_edge_colours = deque((None, 'k'))
        self.tables = deque()
        
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
        self.add_filter('<', self.lower_alpha)
        self.add_filter('>', self.raise_alpha)
        self.add_filter('t', self.toggle_table)
        self.add_filter('T', self.toggle_table_edges)

    def lower_alpha(self):

        alpha = self.foreground.get_alpha()
        alpha *= 0.9
        
        for tab in self.tables:
            if tab.get_visible():
                tab.set_alpha(alpha)
                
        self.foreground.set_alpha(alpha)
        
        self.draw()

    def raise_alpha(self):

        alpha = self.foreground.get_alpha()
        alpha = min(1., alpha/0.9)

        for tab in self.tables:
            if tab.get_visible():
                tab.set_alpha(alpha)
        
        self.foreground.set_alpha(alpha)
        self.draw()


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

        #print('history', len(self.history), 'rotate', n)

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

    async def replay_history(self, maxback=None):

        # take a copy of the current history
        hlen = len(self.history)
        hlen = min(max(*self.size), hlen)
        

        # need to throw away one axis in the queue
        await self.get()
        for hh in range(hlen):
            await self.history_rotate(1)
        
    def toggle_expand2(self):
        """ ask figure to expand the axes to fill the space """
        fig = self.image

        fig.subplots_adjust(hspace=0, wspace=0)
        
    def toggle_expand(self, names=None):
        """ Toggle making each axis fill its space """
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

            await sleep(self.sleep * 10)

    async def start(self):
        
            
        # start some tasks to keep things ticking along
        #watch_task = await curio.spawn(self.watch())
        print("carpet starting tasks")
        poll_task = spawn(self.poll())
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

        # subplot_mosaic has had a per_subplot_kw since 3.7
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
            if ax is self.background or ax is self.foreground:
                continue

            try:
                axe = self.lookup[id(ax)]
            except:
                print(f'WHOA {id(ax)} {type(ax)} missing from lookup')
                raise

                
            if (axe not in self.history and
                axe not in showing):
                ax.figure.delaxes(ax)

                meta_key = tuple(axe.meta.items())
                if meta_key in self.meta:
                    self.delete_axe(self.meta[meta_key])
                else:
                    axe.clear()

                #print(f'adding {meta_key} to carpet.meta {len(self.meta)}')
                self.meta[meta_key] = axe

    def delete_axe(self, axe):
        
        if hasattr(axe, 'img'):
            axe.img.remove()

        del self.lookup[id(axe.delegate)]

        
        
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

        self.draw()

    def draw(self):
        """ trigger a redraw """
        self.image.canvas.draw_idle()
    

    def hide(self, axe):

        if axe.get_visible():
            axe.set_visible(False)

    def add_table(self, table):
        """ Add a table to the carpet and show it """

        if self.tables:
            self.tables[-1].set_visible(False)

        self.tables.append(table)
        colour = self.table_edge_colours[-1]
        for cell in table._cells.values():
            cell.set_edgecolor(colour)

        table.set_alpha(self.foreground.get_alpha())
        self.foreground.set_visible(True)

        self.draw()

    def toggle_table(self):
        """  Show/hide table """
        tab = self.tables[-1]
        if self.tables:
            visible = tab.get_visible()
            tab.set_visible(not visible)
            self.foreground.set_visible(not visible)
            
        self.draw()

    def toggle_table_edges(self):

        tab = self.tables[-1]

        self.table_edge_colours.rotate()
        colour = self.table_edge_colours[-1]
        
        for cell in tab._cells.values():
            cell.set_edgecolor(colour)

        self.draw()

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

    Try to accommodate coroutines and couroutine functions.
    
    """

    print('dog chasing ball:', ball)
    runs = 0

    if isinstance(ball, Ball):
        run = ball.run
    else:
        run = ball

    sleepy = 0
    while True:
        if hasattr(ball, 'paused'):
            paused = ball.paused
        else:
            paused = False
            
        if not paused:
            try:
                # gymnastics to deal with callables coroutines
                # or coroutinefunctions
                if inspect.iscoroutine(run):
                    result = run
                else:
                    result = run()

                # now if it is a coroutine
                if inspect.iscoroutine(result):
                    #print(f'canine awaits result {runs} for {ball}')
                    await result
            
                runs += 1

                if hasattr(ball, 'sleep'):
                    sleepy = ball.sleep
                await sleep(sleepy)

            except asyncio.CancelledError:
                print(f'cancelled running of {ball} after {runs} runs')
                raise

            except:
                print_exc()
                raise

class Task:

    def __init__(self,
                 task,
                 args=None,
                 kwargs=None,
                 active=True,
                 plot=True):

        self.task = task
        self.args = args or []
        self.kwargs = kwargs or {}
        self.active = active
        self.result = None
        self.plot = plot

    def __repr__(self):

        return f'{self.task.__doc__}, active={self.active}'

    def toggle(self):

        self.active = not self.active
        
    async def run(self):

        if not self.active:
            return

        args = self.args.copy()
        if self.plot:
            ax = await magic.TheMagicRoundAbout.get()
            args = [ax] + args

        result = self.task(*args, **self.kwargs)

        if inspect.iscoroutine(result):
            result = await result

        self.result = result

    
class Tasks:

    def __init__(self, tasks=None):

        self.tasks = deque()

    def add(self, task, plot=False, *args, active=True, **kwargs):
        """ Add a task """
        self.tasks.append(Task(task, args, kwargs, active, plot))

    def set_active(self, value=True):

        for task in self.tasks:
            self.active = value        

    async def run(self, sleep=0):
        """ Run the tasks """
        for task in self.tasks:
            await task.run()

            # take a nap between tasks
            await asyncio.sleep(0)
            


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

def runner(ball):

    TheMagicRoundAbout.put_nowait(ball, 'run')
    
                
if __name__ == '__main__':
    
    
    run(runme(), with_monitor=True)
