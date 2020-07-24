
import math
import random
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt

from blume import magic
from blume import farm as fm

def mand(c, n=300):
    z = 0

    for i in range(n):
        z = (z * z) + c
        #print(z)
        if abs(z) > 2:
            return i
    return i
    
    
class Mandy(magic.Ball):

    def __init__(self):

        super().__init__()

        self.zoom = 1
        self.size = 300
        #qself.zoom = 6.3202439021e+12
        #self.zoom = 1.
        self.c = -0.6455095986649674-0.3594044503742747j
        
        self.c = -0.5670461646108229 + 0.4654258477789597j
        self.c = -0.563020876489049-0.4636170351705708j

        self.c = -0.8970362544726358 + 0.2308369508463713j

        self.seed()
        
        self.add_filter('c', self.reseed)
            

        #self.c = math.sin(random.random()*math.pi*2)
        #self.c += math.sin(random.random()*math.pi*2) * 1j
        self.n = 300

    async def reseed(self):

        self.seed()

    def seed(self):
        
        self.c = 0
        while self.c == 0:
            self.c = seed()

        self.zoom = 1


    def xfory(self, y):
        

        x2 = ((.75 * .75) - y*y)**0.5
        return -x2
            
            

    async def capture(self):

        size = self.size
        ii = np.zeros((size, size))

        zoom = self.zoom

        yy = 0.2
        #self.c = self.xfory(yy) + yy * 1j

        #c = -0.569999 -.46361179351j
        c = self.c
        r = c.real
        i = c.imag
        gridx = np.linspace(r-1/zoom, r+1/zoom, size)
        gridy = np.linspace(i-1/zoom, i+1/zoom, size)

        for ix, xx in enumerate(gridx):
            for iy, yy in enumerate(gridy):
                value = mand(xx + yy * 1j, self.n)
                ii[ix][iy] = value

            # keep things responsive
            self.ix = ix
            await curio.sleep(self.sleep/size)
        return ii

    async def run(self):

        img = await self.capture()

        cmaps = plt.colormaps()
        cmap = cmaps[random.randint(0, len(cmaps)-1)]
        print(cmap)
        plt.imshow(img.T, cmap=cmap)
        
        await self.put(magic.fig2data(plt))

        #self.zoomer(img)
        self.zoom *= 2

        maxi = img.flatten().max()
        mini = img.flatten().min()

        if maxi == mini:
            self.seed()


        

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

def seed():

    n = 300
    
    imag = math.sin(random.random()*math.pi*2) * 1j

    real = math.sin(random.random()*math.pi*2)

    epsilon = 1
    last = 0
    for trial in range(100):
        data = []
        points = np.linspace(real-epsilon, real+epsilon, 100)
        for x in points:
            data.append(mand(x + imag))
        
        data = np.array(data)
        data = data[1:] - data[1]

        hit = data.argmax()
        real = (points[hit+1] + points[hit]) / 2
        epsilon = (points[hit+1] - points[hit]) / 10
        print(hit, real, epsilon, data[hit])

        if hit == 0:
            break

        last = real + imag

    return last

if __name__ == '__main__':

    import curio
    curio.run(run())
