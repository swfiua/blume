"""
Display data from Gaia

All thanks to the European Space Agency for data and images such as this.

https://gea.esac.esa.int/archive/documentation/GDR2/large/cu9/cu9gat_skydensity_healpix_logcount_gal_large.png

This module uses the `astroquery.gaia` submodule to query the Gaia database.

I am still finding my way around the data (almost June 2020).

It is a record of over a billion observations.

Many variables, along with error estimates too.

The plan for now is to download a bunch of random samples, asynchronously.

Save each sample in `fits` format.

And then explore the data.

Data downloaded is cached in the current directory.

The same is checked for data from a previous run and that will be read in
before loading any further data.

Would be good to be able to be able to share bunches of data, that is part of
the more general problem of distributed data.

See `-bunch` and `-topn` command line options for how to control how many
bunches are downloaded and how big each bunch is.

The idea here is to look into the question, of just where is the sun?

Specifically, where is it relative to the galactic centre?

Recognising that the galactic centre is a bit of a puzzle itself.

"""
import argparse
from collections import deque

from astropy.table import Table, vstack
from astropy import coordinates
from astropy import units as u
from .magic import Ball

import curio
from curio import queue

import healpy as hp
import numpy as np
from matplotlib import pyplot as plt
import math
import random
from pathlib import Path

from . import magic

from . import farm as fm

TABLE = 'gaiadr2.gaia_source'
TABLE_SIZE=1692919134

COLUMNS = ('source_id', 'random_index', 'ra', 'dec', 'parallax', 'radial_velocity')

FILENAME = 'radial_velocity2.fits'


def get_sample(squeal, filename=None):

    if len(squeal) > 1000:
        print(f'squeal: {squeal[:360]} .. {squeal[-180:]}')
    else:
        print(squeal)


    from astroquery.gaia import Gaia
    job = Gaia.launch_job_async(
        squeal,
        output_file=str(filename),
        dump_to_file=filename)

    print('*' * 49)
    print(job)
    job.wait_for_job_end()
    print(job)
    
    return job.get_results()


