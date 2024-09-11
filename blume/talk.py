
from docutils import utils, nodes
from docutils.parsers import rst
from docutils.frontend import get_default_settings

import random

from PIL import Image

from blume import magic, farm, table

def parse_rst(txt):
    """ Parses restructured txt using default settings """

    settings = get_default_settings(rst.Parser)

    doc = utils.new_document('.', settings)

    parser = rst.Parser()

    parser.parse(txt, doc)

    return doc


class Talk(magic.Ball):


    def __init__(self, paths=None):

        super().__init__()
        if not paths:
            paths = magic.Path('.').glob('*.rst')

        # expand directories
        epaths = []
        for path in paths:
            path = magic.Path(path)
            if path.is_dir():
                epaths = epaths + path.glob('*.rst')
            else:
                epaths.append(path)
           
        self.paths = magic.deque(epaths)

        self.load()

        self.add_filter(' ', self.next)
        self.add_filter('<', self.lower_alpha)
        self.add_filter('>', self.raise_alpha)

    def load(self):
        """ Load a file of restructured text

        Parse the document.

        Set things up to go through so we can navigate through sections.
        """
        print(f'Loading {self.paths[0]}')
        
        txt = self.paths[0].open().read()

        # start the section ball rolling
        self.node = parse_rst(txt)
        self.child_numbers = magic.deque([0])

    def set_section(self):

        section = self.node.first_child_matching_class(
            nodes.section, start=self.child_numbers[-1])

        if section is None:
            # go back up a level
            self.child_numbers.pop()
            self.node = self.node.parent
            if self.child_numbers:
                self.set_section()
            else:
                print("The End!!!!")
                return
        else:
            self.child_numbers.append(0)
        self.node = self.node.children[section]

    def find_children(self):
        
        self.sections = magic.deque(
            [x for x in self.node.findall(nodes.section) if x.parent == self.node])
        self.paras = magic.deque(
            [x for x in self.node.findall(nodes.paragraph) if x.parent == self.node])
        self.images = magic.deque(
            [x for x in self.node.findall(nodes.image) if x.parent == self.node])

    async def next(self):

        self.set_section()
        self.find_children()
        await self.display()
        self.child_numbers[-1] += 1
        print(self.child_numbers, self.node['names'])
        

    async def display(self):
                 
        msg = []
        for para in self.paras:
            msg.append([para.astext()])

        self.ax = ax = self.get_nowait()
        title = self.node.first_child_matching_class(nodes.title)
        if title is not None:
            title = self.node.children[title]
            ax.set_title(title.astext())
        else:
            print('No title', self.section)

        self.tab = table_text(ax, msg, self.images)
        ax.show()

    def lower_alpha(self):

        self.scale_alpha(0.9)

    def raise_alpha(self):
        self.scale_alpha(1/0.9)

    def scale_alpha(self, factor=0.9):
        alpha = None
        for key, cell in self.tab._cells.items():
            if alpha is None:
                alpha = cell.get_alpha()
                alpha *= factor
                alpha = min(1., max(alpha, 0.0))
                
            cell.set_alpha(alpha)
        self.ax.show()

def table_text(ax, msg, images=[], alpha=0.5):

    if images:
        image = random.choice(images)

        image = Image.open(image['uri'])
        ax.imshow(image)

    if not msg or not msg[0]:
        return

    widths = get_widths(msg)
    tab = table.table(
        ax.delegate, cellText=msg, bbox=(0,0,1,1),
        cellLoc='center',
        colWidths=widths)

    for key in tab._cells.keys():
        tab[key].set_alpha(alpha)

    return tab

def get_widths(msg):

    # find max len of string for each column
    ncols = len(msg[0])

    widths = []
    for col in range(ncols):
        widths.append(max([len(str(x[col])) for x in msg]) + 3)

    # now normalise
    total = sum(widths)
    widths = [x/total for x in widths]

    return widths
    
        

if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('path', default=[], nargs='*')
    
    args = parser.parse_args()
    
    talk = Talk(args.path)

    land = farm.Farm()
    land.add(talk)
    magic.run(farm.start_and_run(land))
