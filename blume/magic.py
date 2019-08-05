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

import io

from pathlib import Path

from collections import deque

import curio

import numpy as np

from .tkloop import EventLoop, Top, Help

from PIL import Image

import matplotlib

from matplotlib import figure


class PigFarm:
    """ Connections to the outside world """

    def __init__(self, meta=None, events=None):

        self.data = curio.UniversalQueue()

        # currently, a list of things being managed
        self.piglets = deque()
        self.tasks = []

        self.current = None

        # mapping of events to co-routines
        self.event_map = dict(
            P=self.previous,
            N=self.next,
            h=self.help,
            q=self.quit)


        self.eloop = EventLoop()

        # create a task to run the event loop
        self.tasks.append(self.eloop.run())


    def status(self):

        print('tasks::', self.piglets.qsize())
        print(self.current)

    async def create_carpet(self):

        # fixme -- want a new top level each time, I think????
        # Also why is carpet special?
        carpet = Carpet(self.eloop.toplevel())
        self.tasks.append(carpet.run())

        # for now merge carpet events
        self.event_map.update(carpet.event_map)
        self.carpet = carpet
        return carpet


    def add(self, piglet):

        self.piglets.appendleft(piglet)

    async def start_tasks(self):
        while self.tasks:
            await curio.spawn(self.tasks.pop())

    async def start(self):
        """ Start the farm running 
        
        This should do any initialisation that has to
        wait for async land.
        """

        await self.start_tasks()
        
        pigs = []
        for piglet in self.piglets:
            pig = await curio.spawn(piglet.start())
            pigs.append(pig)

        await curio.gather(pigs)
            

    async def start_piglet(self):
        """ Start the current piglet running """

        # set current out queue to point at
        #self.current.out = self.viewer.queue
        
        self.current_task = await curio.spawn(self.current.run())

    async def stop_piglet(self):
        """ Stop the current piglet running """

        await self.current_task.cancel()
        self.current.pack_forget()

    async def help(self):
        """ Show help """
        print('Help')

        keys = {}
        if self.current:
            keys = self.current.event_map.copy()
            print('current keys:', keys)

        keys.update(self.event_map)
        msg = ''
        for key, value in sorted(keys.items()):
            msg += '{} {}\n'.format(key,
                                    self.doc_firstline(value.__doc__))

        Help(msg)

    def doc_firstline(self, doc):
        """ Return first line of doc """
        if doc:
            return doc.split('\n')[0]
        else:
            return "????"
        

    async def quit(self):
        """ quit the farm """

        await self.quit_event.set()

    async def next(self):
        """ Show next

        Connect to next piglet, whatever that may be
        """
        if not len(self.piglets): return
        print('current', self.current)
        if self.current:
            self.pigets.append(self.current)

            await self.stop_piglet()

        self.current = self.piglets.popleft()
        await self.start_piglet()


    async def previous(self):
        """ Show previous 

        Connect to next piglet, whatever that may be.
        """
        if not len(self.piglets): return
        print('going to previous', self.current)
        if self.current:

            self.piglets.appendleft(self.current)

            await self.stop_piglet()

        self.current = self.piglets.pop()
        await self.start_piglet()



    async def run(self):

        self.quit_event = curio.Event()

        runner = await curio.spawn(self.tend())

        # select next piglet
        await self.next()

        await self.quit_event.wait()

        print('over and out')

        await runner.cancel()

        print('runner gone')


    async def tend(self):
        """ Make the pigs run """

        while True:
            event = await self.eloop.events.get()

            await self.process_event(event)


    async def process_event(self, event):
        """ Dispatch events when they come in """

        print('EVENT', event)
        coro = self.event_map.get(event)

        if coro is None and self.current:
            if hasattr(self.current, 'event_map'):
                coro = self.current.event_map.get(event)

        if coro:
            await coro()
        else:
            print('no callback for event', event, len(event))


