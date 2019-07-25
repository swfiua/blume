"""
Matplotlib plus async


mainloop()

queues of images

clients set up their own queues

draw from Q


"""

import curio

class PigFarm:
    """ A pig farm event loop """

    def __init__(self, meta=None, events=None):

        self.event = curio.UniversalQueue()
        self.play = ''

        self.piglet_event = curio.UniversalQueue()

        self.piglets = curio.UniversalQueue()

        self.builds = curio.UniversalQueue()

        self.data = curio.UniversalQueue()

        self.micks = curio.UniversalQueue()

        self.widgets = deque()
        self.current = None
        self.eric = None

        self.create_event_map()

        from karmapi import piglet

        # this probably needs to be a co-routine?
        self.eloop = piglet.EventLoop()
        self.eloop.set_event_queue(self.event)
        self.eloop.farm = self

        self.piglets.put(self.eloop.run())
        displays = getattr(self.eloop, 'displays', [])
        for output in displays:
            self.piglets.put(output)


    def add_event_map(self, event, coro):

        self.event_map[event] = coro

    def create_event_map(self):

        self.event_map = {}
        self.add_event_map('p', self.previous)
        self.add_event_map('n', self.next)
        self.add_event_map('h', self.help)
        self.add_event_map('c', self.show_monitor)
        self.add_event_map('e', self.show_eric)
        self.add_event_map('q', self.quit)


    def status(self):

        print('builds: ', self.builds.qsize())
        print('piglets::', self.piglets.qsize())
        print('micks:', self.micks.qsize())


    def add(self, pig, kwargs=None):

        kwargs = kwargs or {}
        print('pigfarm adding', pig, kwargs.keys())

        self.builds.put((pig, kwargs))

    def add_mick(self, mick):

        self.micks.put(mick)
        #self.piglets.put(mick.start())

    def toplevel(self):
        """ Return toplevel piglet """
        return self.eloop.app.winfo_toplevel()


    async def build(self):
        """ Do the piglet build """

        while True:
            meta, kwargs = await self.builds.get()
            print('building piglet:', meta, kwargs.keys())

            piglet = meta(self.toplevel(), **kwargs)

            self.widgets.append(piglet)

            # let the piglets see the farm
            piglet.farm = self
            print('built', meta, piglet)

            await piglet.start()

    async def start_piglet(self):

        self.current.pack(fill='both', expand=1)
        self.current_task = await spawn(self.current.run())

    async def stop_piglet(self):

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

        piglet.Help(msg)

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
        if not len(self.widgets): return
        print('current', self.current)
        if self.current:
            self.widgets.append(self.current)

            await self.stop_piglet()

        self.current = self.widgets.popleft()
        await self.start_piglet()


    async def previous(self):
        """ Show previous widget """
        if not len(self.widgets): return
        print('going to previous', self.current)
        if self.current:

            self.widgets.appendleft(self.current)

            await self.stop_piglet()

        self.current = self.widgets.pop()
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

        print(f'PLAYYYYY TIME  *{self.play}*')
        for x in self.play:
            await self.event.put(x)
            
            #print(f'playing {x] qsize {self.event.qsize}')
            print(f'{x} xxxx')

        self.play = ''
        
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


    async def show_monitor(self):
        """ Show curio monitor """
        
        from karmapi import milk
        farm = PigFarm()
        farm.add(milk.Curio)
        await spawn(farm.run())

    async def mon_update(self, mon):

        while True:
            #await mon.update()
            await mon.next()
            await sleep(1)

    async def show_eric(self):
        """ Show eric idle """

        if self.eric:
            return
        self.eric = True
        
        from karmapi.eric import  Eric
        farm = PigFarm()
        filename = None
        if self.current:
            filename = inspect.getsourcefile(self.current.__class__)
        farm.add(Eric, dict(filename=filename))

        await spawn(farm.run())

        #farm.toplevel().withdraw()
        

class AppEventLoop:
    """ An event loop

    tk specific application event loop
    """
    def __init__(self, app=None):

        if app is None:
            self.app = Tk()

        self.outputs = []
        self.events = curio.UniversalQueue()
        self.app.bind('<Key>', self.keypress)

    def set_event_queue(self, events):

        self.events = events

    def keypress(self, event):
        """ Take tk events and stick them in a curio queue """
        self.events.put(event.char)
        
        return True

    async def flush(self):
        """  Wait for an event to arrive in the queue.
        """
        while True:

            event = await self.queue.get()

            self.app.update_idletasks()
            self.app.update()


    async def poll(self):

        # Experiment with sleep to keep gui responsive
        # but not a cpu hog.
        event = 0

        nap = 0.05
        while True:

            # FIXME - have Qt do the put when it wants refreshing
            await self.put(event)
            event += 1

            nap = await self.naptime(nap)

            # FIXME should do away with the poll loop and just schedule
            # for some time in the future.
            await curio.sleep(nap)

    async def naptime(self, naptime=None):
        """Return the time to nap """

        if naptime is None:
            naptime = 0.05

        return naptime

    async def run(self):

        poll_task = await curio.spawn(self.poll())

        flush_task = await curio.spawn(self.flush())

        tasks = [flush_task, poll_task]

        await curio.gather(tasks)
    

class Carpet:

    def __init__(self):

        self.queues = {}

    async def add_queue(self, name):
        """ Add a new image queue to the carpet """
    
        qq = curio.UniversalQueue()
        self.queues[name] = qq

        return qq

        
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


        
