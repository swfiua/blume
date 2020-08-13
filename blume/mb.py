
import math
import random
import argparse
from collections import Counter

import numpy as np
from PIL import Image
from matplotlib import pyplot as plt

from blume import magic
from blume import farm as fm

def mand(c, n=300):
    """ Test to see if a point is in the Mandlebrot set """
    z = 0

    for i in range(n):
        z = (z * z) + c

        if abs(z) > 2:
            return i
    return i
    
def npmand(c, n=300):
    """ Mandelbrot numpy version 

    This trades doing a bit of pointless computation for the
    speed up of working on whole numpy arrays.
    """
    z = 0

    results = np.zeros(len(c))
    results = n

    diverged = np.zeros(len(c))
    for i in range(n):

        z = (z * z) + c
        diverged = np.where(abs(z) > 2, i, n)
        results = np.minimum(results, diverged)

    return results
    
    
class Mandy(magic.Ball):

    def __init__(self):

        super().__init__()

        self.zoom = 1
        self.size = 450

        self.seed()
        
        self.add_filter('c', self.reseed)

        self.n = 300

    async def reseed(self):

        self.seed()

    def seed(self):
        
        self.c = 0
        while self.c == 0:
            self.c = seed()

        self.zoom = 1


    async def capture(self):

        size = self.size

        if size == 0:
            size = random.randint(2, 12) * 100
            self.thissize = size
        
        ii = np.zeros((size, size))

        zoom = self.zoom

        yy = 0.2

        c = self.c
        r = c.real
        i = c.imag
        gridx = np.linspace(r-1/zoom, r+1/zoom, size)
        gridy = np.linspace(i-1/zoom, i+1/zoom, size)

        for ix, xx in enumerate(gridx):

            ii[ix] = npmand(xx + (gridy * 1j))
            #for iy, yy in enumerate(gridy):
            #    value = mand(xx + yy * 1j, self.n)
            #    ii[ix][iy] = value

            # keep things responsive
            self.ix = ix
            await curio.sleep(self.sleep/size)
        return ii

    async def run(self):

        img = await self.capture()

        cmap = self.cmap
        if cmap == 'random':
            cmap = magic.random_colour()
            print(cmap)

            # half the time, flip direction of colour map
            if random.random() > 0.5:
                img = -1 * img


        plt.imshow(img.T, cmap=cmap)
        
        await self.put(magic.fig2data(plt))

        #self.zoomer(img)
        self.zoom *= 2

        # re-seed if image is 2 values or less
        counts = Counter(img.flatten())
        print('number of values:', len(counts))
        if len(counts) <= 2:
            self.seed()
        

        

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

    if args.random:
        mandy.cmap = 'random'
    else:
        mandy.cmap = args.cmap

    mandy.size = args.size
    mandy.n = args.n

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
    parser.add_argument('-cmap', default='rainbow')

    args = parser.parse_args()
    import curio
    curio.run(run(args))
