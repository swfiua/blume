""" Show docs for things.
"""

from collections import deque

from blume import magic

class Docs(magic.Ball):


    def __init__(self, objects=None):

        super().__init__()
        self.objects = deque(objects)

    def run(self):

        self.select('help').put_nowait(self.objects[0].__doc__)

        self.objects.rotate()

        

        
