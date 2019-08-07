from tkinter import Tk, ttk, Text, messagebox, TOP, BOTH, Canvas, Button
from PIL import ImageTk, Image

import curio

class EventLoop:
    """ An event loop

    tk specific application event loop
    """
    def __init__(self, app=None):

        if app is None:
            self.app = Tk()

        self.outputs = []
        self.queue = curio.UniversalQueue()
        self.events = curio.UniversalQueue()
        self.app.bind('<Key>', self.keypress)

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
            
            # Would be good to find a Tk file pointer that
            # can be used as a source of events
            # for now poll just loops push events onto the queue
            # to trigger event flushing with the flush method
            await self.put(event)
            event += 1

            nap = self.naptime(nap)

            # FIXME should do away with the poll loop and just schedule
            # for some time in the future.
            await curio.sleep(nap)

    def naptime(self, naptime=None):
        """Return the time to nap """

        if naptime is None:
            naptime = 0.05

        return naptime

    async def put(self, event):
        """ Push gui events into a queue """
        await self.queue.put(event)

    def toplevel(self):
        """ Return toplevel window """
        return Top(self.app.winfo_toplevel())

    async def run(self):

        print("Starting tkloop.EventLoop.run")

        poll_task = await curio.spawn(self.poll())

        flush_task = await curio.spawn(self.flush())

        tasks = [flush_task, poll_task]

        await curio.gather(tasks)

        print("Event loop over and out")
    

class Top(ttk.Frame):
    """ A very simple top level window """
    def __init__(self, top):

        super().__init__(top)
        self.width = 480
        self.height = 640
        self.pack(side=TOP, expand=1, fill=BOTH)
        self.canvas = Canvas(self, width=self.width, height=self.height)
        self.recalc(width=480, height=640)
        self.queue = None

        self.canvas.pack(side=TOP, expand=1, fill=BOTH)
        self.canvas.bind("<Configure>", self.on_configure)
        #button = Button(top, text='hello')
        #button.pack()

    def on_configure(self, event):

        print('new window size:', event.width, event.height)
        self.recalc(event.width, event.height)

    def recalc(self, width, height):

        self.width = width
        self.height = height
        print()
        print('scroll configure', width, height)
        self.canvas.configure(scrollregion=(0, 0, width, height))

    def display(self, ball):
        """ """
        width, height = self.width, self.height

        image = ball
        image = image.resize((int(width), int(height)))

        self.phim = phim = ImageTk.PhotoImage(image)

        xx = int(width / 2)
        yy = int(height / 2)

        self.canvas.create_image(xx, yy, image=phim)

        # red dot
        self.canvas.create_oval(20, 20, 30, 30, fill='red')

        
        

class Help:

    def __init__(self, msg):

        msg = msg or "Help Me!"
        
        messagebox.showinfo(message=msg)
        
        
