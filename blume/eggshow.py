"""
Handle with care.

Runs any python code it finds in examples folders.

Hopes it is producing matplotlib plots.

If so displays them.

Press h for help.
"""


from blume.magic import Farm, Carpet, Ball, fig2data

import curio

import random

from matplotlib import pyplot as plt
from pathlib import Path

class Examples(Ball):

    async def start(self):

        self.paths = list(
            Path('./examples').glob('**/*.py'))

        print('PATHS', len(self.paths))
        self.bans = ['embedding', '_runner', 'tick_labels']
        
        # not sure this works -- stop others stealing the show
        plt.show = show
        self.bads = set()

    async def run(self):

        idx = random.randint(0, len(self.paths) - 1)
        path = self.paths[idx]
        
        if str(path) in self.bads:
            return

        for ban in self.bans:
            if ban in str(path):
                self.bads.add(str(path))
                    
        if str(path) in self.bads:
            return

        print(path)
        try:
            exec(path.open().read())
        except:
            print('BAD ONE', path)
            self.bads.add(str(path))
            return
            
        await self.outgoing.put(fig2data(plt))

        plt.close()

        return True


def show():

    print('NO SHOW TODAY')



async def run():

    farm = Farm()

    carpet = Carpet()

    iq = curio.UniversalQueue()
    await carpet.set_incoming(iq)
    await carpet.set_outgoing(farm.hatq)
    farm.event_map.update(carpet.event_map)

    examples = Examples()
    await examples.set_outgoing(iq)
    examples.incoming = None

    farm.add(carpet, background=True)
    farm.add(examples)


    starter = await curio.spawn(farm.start())

    print('farm runnnnnnnnnning')
    runner = await farm.run()
    
        
if __name__ == '__main__':
    
    
    curio.run(run())
