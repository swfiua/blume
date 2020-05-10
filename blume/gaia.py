"""
Display data from Gaia

All thanks to the European Space Agency for data and images such as this.

https://gea.esac.esa.int/archive/documentation/GDR2/large/cu9/cu9gat_skydensity_healpix_logcount_gal_large.png

This module uses the `astroquery.gaia` submodule to query the Gaia database.


"""
from astropy.table import Table
from astroquery.gaia import Gaia
from .magic import Ball

import curio
from curio import queue

import healpy as hp
import numpy as np
from matplotlib import pyplot as plt
import math
from pathlib import Path

from . import magic

from . import farm as fm

TABLE = 'gaiadr2.gaia_source'

COLUMNS = ('source_id', 'random_index', 'ra', 'dec', 'parallax', 'radial_velocity')



def get_sample(self):

    columns = (', ').join(COLUMNS)
    table = TABLE
    sample = tuple(range(1,100001))
    squeal = f'select {columns} from {table} where random_index in {sample}'
    #squeal = f'select top 1000 {columns} from {table} where mod(random_index, 1000000) = 0'


    #print(f'squeal: {squeal}')
        
    job = Gaia.launch_job_async(squeal)

    return job.get_results()




class Milky(Ball):

    def __init__(self, table):

        super().__init__()

        self.table = table
        self.level = 1
        
        self.add_filter('z', self.zoom)
        self.add_filter('x', self.xzoom)

    async def run(self):


        level = self.level
        table = self.table
        
        nside = 2 ** level

        indices = hp.ang2pix(
            nside,
            [x['ra'] for x in table],
            [x['dec'] for x in table],
            lonlat=True)
    
        npix = hp.nside2npix(nside)
        print('npix, nside, level', npix, nside, level)


        hpxmap = np.zeros(npix, dtype=np.float)

        for row, index in zip([item for item in table], indices):

            ix = row['source_id'] >> 35
            #ix = row['source_id'] >> 35

            #assert(index == ix)
            hpxmap[ix // 4**(12 - level)] += 1
            #hpxmap[index] += 1

        #print(hpxmap)
        hp.mollview(hpxmap, coord=('C', 'G'), nest=True)

        plt.scatter([0.0], [0.0])
        
        await self.put(magic.fig2data(plt))

    async def zoom(self):

        if self.level < 12:
            self.level += 1

    async def xzoom(self):

        if self.level > 0:
            self.level -= 1

async def run(table):

    milky = Milky(table)

    farm = fm.Farm()
    farm.add(milky)

    await farm.start()

    await farm.run()


if __name__ == '__main__':

    path = Path('tab.fits')
    if path.exists():
        table = Table.read(path, 'fits')

    else:
        table = get_sample()

        # be nice, cache data
        table.write(path, 'fits')

    curio.run(run(table))
    

    
    
