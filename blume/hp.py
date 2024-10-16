"""
healpy and healpix helpers.
"""

from math import *
import healpy
import numpy as np

from blume import magic

class PixelCounter(magic.Ball):


    def __init__(self, nside=None, xsize=None, **kwargs):

        super().__init__(**kwargs)

        self.nside = nside or 2 ** 6
        self.xsize = xsize or 1000

        self.pixels = np.zeros(healpy.nside2npix(self.nside))

    def ix2pixel(self, ix):

        return ix // 4**(self.nside)

    def pix2image(self):

        phis = np.linspace(0, 2*pi, self.xsize)
        thetas = np.linspace(0, pi, self.xsize//2)

        theta, phi = np.meshgrid(thetas, phis)

        img = self.pixels[healpy.ang2pix(self.nside, theta, phi, nest=True)]

        return img, theta, phi

    def update(self, ix, weight=1.):

        try:
            wgt = weight[ix]
        except:
            wgt = weight

        self.pixels[ix] += weight

    async def show(self):


        ax = await magic.TheMagicRoundAbout.get()

        ax.projection('mollweide')

        img, theta, phi = self.pix2image()

        ax.pcolormesh(phi - pi, theta - pi/2, img, cmap=magic.random_colour())

        ax.show()


if __name__ == '__main__':

    from . import farm
    pc = PixelCounter()
    pc.update(range(len(pc.pixels)), range(len(pc.pixels)))
    farm.run(balls=[pc])


    
