"""Queues, pipes, graphs and things

I have been puzzling over the magic module for a while, trying to get
to the core of what is going on.

The idea is to have a graph of objects that communicate with each
other just by pushing and pulling objects from queues.

Things seem manageable so long as each object just has a single input
or output queue.

So the objects consume a stream of objects and also generate a stream,
just like a unix filter.

A typical object might sit waiting for something to appear in a queue,
then do some work and perhaps push some output to its output queue.

How to plumb everything together?

The previous code, in a roudabout way, solved this by having a
directed graph of objects.

For each edge it just sets up a relay.

Suppose the edge is from A to B, then the relay simply waits for A to
push objects to its output queue and simply pushes the object onto B's
input queue.

This works fine so long as the graph is static.

But I would really like the graph to be dynamic, add a new node,
change an edge etc, and not have too much break.

I would really like something that just watches all the queues and
decides for itself how to connect everything up.

Sometimes it seems helpful to have multiple input, or output
queues. But here things really start to get more complicated.

The code tried to support this, but the relaying of messages suddenly
seems to get very much more complicated.

Things are not too bad if the communication splits into separate
graphs for each queue name.

The problem is that objects would appear to have to agree on what
queue names to use for what sort of objects.

On the one hand, I want to create a bunch of objects that know very
little about each other, they just consume whatever, and produce their
thing.

At the same time 

"""

from collections import defaultdict, Counter

from matplotlib import artist, figure, pyplot

import curio

import random

def random_queue():

    return curio.UniversalQueue(maxsize=random.randint(5,30))

class Ball:
    """  
    
    
    """

    def __init__(self):
        pass
        

class Borg:

    _shared_state = {}
    def __init__(self):

        self.__dict__ = self._shared_state


        

class RoundAbout(Borg):
    """ Pass self around.

    """
    def __init__(self):

        super().__init__()

        if not hasattr(self, 'queues'):
            self.queues = defaultdict(random_queue)
            self.filters = defaultdict(dict)

        self.counts = Counter()
        
    
    async def put(self, item, name=None):

        qq = self.queues[name]

        await qq.put(item)

    async def get(self, name=None):

        qq = self.queues[name]

        result = await qq.get()

        return result


    def add_filter(self, key, coro, name='keys'):

        self.filters[name][key] = coro


    def select(self, name=None, create=True):
        """ pick a q 
        
        create: if True, create if missing -- actually seems to create
        regardless, why not?
        """
        return self.queues[name]



