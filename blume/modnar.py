"""
Functions that return a random something.

Use if you don't know what to use?
"""

import random
import asyncio
from matplotlib import pyplot as plt

def random_colour():
    """ Pick a random matplotlib colormap """
    return random.choice(plt.colormaps())

def random_queue(minsize=3, maxsize=20):
    """Return a universal queue of random max size 

    Whilst this may seem a little strange, it means every run is a
    little different.  
    
    Probably could do with a debug over-ride.

    I've been using this a while.

    """
    return asyncio.Queue(maxsize=random.randint(minsize, maxsize))
