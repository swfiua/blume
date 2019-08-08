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

from PIL import Image

import matplotlib

from matplotlib import figure

import networkx as nx

from .teakhat import Hat, Help

class Farm:
    """ Connections to the outside world """

    def __init__(self, meta=None, events=None):

        # currently, a list of things being managed
        self.nodes = deque()
        self.background = set()
        self.running = set()
        self.hats = set()
        self.hatq = curio.UniversalQueue()

        self.current = None

        # mapping of events to co-routines
        self.event_map = dict(
            p=self.previous,
            n=self.next,
            h=self.help,
            q=self.quit)


        self.hats.add(Hat())


    def status(self):

        print(self.current)

    def add(self, node, background=False):

        if background:
            self.background.add(node)
        else:
            self.nodes.appendleft(node)
        

    async def hat_stand(self):
        """ Pass data on to hats """
        while True:
            event = await self.hatq.get()
            print('hat stand event', event)
            for hat in self.hats:
                await hat.put(event)

    async def start(self):
        """ Start the farm running 
        
        This should do any initialisation that has to
        wait for async land.
        """
        for node in self.nodes:
            print('farm.start starting', node)
            await curio.spawn(node.start())

        for hat in self.hats:
            print('farm.start starting hat', hat)
            await curio.spawn(hat.start())

        await curio.spawn(self.hat_stand())

        for node in self.background:
            print('farm starting background task', node)
            await node.start()
            runner = await curio.spawn(self.runner(node))
            self.running.add(runner)
            
    async def runner(self, node=None):

        node = node or self.current

        print('Farm running node:', str(node))
        while True:
            if not node.paused:
                if node.incoming:
                    #print('no incoming', id(node))
                
                    print(f'runner for {node} waiting for plots from {node.iqname}')
                    print('idcheck', id(node))
                    print(f'{id(node.incoming)} size {node.incoming.qsize()}')
                    node.ball = await node.incoming.get()

                    print(type(node.ball), node.ball.width, node.ball.height)

                await node.run()

            await curio.sleep(node.sleep)

    async def run_node(self):
        """ Start the current node running """

        # set current out queue to point at
        #self.current.out = self.viewer.queue

        runner = getattr(self.current, 'runner', self.runner)
        
        self.current_task = await curio.spawn(self.runner())

    async def stop_node(self):
        """ Stop the current running node """

        await self.current_task.cancel()

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

        Connect to next node, whatever that may be
        """
        if len(self.nodes) == 0 and not self.current: return
        print('current', self.current)
        if self.current:
            self.nodes.append(self.current)

            await self.stop_node()

        self.current = self.nodes.popleft()
        await self.run_node()


    async def previous(self):
        """ Show previous
        Connect to next node, whatever that may be.
        """
        if len(self.nodes) == 0 and not self.current: return
        print('going to previous', self.current)
        if self.current:

            self.nodes.appendleft(self.current)

            await self.stop_node()

        self.current = self.nodes.pop()
        await self.run_node()



    async def run(self):

        print('Farm starting to run')
        self.quit_event = curio.Event()

        runners = []
        for hat in self.hats:
            runner = await curio.spawn(self.tend(hat.events))
            runners.append(runner)

        # select next node
        #await self.next()

        await self.quit_event.wait()

        print('over and out')

        for runner in runners:
            await runner.cancel()

        print('runner gone')


    async def tend(self, queue):
        """ Event handling for the hats  """
                
        while True:
            event = await queue.get()

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
            print('no callback for event', event, type(event))

class GeeFarm:
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
        self.hub = hub or nx.Graph()

        self.hub.add_nodes_from(nodes or set())
        self.hub.add_edges_from(edges or set())

        print(f' nodes: {self.hub.number_of_nodes()}')
        print(f' edges: {self.hub.number_of_edges()}')

    def connect(self):

        hub = self.hub
        for item in hub.nodes:
            print('degree', hub.degree[item])
            continue      
            rab = RoundAbout(source, destination)


class RoundAbout:
    """ 
    A magic queue switch.

    Time for bed, said zebedee 
    """
    pass

    async def put(self, packet):
        pass

    async def get(self):
        pass
        

class Ball:
    
    def __init__(self):

        self.ball = None
        self.paused = False
        self.sleep = .1

        # grid related
        self.size = 1
        self.pos = 0

        self.image = None
        
        self.iqname = 'incoming'
        self.oqname = 'outgoing'
        self.incoming = curio.UniversalQueue()
        self.outgoing = curio.UniversalQueue()

        # ho hum update event_map to control ball?
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

    async def start(self):
        pass

    async def run(self):
        pass


class Carpet(Ball):

    def __init__(self):

        super().__init__()
        
        # grid related
        self.size = 1
        self.pos = 0

        self.image = None

        self.event_map = dict(
            m=self.more,
            l=self.less)

        
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
    

    async def start(self):
        
        pass

    async def run(self):

        # hmm. need to re-think what belongs where
        # also maybe this method is "runner" and "run" is just
        # the inner loop?
        if not self.outgoing:
            print('carpet got nowhere to go')
            return

        if self.ball is None:
            print('carpet got no ball')
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

        # put out in queue for displays
        await self.outgoing.put(self.image)
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
class MagicPlot(Ball):
    """ A simple carpet carpet """
    async def add(self):
        """ Magic Plot key demo """
        print('magic key was pressed')

    async def start(self):

        print('magic plot started')
        self.event_map.update(dict(
            a=self.add))

        self.fig = figure.Figure()
        self.ax = self.fig.add_subplot(111)

        # temp hack
        self.incoming = None

    async def run(self):

        print('magic plot run')
        ax = self.ax
        ax.clear()
        data = np.random.randint(50, size=100)
        print(data.mean())
        ax.plot(data)

        await self.outgoing.put(fig2data(self.fig))
        print('qsize', self.outgoing.qsize())


            
async def run():


    farm = Farm()

    carpet = Carpet()

    # for now merge carpet events
    farm.event_map.update(carpet.event_map)
    farm.add(carpet, background=True)


    #edges = [[MagicPlot(), carpet]]
    #farm = GFarm(edages=edges)
    
    
    iq = curio.UniversalQueue()
    oq = farm.hatq
    await carpet.set_incoming(iq)
    await carpet.set_outgoing(oq)

    # tell farm to connect oq to the hats

    print(f'image queue: {iq}')
    magic_plotter = MagicPlot()
    await magic_plotter.set_outgoing(iq)

    farm.add(magic_plotter)

    print('Farm nodes', farm.nodes)
    
    print('starting farm')
    fstart = await curio.spawn(farm.start())

    print('farm running')
    runner = await farm.run()

    
        
if __name__ == '__main__':
    
    
    curio.run(run())
