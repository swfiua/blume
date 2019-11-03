from tkinter import Tk, ttk, Text, messagebox, TOP, BOTH, Canvas, Button
from PIL import ImageTk, Image

from .magic import Ball

import curio

class Hat(Ball):
    """ A hat

    Or a display.  

    This hat gives you a Tk window.

    It runs a Tk event loop, asynchronously (see below).

    It puts keyboard events into *self.events*

    display(ball) will do that.

    formerly tk specific application event loop
    """
    def __init__(self):

        super().__init__()

        self.top = Tk()
        self.frame = ttk.Frame(self.top)


        self.width = 480
        self.height = 640
        self.sleep = 0.05
        self.ball = Image.new('RGB', (10, 10))
        
        self.frame.pack(side=TOP, expand=1, fill=BOTH)
        self.canvas = Canvas(self.frame, width=self.width, height=self.height)
        self.recalc(width=480, height=640)

        self.canvas.pack(side=TOP, expand=1, fill=BOTH)
        self.canvas.bind("<Configure>", self.on_configure)
        #button = Button(top, text='hello')
        #button.pack()
        
        # Keyboard handling
        self.events = curio.UniversalQueue()
        self.top.bind('<Key>', self.keypress)

    def keypress(self, event):
        """ Take tk events and stick them in a curio queue """
        print('teakhat handling', event.char)
        self.events.put(event.char)
        
        return True

    async def poll(self):

        # Experiment with sleep to keep gui responsive
        # but not a cpu hog.
        event = 0

        nap = 0.05
        while True:
            
            self.top.update_idletasks()
            self.top.update()

            # Would be good to find a Tk file pointer that
            # can be used as a source of events

            await curio.sleep(self.sleep)

    #async def put(self, event):
    #    """ Push gui events into a queue """
    #    if type(event) is int:
    #        print('incoming int', event)
    #        
    #    await self.incoming.put(event)

    async def watch(self):
        """ Get stuff and display it """
        while True:

            ball = await self.get()

            if type(ball) is int:
                print('wtf', ball)
                continue

            self.display(ball)


    def hat(self):
        """ Return a new hat """
        return Hat()


    async def start(self):

        print("Starting teakhat.Hat")
        watch_task = await curio.spawn(self.watch())
        poll_task = await curio.spawn(self.poll())

        self.tasks = [watch_task, poll_task]

    async def run(self):

        await curio.gather(self.tasks)

        print("Event loop over and out")


    def on_configure(self, event):

        print('new window size:', event.width, event.height)
        self.recalc(event.width, event.height)

        # after re-size
        self.display()

    def recalc(self, width, height):

        self.width = width
        self.height = height
        print()
        print('scroll configure', width, height)
        self.canvas.configure(scrollregion=(0, 0, width, height))

    def display(self, ball=None):
        """ """
        width, height = self.width, self.height

        image = ball or self.ball
        self.ball = image
        
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
        
        
