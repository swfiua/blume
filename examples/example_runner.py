from blume.magic import PigFarm, MagicPlot, fig2data

import curio

import random

from pathlib import Path

class Examples(MagicPlot):

    async def start(self):

        self.paths = list(
            Path('./examples').glob('**/*.py'))

        print('PATHS', len(self.paths))

    async def run(self):
        from matplotlib import pyplot as plt

        # not sure this works -- stop others stealing the show
        plt.show = show
        while True:
            if not self.paused:
                path = self.paths[random.randint(0, len(self.paths))]

                if 'embedding' in str(path):
                    continue
                print(path)
                try:
                    exec(path.open().read())
                except:
                    print('BAD ONE', path)
                    continue
            
            await self.outgoing.put(fig2data(plt))
            print('qsize', self.outgoing.qsize())

            await curio.sleep(self.sleep * 10)

def show():

    print('n show today')



async def run():

    farm = PigFarm()

    carpet = await farm.create_carpet()

    iq = curio.UniversalQueue()
    await carpet.set_incoming(iq)

    examples = Examples()
    await examples.set_outgoing(iq)

    farm.add(examples)


    await farm.start()
    await farm.run()
    
        
if __name__ == '__main__':
    
    
    curio.run(run())
