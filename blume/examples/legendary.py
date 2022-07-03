"""Example using legend.Legendary

At this point I am just exploring how the various parameters to the
packers from `offsetbox` interact.

After digging into the whole issue of `matplolib.transforms` I
happened across the LayoutGrid.

Now I would like to be able to change the mosaics without losing all
the axes in the process.

"""
from collections import deque

from matplotlib import pyplot, transforms, _layoutgrid

from blume import legend, magic, farm

class Legend(magic.Ball):

    def __init__(self, data):

        super().__init__()

        self.data = data
        self.fontsize = 6
        self.transpose = True
        self.modes = deque(['fixed', 'equal', 'expand'])
        self.aligns = deque(['center', 'left', 'top', 'right', 'bottom', 'baseline'])

        self.mosaics = deque([
            'aaeee;bbbcc;zyxwv',
            'abc'])
            #[[1,2,3],[1,[[11,12], [6,5]],10], [7,8,9]]])


    async def run(self):

        #mosaic = 'aaeee;bbbcc;zyxwv'
        #mosaic = [[1,2,3],[1,[[11,12], [6,5]],10], [7,8,9]]

        #self.carpet = legend.Carpet()

        self.mosaics.rotate()
        mosaic = self.mosaics[0]
        #for xx in self.carpet.fig._localaxes.as_list():
        #    print(id(xx))

        # ask for a mosaic of axes?
        # wish i knew the set of keys
        #await self.put(mosaic, 'mosaic')

        props = dict(size=self.fontsize)

        ax = await self.get()

        #ax.set_title(key)
        #ax.text(.5,.5, str(key))

        #print(ax.get_subplotspec())
        
        grid = legend.Grid(
            self.data,
            transpose=self.transpose,
            mode=self.modes[0],
            align=self.aligns[0],
            prop=props)
        ax.add_artist(grid)
        print('Legend size', grid.get_window_extent(ax.figure._cachedRenderer))
        
        #print('FINAL DRAW', len(fig._localaxes))
        ax.show()



def main():
    from blume import docs
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
    #foo = pyplot.subplot_mosaic(data)
    #print(foo)

    leg = Legend(words)

    farm = land.Farm()

    from gotu import spiral
    farm.add(docs.Docs([spiral]))
    farm.add(leg)

    farm.shep.path.append(leg)
    print(type(magic.run))
    foo = land.start_and_run(farm)
    print('cooroutine', foo)
    magic.run(foo)
    #magic.run(land.start_and_run(farm))

if __name__ == '__main__':
    main()
    
