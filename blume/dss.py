""" de Sitter Space

Are gamma-ray bursts optical illusions?

Robert S Mackay, Colin Rourke.
"""

# we are going to need this
import math

# hmm, sympy is a whole universe of stuff
from sympy import *

from blume import magic
from blume import magic
from blume import farm as fm

class Dss(magic.Ball):

    def __init__(self):
        """ initialise """
        self.alpha, self.beta, self.gamma, self.delta = symbols(
            'alpha beta gamma delta')

    def set_abcd(self):

        self.a = (self.alpha + self.beta - self.gamma - self.delta) / 2
        self.b = (self.alpha - self.beta - self.gamma + self.delta) / 2
        self.c = (self.alpha + self.beta + self.gamma + self.delta) / 2
        self.d = (self.alpha - self.beta + self.gamma - self.delta) / 2
        

    def constraints(self):

        assert(self.alpha**2 - self.gamma**2 >= 1.)

        assert(self.alpha > 0)

        a, b, c, d = self.alpha, self.beta, self.gamma, self.delta

        assert((a * b - c * d) <= (a*a - c*c - 1) * (b*b - d*d -1))

        assert((a*d - b*c) <= (a*a - c*c - b*b + d*d -1))

    def blue_shift_time(self, alpha, delta):
        """ """
        sqrt = math.sqrt

        a = sqrt(alpha)
        d = sqrt(delta)

        etb = sqrt((1+a+d)/d) + sqrt((1+a-d)/d)
        
        return math.log(math.sqrt(etb))
        


if __name__ == '__main__':

    dss = Dss()

    dss.set_abcd()
    dss.constraints()
