"""
======
Sudoku
======

Demo using blume.table function to display a sudoku game.
"""
import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt

import curio

from matplotlib import cm, colors

import random

from blume.table import table

from blume import magic

N = 9

def random_board(N, cells=None):
    if cells is None:
        cells = np.zeros((N, N), dtype=int)

    for row in range(N):
        for col in range(N):
            cells[row][col] = random.randint(1, N)
    return cells

class Sudoku(magic.Ball):

    async def start(self):

        fig = plt.figure()
        self.ax = fig.add_subplot(1,1, 1)
        self.ax.axis('off')

        self.N = 9
        self.board = None

    async def run(self):

        
        # create a random board
        self.board = random_board(self.N, self.board)

        await self.show_board()
        await self.eagle_eyes()

        # show board
        await self.eagle_eyes()
        

    async def eagle_eyes(self):
        """ Adjust table until legal eagle """
        n = self.N
        n3 = n//3

        board = self.board
        for row in range(n3):
            for col in range(n3):
                seen = set()
                for x in range(n3):
                    xx = (col * n3) + x
                    for y in range(n3):
                        yy = (row * n3) + y
                        value = board[xx][yy]
                        if value in seen:
                            board[xx][yy] *= -1
                        else:
                            seen.add(value)
                            
                await self.show_board()
                await curio.sleep(self.sleep)

        for xx in range(n):
            seen = set()
            for yy in range(n):
                value = board[xx][yy]
                if value in seen:
                    board[xx][yy] *= -1
                else:
                    seen.add(value)

            print(f'showing row {xx}')
            await self.show_board()
            await curio.sleep(self.sleep)
            
        for xx in range(n):
            seen = set()
            for yy in range(n):
                value = board[yy][xx]
                if value in seen:
                    board[yy][xx] *= -1
                else:
                    seen.add(value)

            print(f'showing col {xx}')
            await self.show_board()
            await curio.sleep(self.sleep)
                        
        return
        
    async def show_board(self):
        norm = colors.Normalize()

        # fixme, have table normalise/apply color map?
        # Better, just have values for cells.
        # that may have a color and use str or repr? to
        # get text?
        self.ax.clear()
        board = self.board

        colours = cm.get_cmap()(norm(board))

        
        # Add a table at the top of the axes
        self.table = table(
            self.ax,
            cellText=board,
            cellColours=colours,
            bbox=(0, 0, 1, 1))

        print('showing sudoku board')
        await self.outgoing.put(magic.fig2data(plt))


# From here down boiler plate magic code -- or should be
        
async def run(args):
    """ Don't do things this way until things settle down ..."""

    farm = magic.Farm()
    from blume import mclock2
    
    clock = mclock2.GuidoClock()

    carpet = magic.Carpet()

    iq = curio.UniversalQueue()
    await carpet.set_incoming(iq)
    await carpet.set_outgoing(farm.hatq)


    farm.event_map.update(clock.event_map)
    farm.event_map.update(carpet.event_map)

    examples = Sudoku()
    await examples.set_outgoing(iq)
    await clock.set_outgoing(iq)

    examples.incoming = None
    clock.incoming = None

    farm.add(carpet, background=True)
    farm.add(examples)
    farm.add(clock)


    starter = await curio.spawn(farm.start())

    print('farm runnnnnnnnnning')
    runner = await farm.run()
    
        
if __name__ == '__main__':

    
    parser = argparse.ArgumentParser()
    #parser.add_argument('path', default='.')

    args = parser.parse_args()
    curio.run(run(args))
