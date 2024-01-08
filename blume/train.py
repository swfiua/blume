"""
Tankrain Image viewer.

Looks for images in examples folders.

Displays them

Press h for help.
"""
from pathlib import Path
from PIL import Image
import numpy as np
import random
import traceback

import numpy as np

from collections import deque, defaultdict, Counter
import time
import argparse

from blume import magic
from blume import farm


class Train(magic.Ball):

    def __init__(self, args=None):

        super().__init__()

        parser = self.get_parser()

        # sets attributes from parsed args
        self.update(parser.parse_args(args))

        self.extent = None

        def reverse():
            """ U turn if U want 2 """
            self.rotation *= -1
        self.add_filter('u', reverse)
        self.add_filter('d', self.down)
        self.add_filter('b', self.back)

    def get_parser(self):
        """ Use argparse to get arguments from command line """

        parser = argparse.ArgumentParser()
        parser.add_argument('--path', default='.')
        parser.add_argument('--paths', default=[], nargs='+')
        parser.add_argument('--clip', type=float, default=0)
        parser.add_argument('--clipr', type=float, default=0)
        parser.add_argument('--clipg', type=float, default=0)
        parser.add_argument('--clipb', type=float, default=0)
        parser.add_argument('--scale', type=float, default=0)
        parser.add_argument('--size', type=int, default=1024)
        parser.add_argument('--rotation', type=int, default=-1)
        parser.add_argument('--cmap', default=None)
        parser.add_argument('--min_entropy', type=float, default=.0)
        parser.add_argument('--boost', type=float, default=0)
        parser.add_argument('--rgb', action='store_true', default=False)
        
        return parser
        

    async def down(self):

        choices = [x for x in self.path.glob('*') if x.is_dir()]

        if not choices:
            print(self.path, 'has no sub directories')
            parent = self.path.parent
            choices = [x for x in parent.glob('*') if x.is_dir()]

        # pick at rando from choices
        self.path = random.choice(choices)
        print(self.path)
        self.paths = None # trigger reload
        await self.start()
        
    async def back(self):
        self.path = self.path.parent
        print(self.path)
        self.paths = None # trigger reload
        await self.start()

    async def start(self):

        # turn path into a Path
        self.path = Path(self.path)
        
        if not self.paths:
            if self.path.is_file():
                self.paths = [self.path]
            else:
                path = Path(self.path)
                self.paths = list(path.glob('**/*.jpg'))
                self.paths += list(path.glob('**/*.png'))
        else:
            self.paths = [Path(path) for path in self.paths]
        self.paths = deque(sorted(self.paths))
        #self.scan()
        
        print('PATHS', len(self.paths))
        self.bans = ['embedding', '_runner', 'tick_labels']

        # not sure this works -- stop others stealing the show
        self.bads = set()

    def scan(self):
        """ Scan current position

        Idea is a file browser that shows tables so
        you can select what to view.
        
        Build a table.
        """
        paths = self.paths
        suffix = set(x.suffix for x in paths)
        from astropy import table
        tab = []
        colnames = []
        for path in paths:
            parts = path.parts
            fields = path.stem.replace('-', ' ').replace('_', ' ').split()
            row = list(parts[1:]) + list(fields) + [path.suffix]

            tab.append(row)

        tab = table.Table(tab)
        
        self.put_nowait(tab, 'help')
        self.put_nowait(self.table_count(tab), 'help')

    def table_count(self, table, maxrows=None):
        """ Do some counts on a table 
        
        pretty sure there is some sort of table.info.stats()
        """
        from blume import taybell
        msg = []
        counters = defaultdict(Counter)
        for ix, row in enumerate(table):
            if maxrows and ix > maxrows:
                break
            
            for key in row.colnames:
                value = row[key]
                if isinstance(value, np.ma.core.MaskedConstant):
                    value = value.tolist()
                counters[key].update([value])

        topn = 1
        for key in table.colnames:
            for value, count in counters[key].most_common(topn):
                value = taybell.shortify_line(str(value), 20)
                
                msg.append([key, value, count])

        return msg
            
    def get_image(self, path):
        """ Turn path into an image """
        if str(path) in self.bads:
            return

        for ban in self.bans:
            if ban in str(path):
                self.bads.add(str(path))
                    
        if str(path) in self.bads:
            return

        try:
            image = Image.open(path)
            w, h = image.size

            scale = self.scale

            if scale == 0:
                scale = min(self.size/w, self.size/h)

            if scale:
                image = image.resize((int(w * scale), int(h * scale)))

        except:
            # maybe its fits
            if path.suffix == '.fits':
                image = self.fits_open(path)
            else:
                raise
        
        if self.clip:
            image = np.clip(image, 0, self.clip)
        if self.boost:
            image = self.booster(image)

        return image

    def get_rgb(self):
        """ Turn next three paths into an rgb """
        layers = []
        for ix, c in enumerate('rgb'): 
            path = self.paths[ix]
            print("PATH", path)
            image = self.get_image(path)
            print("RGB", image.shape, path)
            clip = getattr(self, 'clip' + c) or self.clip
            if self.clip:
                image.clip(clip)
                image /= clip
            else:
                image /= image.max()

            layers.append(image[::-1].T)
            #layers.append(image.T)
            self.paths.rotate(self.rotation)

        rgb = np.array(layers).T
        print('RRRRRRRRRRRRRRR', rgb.shape)
        (c,w,h) = rgb.shape
        self.rgbi = rgb
        
        return rgb
    
    async def run(self):

        #if len(self.paths) > 1:
        #    idx = random.randint(0, len(self.paths)-1)


        path = self.paths[0]
        self.paths.rotate(self.rotation)

        if self.rgb:
            image = self.get_rgb()
            print('rgb image shape', image.shape)
        else:
            try:
                image = self.get_image(path)
            except Exception as e:
                traceback.print_exception(e)
                self.paths.rotate(self.rotation)
                return

        mininfo = self.min_entropy
        if mininfo:
            entropy = image.entropy()
            if entropy < mininfo:
                print('skipping  ', path, image.size, 'entropy:', entropy)
                return
            else:
                print('publishing', path, image.size, 'entropy:', entropy)
        else:
            print('publishing', path, image.size)

        ax = await self.get()
        ax.axis('off')
        if self.cmap:
            cmap = self.cmap
        else:
            cmap = magic.random_colour()

        print('EEEEEEEEEEEEE', self.extent)
        ax.imshow(image, cmap=cmap, extent=self.extent)
        
        ax.show()

    def fits_open(self, path):

        from astropy.io import fits
        
        tab = fits.open(path)
        #print(tab.info())
        for item in tab:
            print(item.size)
        if isinstance(item.size, int):
            print('Array size:', item.size)
        elif item.size:
            #await self.show_stats(item)
            pass

        keys = [
            ['title',
             #'origin',
             'duration',
             #'date', 'date-beg', 'date-end',
             'filter',
             'mu_dec', 'mu_ra'],
            ['crpix1', 'crpix2', 'crval1', 'crval2',],
            [ 'crdelt1', 'crdelt2'],
        ]

        # there are other tables with simpler headers
        for ix in 0, 1:
            hdr = tab[ix].header
            for key in keys[ix]:
                print(key, hdr[key.upper()])

        # figure out extents of image
        v1 = hdr['crval1']; v2 = hdr['crval2']
        p1 = hdr['crpix1']; p2 = hdr['crpix2']
        d1 = hdr['cdelt1']; d2 = hdr['cdelt2']

        ww, hh = tab[1].shape
        extent = [v1 - (p1 * d1), v1 + ((hh-p1) * d1),
                  v2 - (p2 * d2), v2 + ((ww-p2) * d2)]
        print('extent', extent)
        print(hh, p1, ww, p2)
        self.extent = extent
        xx, yy = tab[1].shape
        print(xx, yy)
        self.tab = tab
        return tab[1].data


    def booster(self, im):
        """ Scale pixel values in im by self. boost """
        if not self.boost: return im

        ent = im.entropy()
        data = np.array(im.getdata())
        
        data *= int(self.boost)
        data = np.clip(data, 0, 256)
        data = [(int(x), int(y), int(z)) for x,y,z in data]
        im.putdata(data)
        newt = im.entropy()
        print('boost change in entropy:', newt - ent)

        return im

async def run(args=None):

    fm = farm.Farm()

    train = Train(args)

    fm.add(train)
    await farm.start_and_run(fm)

        
if __name__ == '__main__':
    
    magic.run(run())
