"""
A multiline example, see how the table handles multi-line.

Hm... still need tools to help testing with image comparison.
"""
import sys
from matplotlib import pyplot as plt
from blume.table import table

#from blume.taybell import table

cell_text = [["long text\nWith\nmany\nlines"],
                 ['more but short']]
                 

fig = plt.figure()
ax = fig.add_subplot(1,1, 1)
ax.axis('off')

# Add a table at the top of the axes
table(
    ax,
    cellText=cell_text,
    bbox=(0, 0, 1, 1))

if not sys.flags.interactive:
    plt.show()
