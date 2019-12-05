"""
Inverted yeild curve

hmmm who knew? i yield dot py?

So lets yield some curves

What's an inverted yield curve and why does it matter.

It's all about how the value changes over time.

One year, two years, three or more.

Or maybe its days or weeks, or a lunar calendar?

Borrow for a year, borrow for five.

1 percent or five?

a for n or b for m? 

So this plots two yield (or rather random) curves.

Just zoom into a bit where the two curves cross

One the short term and the other the long term value of whatever i yield.
"""

from matplotlib import pyplot as plt

import random

def generate_yield_curve():

    for year in range(1962, 2019):

        rate = random.random()
                
        yield rate

plt.title(f'long versus short term values over time')
plt.plot(list(generate_yield_curve()))
plt.plot(list(generate_yield_curve()))
plt.show()

    




