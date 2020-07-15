""" de Sitter Space
"""


class Dss():

    def __init__(self):
        """ initialise """
        self.alpha = 1
        self.beta = 1
        self.gamma = 1
        self.delta = 1

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
            


if __name__ == '__main__':

    dss = Dss()

    dss.set_abcd()
    dss.constraints()
