"""Discovery of the day is matplotlib.cbook.CallbackRegistry

I think this can be at the heart of the magic roundabout.

It simply allows you to connect up signals as well as to send them.

So it is a whole event driven framework, with some magic to let the
backend event loop manage things.

Digging deeper (unrelated matplotlib.cbook.__init__.py is a good read) ...

As far as I can tell, the only (?) places there are calls to process
events is in backend event handling code.

For example, to handle key events, backends can just call the
backend_base handler for a key event directly, there is no need to 

"""


from matplotlib import pyplot as plt
import numpy as np

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

        self.fig = plt.figure(layout='constrained')

        self.sleep = 0.1

        # create initial axes
        self.generate_mosaic()

        # Connect canvas key events
        self.fig.canvas.mpl_connect('key_press_event', self.keypress)
        self.fig.canvas.mpl_connect('draw_event', self.draw)

        # start the event loop and display the figure.
        #plt.show(block=False)
        print('Showing figure window')
        self.axes[1].plot(range(10))
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
        mosaic = np.arange(self.size * self.size)
        print(mosaic)
        mosaic = mosaic.reshape((self.size, self.size))
        print(mosaic)
        #for row in range(self.size):
        #    arow = []
        #    mosaic.append(arow)
        #    for col in range(self.size):
        #        arow.append(n)
        #        n += 1
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
        print('key press event', event)
        self.select('stdout').put(event.key)

    def draw(self, key=None):

        canvas = self.fig.canvas
        #canvas.draw_idle()
        canvas.flush_events()
        canvas.start_event_loop(self.sleep)

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
            await self.put(ax, 'axes')


    async def start(self):

        print("Starting teakhat.Hat")
        watch_task = await curio.spawn(self.serve())
        poll_task = await curio.spawn(self.poll())

        self.tasks = TaskGroup([watch_task, poll_task])

    async def run(self):

        while True:
            for key, ax in self.axes.items():
                ax.plot([x * key for x in range(10)])
                

        self.fig.canvas.process('draw_event')

            

if __name__ == '__main__':

    carpet = Carpet()

    curio.run(carpet.run)

        
