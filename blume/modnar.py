"""
Functions that return a random something.

Use if you don't know what to use?
"""

import random
import curio

def random_colour():
    """ Pick a random matplotlib colormap """
    return random.choice(plt.colormaps())

def random_queue(minsize=1, maxsize=5):
    """Return a universal queue of random max size 

    Whilst this may seem a little strange, it means every run is a
    little different.  
    
    Probably could do with a debug over-ride.

    I've been using this a while.

    """
    return curio.UniversalQueue(maxsize=random.randint(minsize, maxsize))
