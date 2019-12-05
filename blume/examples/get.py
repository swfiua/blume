"""
Get bayestar fits files for a bunch of events
"""

import os
import requests

url = 'https://gracedb.ligo.org/api/superevents/%s/files/bayestar.fits.gz'


def fetch(event):

    event = event.strip()

    resp = requests.get(url % event)

    os.mkdir(event)

    bf = open(event + '/bayestar.fitz.gz', 'wb')

    bf.write(resp.content)

    bf.close()


if __name__ == '__main__':

    
    
    fetch('S191204r')
    
    #for event in open('../events.csv'):
    #    get(event)


        
