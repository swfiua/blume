"""
Ottawa c19

Data thanks to open ottawa

https://open.ottawa.ca/datasets/covid-19-source-of-infection/geoservice
"""
from matplotlib import pyplot as plt
import requests
import json
import datetime
import csv
from pprint import pprint

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
    format = '.csv'

    async def start(self):
    
        p = Path('.')

        data = p.glob(f'**.{self.format}')
        
        self.files = deque(data)
        self.files.sort()


    def check_and_save(self, data):

        ck = hashlib.md5(data.encode()).digest()

        ck = ''.join(['%02x' % x for x in ck])

        print(ck)
        
        cksums = set(x.stem.split('_')[1] for x in self.files)

        if ck not in cksums:
            path = Path(ck + str(datetime.datetime.now() + self.format))
            path.write_text(data)
            self.files.append(path)
        

BASE_URL = 'https://www.arcgis.com/sharing/rest/content/items/'
ITEM_IDS = [
    'cf9abb0165b34220be8f26790576a5e7',
    '02c99319ef44488e85cd4f96f5061f20',
    '77078920fea8499dbb6f54cc69c03a90']

def get_csv_data(url):
    
    resp = requests.get(url)
    data = resp.text.split('\n')

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
                
                    
    pprint(casts)
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

    async def run(self):

        item_id = self.items[0]

        URL = BASE_URL + item_id + '/data'

if __name__ == '__main__':

    from pprint import pprint
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-cumulative', action='store_true')
    parser.add_argument('-save', action='store_true')
    parser.add_argument('-update', action='store_true')
    parser.add_argument('-itemid', type=int, default=0)

    args = parser.parse_args()

    URL = BASE_URL + ITEM_IDS[args.itemid] + '/data'

    data = list(get_csv_data(URL))

    casts = find_casts(data)
    
    results = list(cast_data(data, casts))

    foo = json.dumps(results, default=str)

    pprint(results[0])
    pprint(results[-2:])

    for key, value in results[0].items():
        if isinstance(value, datetime.date):
            datekey = key
            break

    index = [x[datekey] for x in results]
    
    for key in casts.keys():
        if key == datekey:
            continue
        if casts[key] is str:
            continue
        
        data = [x[key] for x in results]
        plt.plot(index, data, label=key)


        if args.cumulative:
            data = np.array(data[1:]) - np.array(data[:-1]) 
            plt.plot(index[1:], data, label='delta' + key)
            print(key)
            print(data[-14:])
            
        plt.legend(loc=0)
        plt.grid(True)
    plt.show()

    
