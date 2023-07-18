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

    def add_filter(self, key=None, coro=None, name='keys'):

        filters = self.filters[name]
        if key is None:
            for char in coro.__name__:
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
        pass

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

        self.delegate = pax
        self.position(ax)
        self.carpet.lookup[id(pax)] = self

        if hasattr(ax, 'img'):
            ax.img.remove()

        # now delete ax
        ax.remove()

    def simplify(self):

        #self.xaxis.set_visible(False)
        #self.yaxis.set_visible(False)
        self.axis('off')

    def colorbar(self, mappable):

        self.figure.colorbar(mappable, self)

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
            return self.carpet.get_nowait()
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
        await self.put(self, 'run')

    def set_ball(self, ball):

        if not isinstance(ball, Ball):
            try:

                ball = Wrapper(ball)
                attrs = deque(Wrapper.attrs)
            
            except Exception as e:
                print(e)
                print('oops no can interact', ellipsis(repr(ball)))
                return
        else:
            attrs = deque(sorted(vars(ball)))

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
        current = self.current()
        obj = getattr(self.ball, current)
        print('XXXXX re_interact', current, type(obj))

        try:
            obj = await self.to_table(obj)
        except:
            raise
        
        self.history.append(self.ball)
        self.set_ball(obj)
        self.show_current()


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

        if isinstance(ball, dict):
            self.__dict__.update(ball)
            self.attrs = self.__dict__.keys()

        if hasattr(ball, 'colnames'):
            names = {}
            for name in ball.colnames:
                names[name] = ball[name]
            
            self.__dict__update(names)
            self.attrs = ball.colnames
        

        # keep a reference to the full thing
        self.ball = ball


        
            
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
        msg = []
        for sheep, key, callback in self.generate_key_bindings(name=name):
            doc = self.doc_firstline(callback)
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
            self.put_nowait(msg, 'help')

    def doc_firstline(self, value):
        """ Return first line of doc """

        doc = value.__doc__
        if doc:
            return doc.split('\n')[0]
        else:
            return value.__name__
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

                widths = get_widths(msg)
                tab = table.table(
                    ax.delegate, cellText=msg, bbox=(0,0,1,1),
                    cellLoc='center',
                    colWidths=widths)

                foo = tab[0,0]
                foo.set_text_props(multialignment='left')
            except:
                print(msg)
                print("HELPER CAUGHT AN EXCEPTION")
                print_exc()
                continue

            ax.axis('off')
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

def get_widths(msg):

    # find max len of string for each column
    ncols = len(msg[0])

    widths = []
    for col in range(ncols):
        widths.append(max([len(str(x[col])) for x in msg]) + 3)

    # now normalise
    total = sum(widths)
    widths = [x/total for x in widths]
    print('WWWWWWWWWWWW', widths)
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
    
    def __init__self(self, path=None, data=None, meta_data=None):
        """ Turn what we are given into a table """

        self.path = path or Path()
        self.data = data
        self.meta_data = meta_data
        
        """ now what?  look at data with a magic spell and get meta data.
        
        
        """


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

        self.history = deque(maxlen=random.randint(10, 20))

        self.axes = deque()
        self.lookup = dict()
        #self.savefig_dpi = 3000
        #self.image = plt.figure(constrained_layout=True, facecolor='grey')
        self.image = plt.figure()
        print("GOT IMAGE", self.image)

        # for emscripten and html5_canvas
        # need an easy way to use any id as the root element.
        # for now, its 'canvas'
        if hasattr(self.image.canvas, "create_root_element"):
            from js import document
            print('FIGURE CANVAS', self.image.canvas.create_root_element)
            def create_root_element():
                return document.getElementById('canvas')

            # monkey patch
            self.image.canvas.create_root_element = create_root_element
        else:
            print('CANVAS has no create_root_element')
            
        self.background = self.image.add_axes((0,0,1,1))
        try:
            plt.show(block=False)
        except:
            # sometimes backends have show without block parameter?  
            plt.show()

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
        #self.add_filter(' ', self.toggle_pause)


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

    async def replay_history(self):

        # take a copy of the current history
        hlen = len(self.history)

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
            if ax is self.background:
                continue

            try:
                axe = self.lookup[id(ax)]
            except:
                print(f'WHOA {id(ax)} {type(ax)} missing from lookup')
                raise

            if (axe not in self.history and
                axe not in showing and
                hasattr(axe, 'img')):
                
                axe.img.remove()
                ax.figure.delaxes(ax)
                del self.lookup[id(ax)]
                del ax


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

        self.image.canvas.draw_idle()
        

    def hide(self, axe):

        if axe.get_visible():
            axe.set_visible(False)
        

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
                print(f'cancelled running of {ball} after {runs} runs')
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
