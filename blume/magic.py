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

from collections import deque, defaultdict

import curio

import numpy as np

from PIL import Image

import matplotlib

from matplotlib import figure

from matplotlib import pyplot as plt

import networkx as nx

from .teakhat import Hat, Help


class Farm:
    """ Connections to the outside world """

    def __init__(self, meta=None, events=None):

        # currently, a list of things being managed
        self.balls = deque()
        self.running = set()

        self.current = None

        self.hats = []

        # mapping of events to co-routines
        self.gfarm = GeeFarm()

        self.radii = RoundAbout()
        
        # wonder what happens here?
        # self.balls.appendleft(self.gfarm)

        self.event_map = dict(
            p=self.previous,
            n=self.next,
            h=self.help,
            q=self.quit)


        # start the farm going
        hat = Hat()
        carpet = Carpet()

        self.add_node(carpet, background=True)
        self.add_node(hat, background=True, hat=True)

        self.add_edge(carpet, hat)
        #self.add_edge('hat', carpet)

        # for now merge carpet events  -- need to sort events a little
        # follow the magic roundabout
        self.event_map.update(carpet.event_map)

        self.carpet = carpet

        
    def __getattr__(self, attr):

        return getattr(self.gfarm, attr)


    def status(self):

        self.show()

    def setup(self):
        """ Process the trees, set up all the connections 

        If it is here ... maybe it's because not figured out where
        it really belongs.
        """
        for node in self.nodes:
            data = self.nodes[node]
            if 'hat' in data:
                self.hats.append(node)

        # hmm maybe this.. add it to itself...
        self.add_edge(self.gfarm, self.carpet)
                

        for edge in self.edges:
            start, end = edge
            qname = self.edges[edge].get('name')
            sname = qname or 'outgoing'
            ename = qname or 'incoming'

            print('joining', start, end, sname, ename)
            if hasattr(end, ename):
                setattr(start, sname, getattr(end, ename))
            elif hasattr(start, sname):
                # this case is tricky
                # for now just do the case where a one to many
                # shares its outputs
                setattr(end, ename, getattr(start, sname))
            else:
                # This is where a magic roundabout
                # would come in handy .. but then above would be different
                # start or end might be just strings
                queue = self.radii.select(name=ename)
                
                if isinstance(start, str):
                    # cross fingers this gets fixed by some later magic
                    pass
                else:
                    setattr(start, sname, queue)

                if isinstance(end, str):
                    # again, what to do?
                    pass
                else:
                    setattr(end, ename, queue)
            

    async def start(self):
        """ Start the farm running 
        
        This should do any initialisation that has to
        wait for async land.
        """
        for node in self.nodes:
            print('farm.start starting', node)
            print(type(node))
            await curio.spawn(node.start())


        for node in self.nodes:
            data = self.nodes[node]
            background = data.get('background')
            if background:
                print('farm starting background task', node)
                if hasattr(node, 'run'):
                    runner = await curio.spawn(self.runner(node))
                    self.running.add(runner)
            else:
                self.balls.appendleft(node)
            
    async def runner(self, node=None):
        """ runner for node.run and more

        This was an an attempt to factor out some boiler plate from 
        run methods.

        so run has turned into "do one iteration of what you do"

        and runner here is managing pausing, and has a curious obsession
        with the incoming queue if you have one.

        I guess it is checking the in-tray if there is one.

        then running anyway and then taking a short nap.

        Now we could loop round doing timeouts on queues and then firing
        off runs.

        With a bit more work when building things ... self.radii time?
        """

        node = node or self.current

        print('Farm running node:', str(node))
        while True:
            if not node.paused:

                #incoming = getattr(node, 'incoming', None)
                if 'incoming' in node.ins:
                    node.ball = await node.incoming.get()

                await node.run()

            await curio.sleep(node.sleep)

    async def run_node(self):
        """ Start the current node running """

        # set current out queue to point at
        #self.current.out = self.viewer.queue

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
        if len(self.balls) == 0 and not self.current: return
        print('current', self.current)
        if self.current:
            self.balls.append(self.current)

            await self.stop_node()

        self.current = self.balls.popleft()
        await self.run_node()


    async def previous(self):
        """ Show previous
        Connect to previous node, whatever that may be.
        """
        if len(self.balls) == 0 and not self.current: return
        print('going to previous', self.current)
        if self.current:

            self.balls.appendleft(self.current)

            await self.stop_node()

        self.current = self.balls.pop()
        await self.run_node()



    async def run(self):

        print('Farm starting to run')
        self.quit_event = curio.Event()

        runners = []
        for hat in self.hats:
            runner = await curio.spawn(self.radii.tend(
                queue=hat.events, coro=self.process_event))
            runners.append(runner)

        # select next node
        await self.next()

        await self.quit_event.wait()

        print('over and out')

        for runner in runners:
            await runner.cancel()

        print('runner gone')


    async def process_event(self, event):
        """ Dispatch events when they come in """

        coro = None
        if self.current:
            if hasattr(self.current, 'event_map'):
                coro = self.current.event_map.get(event)
                
        print('EVENT', event)
        if coro is None:
            coro = self.event_map.get(event)

        if coro:
            await coro()
        else:
            print('no callback for event', event, type(event))