class Carpet:

    def __init__(self, top=None):

        self.top = top
        self.ball = None
        self.paused = False
        self.sleep = .1

        # grid related
        self.size = 1
        self.pos = 0

        self.image = None
        
        self.iqname = 'incoming'
        self.oqname = 'outgoing'
        self.incoming = None
        self.outgoing = None

        # ho hum update event_map to control carpet
        self.event_map = dict(
            s=self.sleepy,
            w=self.wakey,
            m=self.more,
            l=self.less)
        self.event_map[' '] = self.toggle_pause

    async def more(self):
        """ Show more pictures """
        self.size += 1
        self._update_pos()
        self.image = None
        print(f'more {self.size}')

    async def less(self):
        """ Show fewer pictures """
        self.size -= 1
        self._update_pos()
        self.image = None
        print(f'less {self.size}', id(self))
    
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

    async def set_incoming(self, queue, name=None):
        """ Set the carpet incoming queue. """ 
        self.incoming = queue
        if name:
            self.iqname = name

    async def set_outgoing(self, queue, name=None):
        """ Set the carpet outgoing queue to. """
        self.outgoing = queue
        if name:
            self.oqname = name

    async def run(self):

        print('Carpet running')
        while True:
            if not self.paused:
                if self.incoming is None:
                    continue
                
                print(f'CARPET waiting for plots from {self.iqname}')
                print('idcheck', id(self))
                print(f'{id(self.incoming)} size {self.incoming.qsize()}')
                self.ball = await self.incoming.get()

                print(type(self.ball), self.ball.width, self.ball.height)

                if self.outgoing is not None:
                    await self.outgoing.put(self.ball)

                # hmm. need to re-think what belongs where
                # also maybe this method is "runner" and "run" is just
                # the inner loop?
                if self.top:
                    self.display()

            await curio.sleep(self.sleep)

    def display(self):

        if self.ball is None:
            return
        
        print('WOWOWO got a  ball to display', self.size)
        print(f"BALL ID: {id(self.ball)} qsize: {self.incoming.qsize()}")
        ball = self.ball

        sz = self.size

        if self.image is None:
            width, height = ball.width, ball.height
            self.image = Image.new(mode='RGB', size=(width * sz, height * sz))

        width = int(self.image.width / sz)
        height = int(self.image.height / sz)

        print('WWW', width, ball.width)
        print('HHH', height, ball.height)

        # now paste current image in according to self.pos and size
        ps = self.pos
        self._update_pos()
        xx = ps // self.size
        yy = ps % self.size
        offx = xx * width
        offy = yy * height
        self.image.paste(self.ball.resize((width, height)),
                         (offx,  offy, offx + width, offy + height))
        self.top.display(self.image)
        print('displayed ball', self.ball.width, self.ball.height)

    def _update_pos(self):

        self.pos += 1
        if self.pos >= self.size * self.size:
            self.pos = 0
    

def fig2data(fig):
    """ Convert a Matplotlib figure to a PIL image.

    fig: a matplotlib figure
    return: PIL image

    FIXME? return numpy array of image pixels?
    """

    facecolor = 'black'
    if hasattr(fig, 'get_facecolor'):
        facecolor = fig.get_facecolor()

    # no renderer without this
    image = io.BytesIO()
       
    fig.savefig(image, facecolor=facecolor)

    return Image.open(image)


# example below ignore for now
class MagicPlot(Carpet):
    """ A simple carpet carpet """
    async def add(self):
        """ Magic Plot key demo """
        print('magic key was pressed')

    async def start(self):

        self.event_map.update(dict(
            a=self.add))

        self.fig = figure.Figure()
        self.ax = self.fig.add_subplot(111)

    async def run(self):

        ax = self.ax
        while True:
            ax.clear()
            data = np.random.randint(50, size=100)
            print(data.mean())
            ax.plot(data)
            if self.outgoing:
                await self.outgoing.put(fig2data(self.fig))
                print('qsize', self.outgoing.qsize())

            await curio.sleep(1)

            
async def run():

    farm = PigFarm()

    carpet = await farm.create_carpet()

    iq = curio.UniversalQueue()
    await carpet.set_incoming(iq)

    print(f'image queue: {iq}')
    magic_plotter = MagicPlot()
    await magic_plotter.set_outgoing(iq)

    farm.add(magic_plotter)


    await farm.start()
    await farm.run()
    
        
if __name__ == '__main__':
    
    
    curio.run(run())
