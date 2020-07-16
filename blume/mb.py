
import random
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt

from blume import magic
from blume import farm as fm

def mand(c, n=30):

    z = 0

    for i in range(n):
        z = (z * z) + c
        #print(z)
        if abs(z) > 2:
            return i
    return i
    
    
def foo(c=0, zoom=1):
    x = random.random() / zoom
    y = 1j * random.random() / zoom

    z = mand(c+x+y)
    return x * zoom, y * zoom, z

def foobar(x, y, c, zoom=1):

    z = mand(c+x+(y * 1j))
    return z

SIZE = 500

c = random.random() + 1j 
xwidth = 2.25
c = (random.random() * xwidth) - 2.0
c += 1j * ((random.random() * 2) -1)
c = 1. + 0.5j
c = -0.909 -0.275j
c = -0.563020876489049 + -0.4636170351705708j

print(c)
zoom = SIZE
# while True:
#     ii = np.zeros((SIZE, SIZE))
# 
#     for xx in range(SIZE):
#         for yy in range(SIZE):
#             xxx = xx - SIZE/2
#             yyy = yy - SIZE/2
#             ii[xx][yy] = foobar(xxx/zoom, yyy/zoom, c)
#     zoom *= 2
# 
# 
#     plt.imshow(ii.T, cmap='rainbow')
#     plt.show()
# 

class Mandy(magic.Ball):

    def __init__(self):

        super().__init__()

        self.zoom = SIZE
        self.c = -0.563020876489049-0.4636170351705708j
        self.n = 10


    async def capture():

        ii = np.zeros((2*SIZE, 2*SIZE))

        grid = np.linspace(-1/zoom, 1/zoom, 2*SIZE)
        
        for ix, xx in enumerate(grid):
            for iy,yy in enumerate(grid):
                value = mand(xx + yy * 1j, self.n)

                ii[ix][iy] = value
        return ii

    async def run(self):

        img = await self.capture()

        plt.imshow(img.T, cmap='rainbow')
        await self.put(magic.fig2data(plt))


async def run():

    from .gaia import Milky
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
