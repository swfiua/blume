"""
healpy and healpix helpers.
"""
import psutil
from math import *
import healpy
import numpy as np

from blume import magic

class PixelCounter(magic.Ball):


    def __init__(self, nside=None, xsize=None, **kwargs):

        super().__init__(**kwargs)

        self.nside = nside or 2 ** 6
        self.xsize = xsize or 1000
        self.coords = magic.deque([['C', 'G'], ['E', 'G'], ['E', 'C'], None])
        self.rot = [pi, 0., 0.]
        self.nest = True

        self.setup()

    def setup(self):
        
        self.pixels = np.zeros(healpy.nside2npix(self.nside))
        self.counts = np.zeros(healpy.nside2npix(self.nside))

    async def reset(self, value=0., ring=True):
        """ reset the pixels """
        self.pixels[:] = value

        if ring:
            self.pixels = healpy.reorder(self.pixels, r2n=True)

    async def ixrange(self):
        """ reset the pixels """
        self.pixels = np.arange(len(self.pixels))

    def ix2pixel(self, ix):

        return ix // (self.nside * self.nside)

    def pix2image(self, rot=None, pixels=None):

        phis = np.linspace(0, 2*pi, self.xsize)
        thetas = np.linspace(0, pi, self.xsize//2)

        theta, phi = np.meshgrid(thetas, phis)

        if pixels is None:
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
        self.counts[ix] += 1


    def showmem(self, label=None):

        ps = psutil.Process()

        if not hasattr(self, 'lastmem'):
            self.lastmem = 0

        current = ps.memory_info().rss
        print(f'{label} {current/1e8:.2} {(current-self.lastmem) / 1e6:.2}')

        self.lastmem = current
            
                    
    async def run(self):


        ax = await magic.TheMagicRoundAbout.get()

        ax.projection('mollweide')
        ax.simplify()

        
        img, theta, phi = self.pix2image()

        
        cmap = magic.random_colour()
        ax.pcolormesh(phi - pi, theta - pi/2, img, cmap=cmap)

        ax.show()

        rot = healpy.Rotator(rot=self.rot, coord=self.coords[0])
        #rot = None
        img, theta, phi = self.pix2image(rot)

        ax = await magic.TheMagicRoundAbout.get()

        ax.projection('mollweide')
        ax.simplify()
    
        ax.pcolormesh(phi-pi, theta - pi/2, img, cmap=cmap)
        
        ax.show()

        # if we were given weights, this should be true
        if (self.pixels != self.counts).any():
            # show the counts
            ax = await magic.TheMagicRoundAbout.get()
            ax.projection('mollweide')
            ax.simplify()
    
            img, theta, phi = self.pix2image(rot, pixels=self.counts)
            ax.pcolormesh(phi-pi, theta - pi/2, img, cmap=cmap)
        
            ax.show()


    def pcolormeshtest(self):
    
        from matplotlib import pyplot
        import time

        fig, ax = pyplot.subplots(subplot_kw=dict(projection='mollweide'))

        
        img, theta, phi = self.pix2image()
        self.showmem('bbbb')


        for x in range(1000):
            self.showmem('loop')
            cmap = magic.random_colour()

            print(len(phi), len(theta), img.shape)
            collection = ax.pcolormesh(phi - pi, theta - pi/2, img, cmap=cmap)

            pyplot.show(block=False)
            time.sleep(1.)
            fig.delaxes(ax)
            #ax.remove()
            print(collection)
            collection.remove()
            fig, ax = pyplot.subplots(subplot_kw=dict(projection='mollweide'),
                                      num=1)

            

if __name__ == '__main__':

    from . import farm
    pc = PixelCounter()
    pc.update(range(len(pc.pixels)), range(len(pc.pixels)))
    farm.run(balls=[pc])


    
