
import math
import random
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt

from blume import magic
from blume import farm as fm

def mand(c, n=500):

    z = 0

    for i in range(n):
        z = (z * z) + c
        #print(z)
        if abs(z) > 2:
            return i
    return i
    
    
SIZE = 200

class Mandy(magic.Ball):

    def __init__(self):

        super().__init__()

        self.zoom = 1
        #qself.zoom = 6.3202439021e+12
        #self.zoom = 1.
        self.c = -0.563020876489049-0.4636170351705708j
        self.c = -0.6455095986649674-0.3594044503742747j

        self.c = math.sin(random.random()*math.pi*2)
        self.c += math.sin(random.random()*math.pi*2) * 1j
        self.n = 30

    def xfory(self, y):
        

        x2 = ((.75 * .75) - y*y)**0.5
        return -x2
            
            

    async def capture(self):

        ii = np.zeros((SIZE, SIZE))

        zoom = self.zoom

        yy = 0.2
        self.c = self.xfory(yy) + yy * 1j

        #grid1 = np.linspace(c-1/zoom, c, SIZE)
        #grid2 = np.linspace(c, c+1/zoom, SIZE)

        #grid = np.concatenate((grid1, grid2[1:]))

        gridx = np.linspace(-1, 1, SIZE) / zoom
        gridy = np.linspace(-1, 1, SIZE) / zoom
        #print(grid)
        for ix, xx in enumerate(gridx):
            for iy, yy in enumerate(gridy):
                value = mand(self.c + xx + yy * 1j, self.n)
                ii[ix][iy] = value
        return ii

    async def run(self):

        img = await self.capture()

        plt.imshow(img.T, cmap='rainbow')

        
        await self.put(magic.fig2data(plt))

        #self.zoomer(img)
        self.zoom *= 2

    def zoomer(self, img):

        val = img[0][0]
        print(img.shape)

        mmax = 0
        for ix, row1 in enumerate(img[:-1]):
            for row2 in img[1:]:
                delta = abs(row1 - row2)
                dmax = delta.max()
                if dmax > mmax:
                    hitcol = np.argwhere(dmax == delta).min()
                    hitrow = ix
        print('HHH', hitcol, hitrow)

        

        
        

async def run():

    mandy = Mandy()
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

    import curio
    curio.run(run())
