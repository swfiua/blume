
from matplotlib import pyplot as plt
import numpy

from .magic import Ball

from curio import TaskGroup
import curio

class Carpet(Ball):
    """ A hat

    Or a display.  

    This hat gives you a Tk window.

    It runs a Tk event loop, asynchronously (see below).

    It outputs keyboard events.

    display(ball) will do that.

    formerly tk specific application event loop
    """
    def __init__(self):

        super().__init__()

        self.size = 2

        plt.show()
        self.fig = plt.figure(layout='constrained')

        self.sleep = 0.1

        # create initial axes
        self.generate_mosaic()

        # Connect canvas key events
        self.fig.canvas.mpl_connect('key_press_event', self.keypress)

        # start the event loop and display the figure.
        #plt.show(block=False)
        print('Showing figure window')
        plt.show(block=False)

        self.add_filter('+', self.more)
        self.add_filter('=', self.more)
        #self.add_filter('-', self.less)

        #self.add_filter('[', self.history_back)
        #self.add_filter(']', self.history_forward)
        
        #self.add_filter('S', self.save)

    async def more(self):

        self.size += 1

        self.generate_mosaic()

    def generate_mosaic(self):

        mosaic = []
        n = 1
        for row in range(self.size):
            arow = []
            mosaic.append(arow)
            for col in range(self.size):
                arow.append(n)
                n += 1
        print(mosaic)
        self.axes = self.fig.subplot_mosaic(mosaic)
        print(self.axes)
        self.fig.clear()
        
        
        
    def keypress(self, event):
        """ Take keypress events put them out there """

        #print('mosaic carpet handling', event)
        # use select here to get actual magic curio queue
        # where put can magically be a coroutine or a function according
        # to context.
        self.select('stdout').put(event.key)

    def draw(self, key=None):

        self.fig.draw_idle()

    async def poll(self):
        """ Gui Loop """

        # Experiment with sleep to keep gui responsive
        # but not a cpu hog.
        event = 0

        nap = 0.05
        canvas = self.fig.canvas
        while True:
            
            canvas.draw_idle()
            canvas.flush_events()
            canvas.start_event_loop(self.sleep)

            # Would be good to find a Tk file pointer that
            # can be used as a source of events

            await curio.sleep(self.sleep)


    async def serve(self):
        """ Give out axes """

        for key, ax in self.axes.items():
            print('giving away', ax)
            await self.put(ax, dict(type='axes', key=key))


    async def start(self):

        print("Starting teakhat.Hat")
        watch_task = await curio.spawn(self.serve())
        poll_task = await curio.spawn(self.poll())

        self.tasks = TaskGroup([watch_task, poll_task])

    async def run(self):

        await self.tasks.join()

        print("Event loop over and out")



        
