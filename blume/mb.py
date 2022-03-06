
import math
import random
import argparse
from collections import Counter

import numpy as np
from PIL import Image
from matplotlib import pyplot as plt

from blume import magic
from blume import farm as fm

from blume.magic import sleep

def mand(c, n=300):
    """ Test to see if a point is in the Mandlebrot set """
    z = 0

    for i in range(n):
        z = (z * z) + c

        if abs(z) > 2:
            return i
    return i
    
def npmand(c, n=300, skip=10):
    """ Mandelbrot numpy version 

    This trades doing a bit of pointless computation for the
    speed up of working on whole numpy arrays.
    """
    z = 0

    results = n
    diverged = np.zeros(len(c))

    for i in range(int(n)):

        z = (z * z) + c
        diverged = np.where(abs(z) > 2, i, n)
        results = np.minimum(results, diverged)
        if 1 == i % (n/skip):
            #print(f'npmand yielding {i} {n}')
            yield results

    yield results

    
    
class Mandy(magic.Ball):

    def __init__(self):

        super().__init__()

        self.zoom = 1
        self.size = 450

        self.seed()

        self.add_filter('c', self.reseed)

        self.maxn = 3000
        self.n = self.maxn/10

    async def reseed(self):

        self.seed()

    def seed(self):
        
        self.c = 0
        while self.c == 0:
            self.c = seed()

        self.zoom = 1


    def capture(self):

        size = int(self.size)

        if size == 0:
            size = random.randint(2, 12) * 100
            self.thissize = size
        
        ii = np.zeros((size, size))

        if not self.c:
            self.seed()

        zoom = self.zoom

        yy = 0.2

        c = self.c
        r = c.real
        i = c.imag
        gridx = np.linspace(r-1/zoom, r+1/zoom, size)
        gridy = np.linspace(i-1/zoom, i+1/zoom, size)

        xgrid, ygrid = np.meshgrid(gridx, gridy)

        skip = 10
        n = self.n
        for ix, img in enumerate(npmand(xgrid + (ygrid * 1j), n), skip):
            yield img
            self.ix = ix * (n / skip)
            if ix > self.n:
                break
        

    async def run(self):

        cmap = self.cmap
        if self.random:
            cmap = magic.random_colour()
        flip = random.random() > 0.5

        
        for img in self.capture():

            # half the time, flip direction of colour map
            if flip:
                img = -1 * img


            # re-seed if image is 2 values or less
            counts = Counter(img.flatten())

            if len(counts) > 1:
                ax = await self.get()

                ax.imshow(img.T, cmap=cmap)
        
                ax.show()
                
            await sleep(self.sleep/self.n)

            if len(counts) > self.depth:
                break

            
        #print('number of values:', len(counts))
        if self.n < self.maxn:
            if len(counts) <= 20:
                self.n *= 2

        self.zoom *= 2


        

def seed():
    """ Try and find an interesting poing to zoom in on """

    # pick a random point 
    imag = math.sin(random.random()*math.pi*2) * 1j
    real = math.sin(random.random()*math.pi*2)

    epsilon = 1
    last = 0

    mintrials = 4
    for trial in range(100):
        data = []

        # create a 2*epsilon wide window, centred on the real value
        points = np.linspace(real-epsilon, real+epsilon, 100)
        for x in points:
            data.append(mand(x + imag))

        # find the maximum difference between adjacent points
        data = np.array(data)
        data = data[1:] - data[1]

        hit = data.argmax()

        # centre for next trial at point of maximum delta
        real = (points[hit+1] + points[hit]) / 2

        # shrink the window to one tenth of distance between adjacent points
        epsilon = (points[1] - points[0]) / 10

        if hit == 0:
            break

        last = real + imag

    if trial > mintrials:
        return last

    # I don't normally use recursion, but for Mandlebrot
    # it seems an appropriate paradigm.
    return seed()


async def run(args):

    mandy = Mandy()

    mandy.update(args)

    if args.random:
        mandy.cmap = 'random'

    #mandy.size = args.size
    #mandy.n = args.n
    mandy.modes = magic.modes
    mandy.modes.rotate()


    #milky = Milky()
    farm = fm.Farm()
    farm.add(mandy)
    #farm.add(milky)

    # farm strageness, whilst I figure out how it should work
    # add to path to get key events at start 
    farm.shep.path.append(mandy)

    await farm.start()

    await farm.run()



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-random', action='store_true')
    parser.add_argument('-size', type=int, default=400)
    parser.add_argument('-n', type=int, default=300)
    parser.add_argument('-zoom', type=float, default=1)
    parser.add_argument('-cmap', default='rainbow')
    parser.add_argument('-depth', default=200, type=float)
    parser.add_argument('c', type=complex, nargs='?')

    args = parser.parse_args()
    import curio
    curio.run(run(args))
