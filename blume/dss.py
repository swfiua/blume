""" de Sitter Space

Are gamma-ray bursts optical illusions?

Robert S Mackay, Colin Rourke.

See notebook for evolving ideas.

Einsteinpy has all sorts of goodies that are helpful here.  I am just starting
to find my way around the project.

The symbolic part has a predefined deSitter metric among others.

It was there I discovered there is a Gödel metric, an exact solution of the
Einstein field equations.

The metric is based on a spinning universe.  Gödel was known to keep asking,
"has the universe started spinning yet?".   

A rotating universe was central to his solution and had some peculiar
properties such as observers being able to see themselves at some time in the
past.  Although, that's what we see every time we look in a mirror.

If our universe is vast beyond the visible and the cosmic microwave background
is a glimmer of what is beyond, then I think we can see the universe spinning.

"""

# we are going to need this
import math
import numpy as np
from matplotlib import pyplot as plt

from traceback import print_exc

# hmm, sympy is a whole universe of stuff
from sympy import *
from einsteinpy.symbolic import predefined

import curio

from blume import magic
from blume import magic
from blume import farm as fm

class Dss(magic.Ball):

    def __init__(self):
        """ initialise """
        super().__init__()

        self.theta = 0.1
        self.phi = 5
        self.size = 50
        self.aaa = magic.modes
        
        self.alpha, self.beta, self.gamma, self.delta = symbols(
            'alpha beta gamma delta')

    def set_abcd(self):

        self.a = (self.alpha + self.beta - self.gamma - self.delta) / 2
        self.b = (self.alpha - self.beta - self.gamma + self.delta) / 2
        self.c = (self.alpha + self.beta + self.gamma + self.delta) / 2
        self.d = (self.alpha - self.beta + self.gamma - self.delta) / 2
        

    def constraints(self):

        print(self.alpha**2 - self.gamma**2 >= 1.)

        print(self.alpha > 0)

        a, b, c, d = self.alpha, self.beta, self.gamma, self.delta

        print((a * b - c * d) <= (a*a - c*c - 1) * (b*b - d*d -1))

        print((a*d - b*c) <= (a*a - c*c - b*b + d*d -1))

    def blue_shift_time(self, alpha=None, delta=None):
        """ """
        a = alpha or self.alpha
        d = delta or self.delta

        etb = sqrt((1+a)/(a+d)) + sqrt((1-d)/(a-d))
        
        return log(etb)

    def deSitter(self):

        return predefined.DeSitter()


    async def run(self):

        size = self.size
        epsilon = 1e-3

        img = np.zeros((size, size))

        for row in range(1, size+1):

            delta = math.cos(math.pi * row/(size+1))
            for col in range(1, size+1):
                alpha = math.cosh(self.phi * col/(size+1))

                try:
                    img[row-1][col-1] = self.blue_shift_time(
                        alpha or epsilon, delta or epsilon)
                except:
                    print_exc()
                    print(alpha, delta)
                    raise
 
            #print(img[row-1])

            await curio.sleep(0)

        ax = await self.get()
        ax.hide_axes()
        
        maps = ax.imshow(img, cmap=magic.random_colour())
        #ax.colorbar(maps)

        ax.show()


async def run():

    dss = Dss()

    dss.set_abcd()
    dss.constraints()

    farm = fm.Farm()
    
    farm.add(dss)
    
    await farm.start()

    print(dss.deSitter())

    farm.shep.path.append(dss)

    await farm.run()
        


if __name__ == '__main__':

    print(help(init_printing))
    init_printing(pretty_print=True)

    curio.run(run(), with_monitor=True)
