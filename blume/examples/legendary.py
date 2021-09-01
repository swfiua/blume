"""Example using legend.Legendary

At this point I am just exploring how the various parameters to the
packers from `offsetbox` interact.

After digging into the whole issue of `matplolib.transforms` I
happened across the LayoutGrid.



"""
from collections import deque

from matplotlib import pyplot, transforms

from blume import legend, magic, farm

class Legend(magic.Ball):

    def __init__(self, data):

        super().__init__()

        self.data = data
        self.fontsize = 6
        self.transpose = True
        self.modes = deque(['fixed', 'equal', 'expand'])
        self.aligns = deque(['center', 'left', 'top', 'right', 'bottom', 'baseline'])

    async def run(self):

        mosaic = 'aaeee;bbbcc;zyxwv'
        mosaic = [[1,2,3],[1,[[4,5], [6,5]],10], [7,8,9]]
        fig = pyplot.figure()
        fig, plots = pyplot.subplot_mosaic(mosaic)

        props = dict(size=self.fontsize)
        
        for key, ax in plots.items():
            ax.set_title(key)

            grid = legend.Grid(
                self.data,
                transpose=self.transpose,
                mode=self.modes[0],
                align=self.aligns[0],
                prop=props)
            ax.add_artist(grid)
        
        await self.put()
        del fig


    
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

data = [[1,2,3],[1,[[4,5], [6,5]],10], [7,8,9]]
foo = pyplot.subplot_mosaic(data)
print(foo)

leg = Legend(words)

farm = land.Farm()

farm.add(leg)

farm.shep.path.append(leg)

magic.run(land.start_and_run(farm))
