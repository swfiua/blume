"""
Simulate Binary stars
"""

import argparse

import healpy as hp

from .cpr import Spiral


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-ma', type=float,
                        default=0.)
    parser.add_argument('-mb', type=float,
                        default=0.)
