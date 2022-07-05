"""
Tankrain Image viewer.

Looks for images in examples folders.

Displays them

Press h for help.
"""
from pathlib import Path
from PIL import Image
import random

from collections import deque
import time
import argparse

from blume import magic
from blume import farm


class Train(magic.Ball):

    def __init__(self, path='.'):

        super().__init__()
        
        self.path = Path(path)

    async def start(self):

        if self.path.is_file():
            self.paths = [self.path]
        else:
            path = Path(self.path)
            self.paths = list(path.glob('**/*.jpg'))
            self.paths += list(path.glob('**/*.png'))
                
        self.paths = deque(self.paths)
        
        print('PATHS', len(self.paths))
        self.bans = ['embedding', '_runner', 'tick_labels']

        # not sure this works -- stop others stealing the show
        self.bads = set()

    async def run(self):

        idx = 0
        #if len(self.paths) > 1:
        #    idx = random.randint(0, len(self.paths)-1)

        path = self.paths[idx]
        self.paths.rotate()

        if str(path) in self.bads:
            return

        for ban in self.bans:
            if ban in str(path):
                self.bads.add(str(path))
                    
        if str(path) in self.bads:
            return

        try:
            image = Image.open(path)
        except:
            print('BAD ONE', path)
            traceback.print_exc(limit=20)
            self.bads.add(str(path))
            return

        print('publishing', path)
        ax = await self.get()
        ax.axis('off')
        #ax.imshow(image, aspect='equal')
        
        t1=time.time()
        ax.imshow(image, aspect='equal')
        t2=time.time()
        print(f'IMSHOW time for {path} {t2-t1}')
        
        ax.show()


async def run(args):

    fm = farm.Farm()

    examples = Train(args.path)

    fm.add(examples)

    await farm.start_and_run(fm)
    
        
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('path', default='.')

    args = parser.parse_args()
    magic.run(run(args))
