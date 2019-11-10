"""
Split the farm from magic.

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

from .magic import Ball, RoundAbout, GeeFarm, fig2data, Shepherd
from .mclock2 import GuidoClock

class Farm(Ball):
    """ Connections to the outside world """

    def __init__(self):

        # mapping of events to co-routines
        self.gfarm = GeeFarm()

        # start the farm going
        hat = Hat()
        carpet = Carpet()

        self.shepherd = Shepherd()

        self.add_node(carpet, background=True)
        self.add_node(hat, background=True, hat=True)

        self.add_edge(carpet, hat)

        self.add_edge(self.shepherd, carpet)

        self.carpet = carpet

        self.shepherd.set(self.gfarm.hub)
        
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
                    souts = set()
                    
                else:
                    setattr(start, sname, queue)
                    souts = start.outs

                if isinstance(end, str):
                    # again, what to do?
                    # see what outs start has
                    print(end, souts, end in souts)
                    
                    pass
                else:
                    setattr(end, ename, queue)
            

    async def start(self):
        """ Start the farm running 
        
        This should do any initialisation that has to
        wait for async land.
        """
        print('starting shepherd')
        await self.shepherd.start()

            
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

        if False:
            nx.draw_networkx_nodes(self.hub, pos)
            nx.draw_networkx_edges(self.hub, pos, edgelist=self.hub.edges)
            nx.draw_networkx_labels(self.hub, pos, font_color='blue')
            plt.show()
            # how to from farm ?? self.carpet.(plt)

        await self.shepherd.run()
        return

        
        print('Farm starting to run')
        self.quit_event = curio.Event()

        # select next node
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


class Carpet(Ball):

    def __init__(self):

        super().__init__()

        # grid related
        self.size = 1
        self.pos = 0

        self.image = None

        self.add_filter('m', self.more)
        self.add_filter('l', self.less)

        
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
        ball = await self.get()
        
        if ball is None:
            print('carpet got no ball')
            return
        
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
        self.image.paste(ball.resize((width, height)),
                         (offx,  offy, offx + width, offy + height))

        # put out in queue for displays
        await self.put(self.image)
        print('displayed ball', ball.width, ball.height)


    def _update_pos(self):

        self.pos += 1
        if self.pos >= self.size * self.size:
            self.pos = 0
    


# example below ignore for now
class MagicPlot(Ball):
    """ Use a Ball to plot.
    
    FIXME: make this one more interesting.
    """
    def __init__(self):

        super().__init__()

        #self.outs.add('outgoing')
               
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
    clock = GuidoClock()
    farm.add_edge(magic_plotter, farm.carpet)
    farm.add_edge(clock, farm.carpet)

    print('set up the farm .. move to start for added thrills? or not?') 
    farm.setup()

    print()
    print('DUMP')
    farm.dump()


    fstart = await curio.spawn(farm.start())

    print('farm running')
    runner = await farm.run()

    
        
if __name__ == '__main__':
    
    
    curio.run(run())
