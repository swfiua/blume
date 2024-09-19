
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


    def __init__(self, path):

        super().__init__()
        
        self.path = magic.Path(path)
        self.text = True
        self.load()
        
        self.add_filter(' ', self.next)
        self.add_filter('backspace', self.previous)
        self.add_filter('<', self.lower_alpha)
        self.add_filter('>', self.raise_alpha)
        self.add_filter('t', self.toggle_text)

    async def toggle_text(self):

        self.text = not self.text
        await self.display()


    def load(self):
        """ Load a file of restructured text

        Parse the document.

        Set things up to go through so we can navigate through sections.
        """
        print(f'Loading {self.path}')
        
        txt = self.path.open().read()

        # start the section ball rolling
        self.node = parse_rst(txt)

        self.nodes = magic.deque(self.generate_sections())

    def generate_sections(self):

        indices = magic.deque([0])

        while True:
            section = self.find_next_section(indices)
            if not section: break
            yield section

    def find_next_section(self, indices):

        section = self.node.first_child_matching_class(
            nodes.section, start=indices[-1])

        print('finding', indices, section)
        if section is None:
            # go back up a level
            indices.pop()
            self.node = self.node.parent
            if indices:
                return self.find_next_section(indices)

            # nothing left
            return
        else:
            indices[-1] = section + 1 # start at next next time
            indices.append(0)
            
        self.node = self.node.children[section]
        return self.node

    def find_children(self):

        node = self.nodes[0]
        self.sections = magic.deque(
            [x for x in node.findall(nodes.section) if x.parent == node])
        self.paras = magic.deque(
            [x for x in node.findall(nodes.paragraph) if x.parent == node])
        self.images = magic.deque(
            [x for x in node.findall(nodes.image) if x.parent == node])

    async def next(self):

        self.nodes.rotate(-1)
        
        self.find_children()
        await self.display()

        
    async def previous(self):

        self.nodes.rotate(1)
        self.find_children()
        await self.display()

    async def display(self):
                 
        msg = []
        for para in self.paras:
            msg.append([para.astext()])

        node = self.nodes[0]
        self.ax = ax = self.get_nowait()
        title = node.first_child_matching_class(nodes.title)
        if title is not None:
            title = node.children[title]
            ax.set_title(title.astext())
        else:
            print('No title', self.section)

        if not self.text: msg = None
        self.tab = table_text(ax, msg, self.images)
        ax.show()

    def lower_alpha(self):

        print('lowering alpha')
        #self.tab.scale_alpha(0.9)
        self.tab.scale_alpha(0.9)
        self.ax.show()

    def raise_alpha(self):
        print('raising alpha')
        #self.tab.scale_alpha(1/0.9)
        self.tab.scale_alpha(1/0.9)
        self.ax.show()

    def scale_alpha(self, factor=0.9):
        """ Scale the alpha for all cells """
        alpha = None
        for cell in self.tab._cells.values():
            if alpha is None:
                alpha = cell.get_alpha() or 1.
                alpha *= factor
                alpha = min(1., max(alpha, 0.0))
            cell.set_alpha(alpha)

def table_text(ax, msg, images=[], alpha=.5):

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
        colWidths=widths,
        edgeColour=None,
        #edges='vertical'
    )

    tab.scale_alpha(0.6)
    #for key in tab._cells.keys():
    #    tab[key].set_alpha(alpha)
    #tab.scale_alpha(alpha)

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
    parser.add_argument('path', default='index.rst')
    
    args = parser.parse_args()
    
    farm.run(balls=[Talk(args.path)])
