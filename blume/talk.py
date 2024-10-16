
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
        self.alpha = 0.7
        self.load()
        
        self.add_filter(' ', self.next)
        self.add_filter('backspace', self.previous)

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

    async def next(self):

        self.nodes.rotate(-1)
        await self.display()
        
    async def previous(self):

        self.nodes.rotate(1)
        await self.display()

    async def display(self):
                 
        node = self.nodes[0]

        # find images whose parent is this node
        images = [x for x in node.findall(nodes.image) if x.parent == node]

        # display the images
        for image in images:
            ax = await self.get()
            try:
                img = Image.open(image['uri'])
            except FileNotFoundError as e:
                print(e)
                continue

            ax.imshow(img)
            ax.axis('off')
            ax.show()

        # Get the section title
        title = node[node.first_child_matching_class(nodes.Titular)]
        
        msg = [[title.astext()], ['']]
        para = []

        # show paragraphs, math_blocks and sections of this node
        for item in [x for x in
                     node.findall() if x.parent is node]:
            if isinstance(item, nodes.paragraph):
                msg.append([item.astext()])
                
            if isinstance(item, nodes.math_block):
                msg.append(['$' + item.astext() + '$'])

            if isinstance(item, nodes.section):
                title = item[item.first_child_matching_class(nodes.Titular)]
                msg.append([title.astext()])

        self.put_nowait(msg, 'help')


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
