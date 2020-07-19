"""
Use pycbc to show wave forms for random collisions.
"""

import random, math

import argparse

from blume import magic

from blume import farm as fm

import curio

from matplotlib import pyplot as plt

from pycbc import waveform


class Binary(magic.Ball):


    def __init__(self):

        super().__init__()

        self.sample()

    def sample(self):

        self.m1 = random.randint(2, 80)
        self.m2 = self.m1 * (1 - random.random()/10.)


    def generate_wave(self):

        wf = waveform.get_fd_waveform(
            mass1=self.m1,
            mass2=self.m2,
            approximant='TaylorF2', delta_f=.1, f_lower=20)

        return wf

    async def run(self):

        wf = self.generate_wave()

        nn = len(wf[0])
        ts = waveform.fd_to_td(wf[0])
        
        #plt.plot(ts[int(nn/10):])
        plt.plot(ts)

        plt.title(f"{self.m1} {self.m2}")

        await self.put(magic.fig2data(plt))

        self.sample()



async def run(args):

    bino = Binary()

    farm = fm.Farm()
    farm.add(bino)

    # farm strageness, whilst I figure out how it should work
    # add to path to get key events at start 
    farm.shep.path.append(bino)

    await farm.start()

    await farm.run()

        
if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-m1', type=int, default=1)
    parser.add_argument('-m2', type=int, default=10)


    curio.run(run(parser.parse_args()))


        


