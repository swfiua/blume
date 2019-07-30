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

At the same time, the more you explore the data with plots (thanks matplotlib)
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

import io

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
            p=self.previous,
            n=self.next,
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
        carpet = Carpet(self.eloop.toplevel())
        self.tasks.append(carpet.run())

        self.event_map.update(dict(
            s=carpet.sleepy,
            w=carpet.wakey))
        self.event_map[' '] = carpet.toggle_pause

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

        from karmapi import piglet

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
        """ Show next widget """
        if not len(self.piglets): return
        print('current', self.current)
        if self.current:
            self.pigets.append(self.current)

            await self.stop_piglet()

        self.current = self.piglets.popleft()
        await self.start_piglet()


    async def previous(self):
        """ Show previous widget """
        if not len(self.piglets): return
        print('going to previous', self.current)
        if self.current:

            self.piglets.appendleft(self.current)

            await self.stop_piglet()

        self.current = self.piglets.pop()
        await self.start_piglet()


    async def tend(self):
        """ Make the pigs run """

        while True:
            event = await self.eloop.events.get()

            await self.process_event(event)



    async def run(self):

        self.quit_event = curio.Event()

        runner = await curio.spawn(self.tend())

        await self.next()

        await self.quit_event.wait()

        print('over and out')

        await runner.cancel()

        print('runner gone')


    async def process_event(self, event):
        """ Dispatch events when they come in """

        coro = self.event_map.get(event)

        if coro is None and self.current:
            if hasattr(self.current, 'event_map'):
                coro = self.current.event_map.get(event)

        if coro:
            await coro()
        else:
            print('no callback for event', event, len(event))


class Carpet:

    def __init__(self, top):

        self.top = top
        self.paused = False
        self.sleep = .1
        self.queues = {}

    async def sleepy(self):

        self.sleep *= 2
        print(f'sleepy {self.sleep}')

    async def wakey(self):

        self.sleep /= 2
        print(f'wakey {self.sleep}')

    async def toggle_pause(self):

        print('toggle pause')
        self.paused = not self.paused

    async def add_queue(self, name):
        """ Add a new image queue to the carpet """
    
        qq = curio.UniversalQueue()
        self.queues[name] = qq

        self.qname = name

        return qq, self.top.width, self.top.height

    async def run(self):

        print('Carpet running')
        while True:
            if not self.paused:
                print(f'CARPET waiting for plots from {self.qname}')
                print(f'{id(self.queues[self.qname])}')
                ball = await self.queues[self.qname].get()

                print('WOWOWO got a  ball')
                self.top.display(ball)
                print('displayed ball', ball.width, ball.height)
                
            await curio.sleep(self.sleep)


def fig2data (fig):
    """ Convert a Matplotlib figure to a 4D numpy array with RGBA channels

    fig: a matplotlib figure
    return: a numpy 3D array of RGBA values
    """

    # no renderer without this
    image = io.BytesIO()
    fig.savefig(image, facecolor=fig.get_facecolor())

    return Image.open(image)


# example below ignore for now
class MagicPlot:

    def __init__(self, **kwargs):

        self.out = None

        self.event_map = dict(
            a=self.add)


    async def add(self):
          pass

    async def start(self):
        self.fig = figure.Figure()
        self.ax = self.fig.add_subplot(111)
        

    async def run(self):

        ax = self.ax
        while True:
            ax.clear()
            data = np.random.randint(50, size=100)
            print(data.mean())
            ax.plot(data)
            if self.out:
                await self.out.put(fig2data(self.fig))
                print('qsize', self.out.qsize())

            await curio.sleep(1)


            
async def run():

    farm = PigFarm()

    carpet = await farm.carpet()

    iq, width, height = await carpet.add_queue('teaplot')
    
    print(f'image queue {width} {height}')
    print(f'image queue id {id(iq)}')
    magic_plotter = MagicPlot()
    magic_plotter.out = iq

    farm.add(magic_plotter)


    await farm.start()
    await farm.run()
    
        
if __name__ == '__main__':
    
    
    curio.run(run())
