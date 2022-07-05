""" Show docs for things.
"""

from collections import deque

from blume import magic, table

class Docs(magic.Ball):


    def __init__(self, texts=None):

        super().__init__()
        self.texts = deque(texts)

    async def run(self):

        ax = await self.get()

        msg = self.texts[0]
        
        tab = table.table(ax, cellText=[[msg]], bbox=(0,0,1,1),
                          cellColours=[['moccasin']],
                          cellLoc='center')
        foo = tab[0,0]
        foo.set_text_props(multialignment='center')
        ax.axis('off')
        ax.show()
        self.texts.rotate()

