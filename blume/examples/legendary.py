"""
Example using legend.Legendary


"""
from blume import legend, magic, farm

class Legend(magic.Ball):

    def __init__(self, data):

        super().__init__()

        self.leg = legend.LegendArray(data)

    async def run(self):

        ax = pyplot.subplot()

        self.leg.axes(ax)
        self.leg.bbox = (0,0,1,1)
        
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
words[:cols * cols].reshape(cols, cols)

leg = Legend(words)

farm = land.Farm()

farm.add(leg)

farm.shep.path.append(leg)

magic.run(land.start_and_run(farm))
