
import sys

from astropy.io import fits

for x in sys.argv[1:]:

    tab = fits.open(x)
    print(tab[1].shape)

print(tab[1].header)
