"""
Handle with care.

Runs any python code it finds in examples folders.

Hopes it is producing matplotlib plots.

If so displays them.

Press h for help.
"""


from blume.farm import Farm
from blume import magic

import random

from matplotlib import pyplot as plt
from pathlib import Path
import argparse
import traceback

class Examples(magic.Ball):

    def __init__(self, args):

        super().__init__()
        
        self.path = Path(args.path)

    async def start(self):

        if self.path.is_file():
            self.paths = [self.path]
        else:
        
            self.paths = list(
                Path(self.path).glob('**/*.py'))

        print('PATHS', len(self.paths))
        self.bans = ['embedding', '_runner', 'tick_labels']

        # not sure this works -- stop others stealing the show
        plt.show = show
        self.bads = set()

    async def run(self):

        ax = await self.get()
        print('got axes', ax)
        ax.plot(range(10))
        ax.show()
        print('done show')
        await magic.sleep(5)
        print('done sleep and show')

        idx = 0
        if len(self.paths) > 1:
            idx = random.randint(0, len(self.paths)-1)

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
            exec(path.open().read(), globals(), locals())
        except:
            print('BAD ONE', path)
            traceback.print_exc(limit=20)
            self.bads.add(str(path))
            return

        print('publishing', path)

        ax = await self.get()
        print('got axes', ax)
        ax.plot(range(10))
        print('show ax')
        ax.show()
        
        ax = await self.get()
        print('got axis for imshow fun')
        try:
            img = magic.fig2data()
            print('showing', img)
            ax.imshow(img)
            print('imshowed')
            ax.show()
        except Exception:
            print('WHOOO imshow failure')
            import traceback
            traceback.print_exc()


def show():
    print('NO SHOW TODAY')


async def run(args):
    """ Don't do things this way until things settle down ..."""

    farm = Farm()

    examples = Examples(args)

    farm.add(examples)

    starter = await farm.start()

    print('farm runnnnnnnnnning')
    runner = await farm.run()
    
        
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('path', default='.')

    args = parser.parse_args()
    magic.run(run(args))
