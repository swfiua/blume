"""
Example using legend.Legendary


"""
from collections import deque

from matplotlib import pyplot

from blume import legend, magic, farm

class Legend(magic.Ball):

    def __init__(self, data):

        super().__init__()

        self.data = data

        self.transpose = True
        self.modes = deque(['fixed', 'equal', 'expand'])
        self.aligns = deque(['center', 'left', 'top', 'right', 'bottom', 'baseline'])

    async def run(self):

        ax = pyplot.subplot()

        grid = legend.Grid(
            self.data,
            transpose=self.transpose,
            mode=self.modes[0],
            align=self.aligns[0])
        
        ax.add_artist(grid)
        
        await self.put()

    def draw(self, renderer=None):

        self.leg.draw(renderer)


    
import argparse
from blume import farm as land
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--cols', type=int, default=6)

args = parser.parse_args()

cols = args.cols

words = [x.strip() for x in legend.__doc__.split()]

words = np.array(words)
words = words[:cols * cols].reshape(cols, cols)
print(words)

leg = Legend(words)

farm = land.Farm()

farm.add(leg)

farm.shep.path.append(leg)

magic.run(land.start_and_run(farm))
