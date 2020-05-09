"""
Display data from Gaia

All thanks to the European Space Agency for data and images such as this.

https://gea.esac.esa.int/archive/documentation/GDR2/large/cu9/cu9gat_skydensity_healpix_logcount_gal_large.png

This module uses the `astroquery.gaia` submodule to query the Gaia database.


"""
from astroquery.gaia import Gaia
from .magic import Ball

import curio
from curio import queue

import healpy as hp
import numpy as np
from matplotlib import pyplot as plt
import math
import pathlib

TABLE = 'gaiadr2.gaia_source'

COLUMNS = ('source_id', 'random_index', 'ra', 'dec', 'parallax', 'radial_velocity')


class Milky(Ball):

    def __init__(self):

        super().__init__()

    def get_sample(self):

        columns = (', ').join(COLUMNS)
        table = TABLE
        sample = tuple(range(1,1001))
        squeal = f'select {columns} from {table} where random_index in {sample}'
        #squeal = f'select top 1000 {columns} from {table} where mod(random_index, 1000000) = 0'


        #print(f'squeal: {squeal}')
        
        job = Gaia.launch_job_async(squeal)

        #print(job.get_results())

        return job

    async def get_results(self, job):

        while not job.is_finished():
            print('checking for job finish')
            await curio.sleep(10)

        return job.get_results()

    async def run(self):


        job = self.get_sample()

        table = await self.get_results(job)

        return table



if __name__ == '__main__':

    milky = Milky()

    table = curio.run(milky.run())

    level = 12
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
        print('xx', index)

        ix = row['source_id'] >> 35 + (2 * (12-level))
        print(index, ix)
        #assert(index == ix)
        #hpxmap[ix] += 1
        hpxmap[index] += 1

    print(hpxmap)
    hp.mollview(hpxmap)

    plt.show()
