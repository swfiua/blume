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

import curio


from .tkloop import EventLoop


class PigFarm:
    """ Connections to the outside world """

    def __init__(self, meta=None, events=None):

        self.data = curio.UniversalQueue()

        # currently, a list of things being managed
        self.piglets = deque()
        self.tasks = curio.UniversalQueue()

        self.current = None

        # mapping of events to co-routines
        self.event_map = {}
        self.create_event_map()

        # this probably needs to be a co-routine?
        self.eloop = EventLoop()

        self.tasks.put(self.eloop.run())
        displays = getattr(self.eloop, 'displays', [])
        for output in displays:
            self.piglets.put(output)


    def add_event_map(self, event, coro):
        """ Add a binding to the event map 
        
        Over-writes existing one if for same event
        """

        self.event_map[event] = coro

    def create_event_map(self):
        """ Bindings of characters to coroutines """

        self.add_event_map('p', self.previous)
        self.add_event_map('n', self.next)
        self.add_event_map('h', self.help)
        self.add_event_map('q', self.quit)


    def status(self):

        print('builds: ', self.builds.qsize())
        print('tasks::', self.piglets.qsize())
        print(self.current)


    def add(self, pig, kwargs=None):

        kwargs = kwargs or {}
        print('pigfarm adding', pig, kwargs.keys())

        self.builds.put((pig, kwargs))

    def toplevel(self):
        """ Return toplevel piglet """
        return self.eloop.app.winfo_toplevel()

    async def start(self):
        """ Start the farm running 
        
        This should do any initialisation that has to
        wait for async land.
        """


    async def start_piglet(self):
        """ Start the current piglet running """

        self.current.pack(fill='both', expand=1)
        self.current_task = await spawn(self.current.run())

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

        tkloop.Help(msg)

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

        # spawn a task for each piglet

        # spawn a task to deal with keyboard events

        # spawn a task to deal with mouse events

        # ... spawn tasks to deal with any events
        print(self.quit_event)
        builder = await curio.spawn(self.build())

        while True:
            while self.piglets.qsize():
                # spawn a task for each piglet
                piglet = await self.piglets.get()

                print('spawning', piglet)

                await spawn(piglet)

            # wait for an event
            #event = await self.event.get()
            #print(self, event)

            # cycle through the widgets
            print()
            #self.next()
            #await curio.sleep(1)

            event = await self.event.get()

            await self.process_event(event)

            #print(event, type(event))

            print('eq', self.event.qsize())


    async def run(self):

        self.quit_event = curio.Event()

        runner = await spawn(self.tend())

        await self.quit_event.wait()

        print('over and out')

        await runner.cancel()

        print('runner gone')


    async def process_event(self, event):
        """ Dispatch events when they come in """

        coro = self.event_map.get(event)

        if coro is None and self.current:
            coro = self.current.event_map.get(event)

        if coro:
            await coro()
        else:
            print('no callback for event', event)




class Carpet:

    def __init__(self):

        self.top = tkapp.Top()

        self.queues = {}
        self.width = 480
        self.height = 6400

    async def add_queue(self, name):
        """ Add a new image queue to the carpet """
    
        qq = curio.UniversalQueue()
        self.queues[name] = qq

        self.qname = name

        return qq, self.width, self.height

    def display(self, ball):
        """ """
        width, height = self.width, self.height

        image = ball.project('', quantise=False)
        print('xxxxxxxxxx', type(image), image.shape)
        image = Image.fromarray(image)
        image = image.resize((int(width), int(height)))

        self.phim = phim = ImageTk.PhotoImage(image)

        xx = int(width / 2)
        yy = int(height / 2)
        self.canvas.create_image(xx, yy, image=phim)

    async def run(self):

        while True:
            if not self.paused:
                ball = await self.queues[self.qname].pop()
                self.display(ball)
                
            await curio.sleep(self.sleep)

        
class PlotImage(Pig):
    """ An image widget

    This is just a wrapper around matplotlib FigureCanvas.
    """
    def __init__(self, parent, axes=[111], dpi=100, **kwargs):

        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvas

        super().__init__(parent)

        fig = Figure(dpi=dpi, **kwargs)
        self.image = FigureCanvas(fig, master=self)
        self.image._tkcanvas.pack(expand=1, fill=tkinter.BOTH)

        #self.toolbar.update()
        #self.toolbar.pack(expand=0)
        if axes is None:
            axes = []

        self.subplots = []
        for axis in axes:
            self.axes = fig.add_subplot(axis)
            self.subplots.append(self.axes)
            
        self.fig = fig


    def __getattr__(self, attr):

        return getattr(self.image, attr)

    def dark(self):

        self.fig.set_facecolor('black')
        self.fig.set_edgecolor('white')
        pass

    def load_data(self, data):

        self.data = data

    def compute_data(self):
        """ Over-ride to get whatever data you want to see
        
        """
        self.data = pandas.np.random.randint(0,100, size=100)


    async def run(self):
        
        self.compute_data()
        self.plot()


        
