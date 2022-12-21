"""
Tankrain Image viewer.

Looks for images in examples folders.

Displays them

Press h for help.
"""
from pathlib import Path
from PIL import Image
import numpy as np
import random

import numpy as np

from collections import deque
import time
import argparse

from blume import magic
from blume import farm


class Train(magic.Ball):

    def __init__(self, path='.'):

        super().__init__()
        
        self.path = Path(path)
        self.scale = 0
        self.size = 1024
        self.rotation = -1
        self.clip = None

        self.boost = 20

        def reverse():
            """ U turn if U want 2 """
            self.rotation *= -1
        self.add_filter('u', reverse)

    async def start(self):

        if self.path.is_file():
            self.paths = [self.path]
        else:
            path = Path(self.path)
            self.paths = list(path.glob('**/*.jpg'))
            self.paths += list(path.glob('**/*.png'))
                
        self.paths = deque(sorted(self.paths))
        
        print('PATHS', len(self.paths))
        self.bans = ['embedding', '_runner', 'tick_labels']

        # not sure this works -- stop others stealing the show
        self.bads = set()

    async def run(self):

        idx = 0
        #if len(self.paths) > 1:
        #    idx = random.randint(0, len(self.paths)-1)

        path = self.paths[idx]
        self.paths.rotate(self.rotation)

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


        w, h = image.size

        scale = self.scale

        if scale == 0:
            scale = min(self.size/w, self.size/h)

        if scale:
            image = image.resize((int(w * scale), int(h * scale)))

        if self.clip:

            image = np.clip(image, 0, self.clip)

        if self.boost:
            image = self.booster(image)
        
        print('publishing', path, image.size, 'entropy:', image.entropy())

        ax = await self.get()
        ax.axis('off')
        ax.imshow(image, cmap=magic.random_colour())
        
        ax.show()


    def booster(self, im):
        """ Scale pixel values in im by self. boost """
        if not self.boost: return im

        ent = im.entropy()
        data = np.array(im.getdata())
        
        data *= int(self.boost)
        data = np.clip(data, 0, 256)
        data = [(int(x), int(y), int(z)) for x,y,z in data]
        im.putdata(data)
        newt = im.entropy()
        print('boost change in entropy:', newt - ent)

        return im

async def run(args):

    fm = farm.Farm()

    examples = Train(args.path)

    fm.add(examples)

    await farm.start_and_run(fm)
    
        
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', default='.')

    args = parser.parse_args()
    magic.run(run(args))