class Milky(Ball):

    def __init__(self, bunch=1, topn=1): 

        super().__init__()

        self.bunches = deque()
        self.nbunch = bunch
        self.bix = 0
        self.topn = topn
        self.level = 6
        self.plots = False
        self.sagastar = False
        self.clip = 25  # either side

        self.keys = deque(('r_est', 'radial_velocity'))

        self.coord = deque((('C', 'G'), 'C', 'E'))
        

    async def start(self):
        """ start async task to read/download data """
        self.bunchq = curio.PriorityQueue()

        # load any bunches there are
        # for now, keep them separate
        path = Path()
        for bunch in path.glob('bunch*.fits'):
            if bunch.exists():
                table = Table.read(bunch)
                self.bunches.append(table)

            if len(self.bunches) == self.nbunch:
                break

            await curio.sleep(0)

        # launch a task to get more bunches, if needed
        self.sampler = await curio.spawn(self.get_samples())

    async def get_samples(self):

        while len(self.bunches) < self.nbunch:

            squeal = self.get_squeal()


            # take sample
            bid = len(self.bunches)
            path = Path(f'bunch_{bid}.fits')
            bunch = await curio.run_in_process(get_sample, squeal, str(path))

            self.bunches.append(bunch)
            
    def get_squeal(self):

        columns = (', ').join(COLUMNS)
        columns = '*'
        table = TABLE
        sample = tuple(range(self.topn))
        squeal = f'select top {self.topn} {columns} from {table} where random_index in {sample}'
        squeal = f'select top {self.topn} gaia_healpix_index(6, source_id) as healpix_6 count(*) from {table} where random_index in {sample}'
        squeal = f'select top {self.topn} count(*) from {table} where random_index in {sample}'

        example_squeal = "SELECT TOP 10"
        "gaia_healpix_index(6, source_id) AS healpix_6,"
        "count(*) / 0.83929 as sources_per_sq_deg,"
        "avg(astrometric_n_good_obs_al) AS avg_n_good_al,"
        "avg(astrometric_n_good_obs_ac) AS avg_n_good_ac,"
        "avg(astrometric_n_good_obs_al + astrometric_n_good_obs_ac) AS avg_n_good,"
        "avg(astrometric_excess_noise) as avg_excess_noise"
        "FROM gaiadr1.tgas_source"
        "GROUP BY healpix_6"


        columns = 'source_id, ra, dec, phot_g_mean_mag, r_est, r_lo, r_hi, teff_val, radial_velocity, random_index'

        #inflate = 1
        #sample = tuple(random.randint(0, TABLE_SIZE)
        #               for x in range(self.topn * inflate))
        modulus = 997
        
        squeal = (
            f'SELECT top {self.topn} {columns} ' +
            #f'SELECT {columns} ' +
            'FROM external.gaiadr2_geometric_distance ' +
            'JOIN gaiadr2.gaia_source USING (source_id) ' +
            #'WHERE r_est < 1000 AND teff_val > 7000 ')
            #f'WHERE MOD(random_index, {modulus}) = 0')
            #f'WHERE random_index in {sample} ' +
            f'WHERE radial_velocity is not null ' +
            f'AND MOD(random_index, {modulus}) = {len(self.bunches)}')


        #squeal = f'select top 100000 {columns} from {table} where radial_velocity IS NOT NULL'
        #squeal = f'select top 1000 {coumns} from {table} where mod(random_index, 1000000) = 0'

        return squeal

    async def next_bunch(self):

        self.bix


    async def run(self):

        if not self.bunches:
            print(self.sampler.where())
            return
        
        level = self.level

        # join up the bunches
        #table = vstack(self.bunches)
        
        nside = 2 ** level

        #print(hpxmap)
        # Sag A*
        sagra = coordinates.Angle('17h45m20.0409s')
        sagdec = coordinates.Angle('-29d0m28.118s')
        print(f'sag A* {sagra.deg} {sagdec}')

        npix = hp.nside2npix(nside)
        hpxmap = np.zeros(npix, dtype=np.float)
        radvel = np.zeros(npix, dtype=np.float)
        #radvel += 2000

        ra = np.zeros(0)
        dec = np.zeros(0)
        dist = np.zeros(0)
        cdata = np.zeros(0)
        
        key = self.keys[0]

        # get a table
        table = self.bunches.popleft()
        self.bunches.append(table)

        if True:

            if self.level != level:
                print('LEVEL CHANGE', level, self.level)
                level = self.level
                nside = 2 ** level

                npix = hp.nside2npix(nside)
                hpxmap = np.zeros(npix, dtype=np.float)
                radvel = np.zeros(npix, dtype=np.float)

            # Rotate the view
            rot = hp.rotator.Rotator(coord=self.coord[0], deg=False)

            rra, ddec = rot(
                [x['ra'] for x in table],
                [x['dec'] for x in table])

            ra = np.concatenate((ra, rra))
            dec = np.concatenate((dec, ddec))
            dist = np.concatenate((dist, [x['r_est'] for x in table]))
            
            badval = 1e20
            count = 0

            # set up healpix array view
            for row in table:

                ix = row['source_id'] >> 35
                ix //= 4**(12 - level)
                #ix = row['source_id'] >> 35

                rv = row[key]

                hpxmap[ix] += 1

                if rv != badval:
                    radvel[ix] = rv
                    count += 1

            print(f'observations: {count}  mean: {radvel.mean()}')

            dkey = table[key]
            print(dkey.mean())
            
            dkey.fill_value = dkey.mean()

            
            dkey.fill_value = -400
            print(dkey.min())
            cdata = np.concatenate((
                cdata,
                dkey.filled()))
                
            #hp.mollview(radvel / hpxmap, coord=('C', 'G'), nest=True)
            #ma = hp.ma(radvel, badval)
            #from collections import Counter
            #ma.mask = np.logical_not(ma.mask)

            #mask = radvel != 1e20
            #print(Counter(mask).most_common(4))

            #radvel = np.where(mask, radvel, np.zeros(npix))

            vmin, vmax = np.percentile(radvel, (self.clip, 100-self.clip))
            coord = self.coord[0]
            hp.mollview(radvel,
                        coord=coord,
                        nest=True,
                        cmap=magic.random_colour(),
                        max=vmax,
                        min=vmin)

            

            if self.sagastar:
                # show a point at the origin
                plt.scatter([0.0], [0.0])

                hp.projplot(sagra.deg, sagdec.deg,
                            'ro',
                            lonlat=True,
                            coord=coord)
        
            #hp.graticule()
            await self.put(magic.fig2data(plt))

            hp.mollview(hpxmap, coord=coord, nest=True,
                        cmap=magic.random_colour())

            await self.put(magic.fig2data(plt))


            if self.plots:
                plt.close()

                plt.scatter(table['ra'], table['r_est'])
                await self.put(magic.fig2data(plt))
        
                plt.scatter(table['dec'], table['r_est'])
                await self.put(magic.fig2data(plt))

            plt.close()
            fig = plt.figure()
            fig.add_subplot(111, projection='polar',
                            facecolor='grey')

            dist = dist.clip(max=6000)


            vmin, vmax = np.percentile(cdata, (self.clip, 100-self.clip))
            plt.scatter(dec,
                        dist,
                        s=0.1,
                        c=cdata.clip(vmin, vmax),
                        cmap=magic.random_colour())
            plt.colorbar()
            #await self.put(magic.fig2data(plt))
            await curio.sleep(self.sleep)


    async def rotate_view(self):
        """ Galactic or Equator? """
        if self.coord == ('C', 'G'):
            self.coord = 'C'

        elif self.coord == 'C':
            self.coord = 'E'
        else:
            self.coord = ('C', 'G')
            


        

async def run(args):

    milky = Milky(args.bunch, args.topn)

    farm = fm.Farm()
    farm.add(milky)

    # farm strageness, whilst I figure out how it should work
    # add to path to get key events at start 
    farm.shep.path.append(milky)

    await farm.start()

    await farm.run()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-bunch', type=int, default=1)
    parser.add_argument('-topn', type=int, default=10)


    curio.run(run(parser.parse_args()))
    

    
    
