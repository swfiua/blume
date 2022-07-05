"""
Use pycbc to show wave forms for random collisions.
"""

import random, math

import argparse

from blume import magic

from blume import farm as fm

from pycbc import waveform


class Binary(magic.Ball):


    def __init__(self):

        super().__init__()

        self.sample()
        self.skip = 0.8
        self.random = True

    def sample(self):

        self.m1 = random.randint(2, 80)
        self.m2 = self.m1 * (1 - random.random()/10.)


    def generate_wave(self):
        """Generate the wave for the current object

        There is much more of pycbc to explore.

        For starters, there is the ring-down phase too.

        For now, this is just the start of the signal, as the frequency
        rises to a peak.

        As the frequency rises to a peak.

        At this point, it is probably worth a look at the actual detection data.

        But for now, it is good to have something that shows the range
        of waves we might expect to see.
        
        """

        wf = waveform.get_fd_waveform(
            mass1=self.m1,
            mass2=self.m2,
            approximant='TaylorF2', delta_f=.1, f_lower=20)

        return wf

    async def run(self):

        wf = self.generate_wave()

        ts = waveform.fd_to_td(wf[0])
        nn = len(ts)

        skip = int(self.skip * nn)

        ax = await self.get()
        ax.plot(ts[skip:])
        
        ax.axis('off')
        #ax.set_title(f"Solar Masses: {self.m1:.1f} {self.m2:.1f}")
        ax.show()

        
        if self.random:
            self.sample()



async def run(args):

    bino = Binary()

    farm = fm.Farm()
    farm.add(bino)

    #bino.m1 = args.m1
    #bino.m2 = args.m2
    #bino.random = args.random

    #  ????
    bino.update(args)

    # farm strageness, whilst I figure out how it should work
    # add to path to get key events at start 
    farm.shep.path.append(bino)

    await farm.start()

    await farm.run()

        
if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-m1', type=float, default=23)
    parser.add_argument('-m2', type=float, default=2.6)
    parser.add_argument('-random', action='store_true')


    magic.run(run(parser.parse_args()))




