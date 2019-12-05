
from collections import Counter

import healpy as hp

from glob import glob

from matplotlib import pyplot as plt

import numpy as np

image = None

count = Counter()

N = 500000

thetas = np.random.random(N) * np.pi
phis = np.random.random(N) * np.pi * 2.

nside = 64
indices = hp.ang2pix(nside, thetas, phis)

npix = hp.nside2npix(nside)

hpxmap = np.zeros(npix, dtype=np.float)


images = {}
for folder in glob('S*'):
    print(folder)
    try:
        data = hp.read_map(folder + '/bayestar.fitz.gz')
    except:
        print('bad fitz')
        continue

    nside = hp.npix2nside(len(data))
    count.update([nside])

    image = images.get(nside)
    if image is None:
        npix = hp.nside2npix(nside)
        image = np.zeros(npix, dtype=np.float)
        images[nside] = image

    image += data

    # Go from HEALPix coordinates to indices
    #takes = hp.ang2pix(nside, thetas, phis)
    #print(len(takes))
    #for put, take in zip(indices, takes):
    #    hpxmap[put] += data[take]


    #hp.mollview(data)
    #plt.show()
    #hp.mollview(hpxmap)
    #plt.show()

for key, image in images.items():
    # Inspect the maps
    print(key, len(image))
    hp.mollview(image)

    plt.show()
