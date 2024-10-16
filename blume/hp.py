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
        self.coords = magic.deque([['C', 'G'], ['E', 'G'], ['E', 'C']])
        self.rot = pi
        self.nest = True

        self.reset()

    def reset(self):
        
        self.pixels = np.zeros(healpy.nside2npix(self.nside))

    def ix2pixel(self, ix):

        return ix // (self.nside * self.nside)

    def pix2image(self, rot=None):

        phis = np.linspace(0, 2*pi, self.xsize)
        thetas = np.linspace(0, pi, self.xsize//2)

        theta, phi = np.meshgrid(thetas, phis)

        pixels = self.pixels
        if rot:
            #pixels = pixels[healpy.nest2ring(self.nside, range(len(pixels)))]
            #pixels = pixels[healpy.ring2nest(self.nside, range(len(pixels)))]
            pixels = healpy.reorder(pixels, n2r=True)
            pixels = rot.rotate_map_pixel(pixels)
            pixels = healpy.reorder(pixels, r2n=True)
        
        img = pixels[healpy.ang2pix(self.nside, theta, phi, nest=self.nest)]

        return img, theta, phi

    def update(self, ix, weight=1.):

        try:
            wgt = weight[ix]
        except:
            wgt = weight

        self.pixels[ix] += weight

    async def run(self):


        ax = await magic.TheMagicRoundAbout.get()

        ax.projection('mollweide')

        img, theta, phi = self.pix2image()

        cmap = magic.random_colour()
        ax.pcolormesh(phi - pi, theta - pi/2, img, cmap=cmap)

        ax.show()

        rot = healpy.Rotator(rot=[self.rot, 0.], coord=self.coords[0])

        img, theta, phi = self.pix2image(rot)

        ax = await magic.TheMagicRoundAbout.get()

        ax.projection('mollweide')

        ax.pcolormesh(phi-pi, theta - pi/2, img, cmap=cmap)

        ax.show()


if __name__ == '__main__':

    from . import farm
    pc = PixelCounter()
    pc.update(range(len(pc.pixels)), range(len(pc.pixels)))
    farm.run(balls=[pc])


    