class Ball:
    
    def __init__(self):

        self.ball = None
        self.paused = False
        self.sleep = .1
        self.ins = set()
        self.outs = set()

        # grid related
        self.size = 1
        self.pos = 0

        self.image = None

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


    def __getattr__(self, attr):
        """ Delegate to hub or Round
        """
        return getattr(self.hub, attr)
        

    def dump(self):

        print(f' nodes: {self.hub.number_of_nodes()}')
        print(f' edges: {self.hub.number_of_edges()}')

        hub = self.hub
        for item in hub.nodes:
            print('degree', hub.degree[item], hub[item])

        for edge in self.hub.edges:
            print(edge)

    async def start(self):

        pass
    
    async def run(self):

        print('MAGIC TREE FARM')

        # delegated to hub
        fig = plt.figure()
        nx.draw(self.hub)

        await self.outgoing.put(fig2data(plt))
        print('qsize', self.outgoing.qsize())


class RoundAbout(Ball):
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

    async def tend(self, queue=None, name=None, coro=None):
        """ A co-routine to mind a queue and pass stuff on to another """

        queue = queue or self.select(name)

        print('TENDING', name, coro)

        while True:
            event = await queue.get()

            await coro(event)


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

        


class Carpet(Ball):

    def __init__(self):

        super().__init__()

        self.ball = None
        
        # grid related
        self.size = 1
        self.pos = 0

        self.image = None
        self.ins.add('incoming')

        self.event_map.update(dict(
            m=self.more,
            l=self.less))

        
    async def more(self):
        """ Show more pictures """
        self.size += 1
        self._update_pos()
        self.image = None
        print(f'more {self.size}')

    async def less(self):
        """ Show fewer pictures """
        if self.size > 1:
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
    #facecolor = 'white'
    if hasattr(fig, 'get_facecolor'):
        facecolor = fig.get_facecolor()

    # no renderer without this
    image = io.BytesIO()
       
    fig.savefig(image, facecolor=facecolor, dpi=200)

    return Image.open(image)


# example below ignore for now
class MagicPlot(Ball):
    """ Use a Ball to plot.
    
    FIXME: make this one more interesting.
    """
    async def add(self):
        """ Magic Plot key demo  """
        print('magic key was pressed')

        # now what to add?
        return math.pi + math.e

    async def start(self):

        print('magic plot started')
        self.event_map.update(dict(
            a=self.add))

        self.fig = figure.Figure()
        self.ax = self.fig.add_subplot(111)

        # temp hack
        #self.incoming = None

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

    magic_plotter = MagicPlot()

    farm.add_edge(magic_plotter, farm.carpet)

    farm.dump()

    print('set up the farm .. move to start for added thrills? or not?') 
    farm.setup()

    fstart = await curio.spawn(farm.start())

    print('farm running')
    runner = await farm.run()

    
        
if __name__ == '__main__':
    
    
    curio.run(run())
