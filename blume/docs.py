""" Show docs for things.
"""

from collections import deque

from blume import magic, table

class Docs(magic.Ball):


    def __init__(self, objects=None):

        super().__init__()
        self.objects = deque(objects)

    async def run(self):

        ax = await self.get()

        msg = self.objects[0].__doc__
        
        tab = table.table(ax, cellText=[[msg]], bbox=(0,0,1,1),
                          cellColours=[['moccasin']],
                          cellLoc='center')
        foo = tab[0,0]
        foo.set_text_props(multialignment='center', ha='center')
        foo.set_text_props(multialignment='center', ha='left')
        ax.axis('off')
        ax.show()
        self.objects.rotate()

