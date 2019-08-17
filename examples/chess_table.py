"""
===========
Chess board
===========

Demo using blume.table function to display a chess board.
"""
import sys
import numpy as np
import matplotlib.pyplot as plt

from blume.table import table

columns = [x for x in 'abcdefgh']
rows = [x for x in '87654321']

black = '#333333'
white = '#999999'

arow = [white, black] * 4

# unicode characters for chess pieces
pieces = dict(
    black_king="\N{BLACK CHESS KING}",
    black_queen="\N{BLACK CHESS QUEEN}",
    black_bishop="\N{BLACK CHESS BISHOP}",
    black_knight="\N{BLACK CHESS KNIGHT}",
    black_rook="\N{BLACK CHESS ROOK}",
    black_pawn="\N{BLACK CHESS PAWN}",

    white_king ="\N{WHITE CHESS KING}",
    white_queen="\N{WHITE CHESS QUEEN}",
    white_bishop="\N{WHITE CHESS BISHOP}",
    white_knight="\N{WHITE CHESS KNIGHT}",
    white_rook="\N{WHITE CHESS ROOK}",
    white_pawn="\N{WHITE CHESS PAWN}")


cell_text = [[
    pieces['black_rook'],
    pieces['black_knight'],
    pieces['black_bishop'],
    pieces['black_queen'],
    pieces['black_king'],
    pieces['black_bishop'],
    pieces['black_knight'],
    pieces['black_rook']]]

cell_text.append([pieces['black_pawn']] * 8)

for row in range(4):
    cell_text.append([''] * 8)

cell_text.append([pieces['white_pawn']] * 8)

cell_text.append([
    pieces['white_rook'],
    pieces['white_knight'],
    pieces['white_bishop'],
    pieces['white_queen'],
    pieces['white_king'],
    pieces['white_bishop'],
    pieces['white_knight'],
    pieces['white_rook']])

cell_colours = []
for row in range(8):
    cell_colours.append(arow.copy())
    arow.reverse()
    
fig = plt.figure()
ax = fig.add_subplot(1,1, 1)
ax.axis('off')

# Add a table at the top of the axes
table(
    ax,
    cellColours=cell_colours,
    cellText=cell_text,
    rowLabels=rows,
    colLabels=columns,
    bbox=(0, 0, 1, 1))

if not sys.flags.interactive:
    plt.show()
