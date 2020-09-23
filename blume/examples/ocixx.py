"""Ottawa c19

Data thanks to open ottawa

https://open.ottawa.ca/datasets/covid-19-source-of-infection/geoservice

This short little example, originally written to explore Ottawa
datasets relating to covid 19.

There are a number of interesting datasets.

The actual data itself is hosted by arcgis.  

The endpoints all include random hexadecimal ids.

So far I have not been able to find stable endpoints for these
datasets and they have had a half-life of about one month.

A script will stop working as a dataset no longer seems to exist.

This is not all bad news, the breakages usually also mean some more
data is available.  There are now 9 covid related datasets.

The primary dataset now has more fields and the date field is now called Date.

Data for the last 14 days in these datasets is typically incomplete,
so it is useful to keep a few days of data so get a better idea of the
evolving picture.

I've started saving data each time the code is run.

Aim to add checksums and scrolling through data sets to see how the
plots change in time.

Seems this little problem has all the key ingredients of the costs of
keeping a data pipeline going.

"""

from matplotlib import pyplot as plt

import requests
import json
import datetime
import csv
from pprint import pprint

from pathlib import Path
from collections import deque

import numpy as np

import traceback
import hashlib

from blume import magic
from blume import farm as fm

def find_date_key(record):

    for key, value in record.items():
        try:

            date = to_date(value)
            return key
        except:
            # guess it is not this one
            print(key, 'is not a date')


def to_date(value):

    fields = value.split()[0].split('-')
    y, m, d = (int(x) for x in fields)

    return datetime.date(y, m, d)


class River(magic.Ball):
    """ Like a river that """

    def __init__(self):

        super().__init__()
        p = Path('.')
        self.format = '.csv'
        
        data = p.glob(f'*{self.format}')
        
        self.files = deque(sorted(data))
        

    async def xstart(self):
        pass


    def save(self, data):

        path = Path(str(datetime.datetime.now()) + self.format)
        path.write_text(data)
        self.files.append(path)
        

BASE_URL = 'https://www.arcgis.com/sharing/rest/content/items/'
ITEM_IDS = [
    '6bfe7832017546e5b30c5cc6a201091b',
    '26c902bf1da44d3d90b099392b544b81',
    'cf9abb0165b34220be8f26790576a5e7',
    '02c99319ef44488e85cd4f96f5061f20',
    '77078920fea8499dbb6f54cc69c03a90']

def get_response(url):
    
    return requests.get(url)


def data_to_rows(data):
    
    # figure out what we have
    for row in csv.reader(data):
        keys = [x.strip() for x in row]
        break

    for row in csv.DictReader(data[1:], keys):
        yield row
    

def find_casts(data, sniff=10):

    keys = data[0].keys()

    # look for a date key
    datekey = find_date_key(data[0])
    
    casts = {}
    casts[datekey] = to_date

    upcast = {None: int, int: float, float: str}
    
    for row in data[:sniff]:
        for key in keys:
            value = row[key].strip()
            if key:
                try:
                    casts.setdefault(key, int)(value)
                except:
                    casts[key] = upcast[casts[key]]
                
                    
    return casts

def cast_data(data, casts):

    fill = {None: None, int: 0, float: 0.0, str:''}

    for row in data:

        result = {}
        for key, value in row.items():
            cast = casts[key]
            if not value.strip():
                value = fill.setdefault(cast)

            result[key] = cast(value)
        yield result

                  

class Ocixx(magic.Ball):

    def __init__(self, data):

        super().__init__()

        self.data = data
        self.fields = deque(self.data[0].keys())
        
        
    async def run(self):

        
        for key, value in self.data[0].items():
            if isinstance(value, datetime.date):
                datekey = key
                break 
        index = [x[datekey] for x in results]

        key = self.fields[0]
        data = [x[key] for x in results]
        
        plt.plot(index, data, label=key)

        plt.legend(loc=0)
        plt.grid(True)

        #self.put(magic.fig2data(plt))
        await self.put()


async def run(results):
    
    pprint(results[0])

    ocixx = Ocixx(results)

    farm = fm.Farm()
    
    farm.add(ocixx)
    farm.shep.path.append(ocixx)

    await farm.start()
    await farm.run()



if __name__ == '__main__':

    from pprint import pprint
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-cumulative', action='store_true')
    parser.add_argument('-save', action='store_true')
    parser.add_argument('-update', action='store_true')
    parser.add_argument('-itemid', type=int, default=0)

    args = parser.parse_args()

    url = BASE_URL + ITEM_IDS[args.itemid] + '/data' # 

    resp = get_response(url)

    River().save(resp.text)

    data = list(data_to_rows(resp.text.split('\n')))

    casts = find_casts(data)
    
    results = list(cast_data(data, casts))

    import curio
    curio.run(run(results))
    
    if args.cumulative:
        data = np.array(data[1:]) - np.array(data[:-1]) 
        plt.plot(index[1:], data, label='delta' + key)
        print(key)
        print(data[-14:])
        print('Sum for last 14 days:', sum(data[-14:]))
            

    
