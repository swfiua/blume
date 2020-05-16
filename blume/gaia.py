"""
Display data from Gaia

All thanks to the European Space Agency for data and images such as this.

https://gea.esac.esa.int/archive/documentation/GDR2/large/cu9/cu9gat_skydensity_healpix_logcount_gal_large.png

This module uses the `astroquery.gaia` submodule to query the Gaia database.


"""
import argparse

from astropy.table import Table
from astropy import coordinates
from astropy import units as u
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

FILENAME = 'radial_velocity2.fits'

def get_sample():

    columns = (', ').join(COLUMNS)
    table = TABLE
    sample = tuple(range(1,100001))
    squeal = f'select {columns} from {table} where random_index in {sample}'

    squeal = f'select top 100000 {columns} from {table} where radial_velocity IS NOT NULL'
    #squeal = f'select top 1000 {coumns} from {table} where mod(random_index, 1000000) = 0'


    print(f'squeal: {squeal}')
        
    job = Gaia.launch_job_async(squeal)

    return job.get_results()




class Milky(Ball):

    def __init__(self, table):

        super().__init__()

        self.table = table
        self.level = 6

        self.coord = ('C', 'G')
        
        self.add_filter('z', self.zoom)
        self.add_filter('x', self.xzoom)
        self.add_filter('c', self.rotate_view)

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
        radvel = np.zeros(npix, dtype=np.float)

        key = 'radial_velocity'
        key = 'parallax'
        badval = 1e20
        count = 0
        for row, index in zip([item for item in table], indices):

            ix = row['source_id'] >> 35
            ix //= 4**(12 - level)
            #ix = row['source_id'] >> 35

            rv = row[key]

            hpxmap[ix] += 1

            if rv != badval:
                radvel[ix] = rv
                count += 1

        print('number of observations:', count)
                
        #print(hpxmap)
        coord = self.coord
        #hp.mollview(radvel / hpxmap, coord=('C', 'G'), nest=True)
        #ma = hp.ma(radvel, badval)
        #from collections import Counter
        #ma.mask = np.logical_not(ma.mask)

        #mask = radvel != 1e20
        #print(Counter(mask).most_common(4))

        #radvel = np.where(mask, radvel, np.zeros(npix))

        hp.mollview(radvel, coord=coord, nest=True, cmap='rainbow')
        hp.mollview(hpxmap, coord=coord, nest=True, cmap='rainbow')

        # Sag A*
        sagra = coordinates.Angle('17h45m20.0409s')
        sagdec = coordinates.Angle('-29d0m28.118s')
        print(f'sag A* {sagra.deg} {sagdec}')

        hp.projplot(sagra.deg, sagdec.deg,
                    'ro',
                    lonlat=True,
                    coord=coord)

        hp.graticule()

        plt.scatter([0.0], [0.0])
        
        await self.put(magic.fig2data(plt))


    async def rotate_view(self):

        if self.coord == ('C', 'G'):
            self.coord = 'C'

        elif self.coord == 'C':
            self.coord = 'E'
        else:
            self.coord = ('C', 'G')
            

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

    farm.shep.path.append(milky)

    await farm.start()

    await farm.run()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-data', default=FILENAME)

    path = Path(FILENAME)
    if path.exists():
        table = Table.read(path, 'fits')

    else:
        table = get_sample()

        # be nice, cache data
        table.write(path, 'fits')

    curio.run(run(table))
    

    
    
