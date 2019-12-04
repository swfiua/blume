""" Mathematics for a new paradigm.

Colin P. Rourke.
"""
import math
import sys

from matplotlib import pyplot as plt
import numpy as np
from scipy import integrate
from blume.table import table

def cpr():
    """  Started as Mathematica code from the new paradigm.
    
    adapted to python over time.

    See spiral class in `blume.cpr` for more information over time.
    """

    Plot = plt.plot
    Log = np.log
    Sqrt = np.sqrt
    NIntegrate = integrate.cumtrapz

    # Magic constants for now
    A = 0.0005
    B = .00000015

    EE = -.00000345
    CC = -10;

    # Masses: centra, a ball, a disk
    Mcent = .03; 
    Mball = 0;
    Mdisc = 0;

    K = Mcent;

    # range of radii in light years
    rmin = 5000
    rmax = 50000

    # range of r to compute for
    r = np.arange(rmin, rmax, step=1)

    # Velocity at distance r
    v = 2*A - 2*K*A*Log(1 + r/K)/r + CC/r

    # velocity in inertial frame
    inert = v - A*r/(K + r);

    # rate of acceleration towards center, at radius r
    rdoubledot = inert**2/r - Mcent/r**2 - Mdisc/rmax**2 - Mball*r/rmax**3

    energy = (-CC**2/(2*r**2) + (Mcent - 2*A*CC)/r -
                  Mdisc*r/rmax**2 +
                  Mball*r**2/(2*rmax**3) +
                  A**2*K/(K + r) +
                  A**2*Log(K + r) +
                  2 * A*K * (CC + 2*A*r) * Log(1 + r/K)/(r**2)
                  - (2 * A*K*Log(1 + r/K)/r)**2 + EE);
    #Plot(energy, r, label='energy')
    rdot = Sqrt(2*energy)

    thetadot = v/r;
    dthetabydr = thetadot/rdot 
    dtbydr = 1/rdot

    
    thetaValues = NIntegrate(dthetabydr, r, initial=0.)
    print(thetaValues)
    print(len(thetaValues))

    tvalues = NIntegrate(dtbydr, r, initial=0.)

    # Aha, we need a table, but this is a slightly different
    # beast.  Time for `magic.table`?  or just a stream of dictionaries?
    # to summarise in a table?
    
    #thetavalues = Table(
    #    NIntegrate(dthetabydr, rmin, rmax), ivalue, i, iterate))
    #tvalues = Table(
    #    NIntegrate(dtbydr, r, ivalue, i, iterate))
    
    #ListPolarPlot[{ Table[{thetavalues[[i]] - B*tvalues[[i]], ivalue},
    #{i, iterate}] ,
    #Table[{thetavalues[[i]] - B*tvalues[[i]] + Pi, ivalue}, 
    #{i, iterate}] }]

    # Now do some plotting
    ax = plt.subplot(221)
    
    ax.plot(r, v, label='velocity')
    ax.plot(r, inert, label='vinert')
    ax.plot(r, rdoubledot, label='rdoubledot')
    ax.plot(r, rdot, label='rdot')
    ax.legend(loc=0)
    

    # inertia and newton????
    ax = plt.subplot(222)
    ax.plot(r, inert ** 2/r, label='inertia')
    ax.plot(r, Mcent / r ** 2, label='newton')
    ax.legend(loc=0)

    ax = plt.subplot(223, projection='polar')
    ax.plot(thetaValues - (B * tvalues), r)
    ax.plot(thetaValues - (B * tvalues) + math.pi, r)

    values = (thetaValues - (B * tvalues))

    ax = plt.subplot(224)
    cellColours = None

    ax.axis('off')
    ax.text(0, 0, "...........A new paradigm")

    #rdot, inert
    # what I need here is a magic ball that helps you explore a table
    # need a new name for a table -- taybell?
    #table(cellText=[['a','b','c','d']])
        
    

cpr()

if not sys.flags.interactive:
    plt.show()
