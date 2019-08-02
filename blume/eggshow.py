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

        bans = ['embedding', '_runner', 'tick_labels']
        
        plt.show = show
        bads = set()
        while True:
            if not self.paused:
                idx = random.randint(0, len(self.paths) - 1)
                path = self.paths[idx]

                if str(path) in bads:
                    continue

                for ban in bans:
                    if ban in str(path):
                        bads.add(str(path))
                    
                if str(path) in bads:
                    continue

                print(path)
                try:
                    exec(path.open().read())
                except:
                    print('BAD ONE', path)
                    bads.add(str(path))
                    continue
            
                await self.outgoing.put(fig2data(plt))

            plt.close()

            await curio.sleep(self.sleep * 10)

def show():

    print('NO SHOW TODAY')



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
