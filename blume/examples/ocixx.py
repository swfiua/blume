"""
Ottawa c19

Data thanks to open ottawa

https://open.ottawa.ca/datasets/covid-19-source-of-infection/geoservice
"""
from matplotlib import pyplot as plt
import requests
import json
import datetime

import numpy as np

import traceback
import hashlib

from blume import magic
from blume import farm as fm

URL = "https://opendata.arcgis.com/datasets/de83f9e01278463e916f14121d5980d1_0/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json"

keys =[
    '%_No_Known_Source_for_Cases_with_non-institutional__source_of_infection_over_the_last_14_days',
    'No_Information_Available',
    'No_Known_Source_of_Infection',
    'Outbreak_or_Close_Contact_with_a_Case',
    'Sum_of_Non-institutional_Source_of_Infection_Over_the_Last_14_Days',
    'Travel'] 

keys2 = ["Cumulative_Cases", "Cumulative_Deaths"]
           
URL2 = 'https://opendata.arcgis.com/datasets/cf9abb0165b34220be8f26790576a5e7_0/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json'

def find_date_key(record):

    for key, value in record.items():
        try:

            date = to_date(value)
            return key
        except:
            traceback.print_exc()


def to_date(value):

    fields = value.split()[0].split('-')
    y, m, d = (int(x) for x in fields)

    return datetime.date(y, m, d)


def get_data(url, keys):
    
    resp = requests.get(URL)

    data = resp.content

    print(len(data))

    data = json.loads(data)

    print(len(data['features']))

    print(data.keys())

    print(data['exceededTransferLimit'])

    results = [x['attributes'] for x in data['features']]

    return results

class River(magic.Ball):
    """ Like a river that """


    async def start(self):
    
        import glob

        index = Path('index')
        if not index.exists():
            index.touch()

        data = []
        for row in csv.reader(index.open()):
            dt = dateutil.isoparse(row[0])
            cksum = row[1].strip()

            data.append(dt, cksum)
            

        self.files = deque(data)
        self.files.sort()


    def check_and_save(self, results):

        # turn results back into json
        data = json.dumps(results)
        ck = hashlib.md5(data.encode()).digest()

        ck = ''.join(['%02x' % x for x in ck])

        print(ck)
        
        cksums = set(x[0] for x in self.files)

        if ck not in cksums:
            path = Path(ck + str(datetime.datetime.now()))
            
        

    


class Ocixx(magic.Ball):
    
    async def run(self):
        pass

if __name__ == '__main__':

    from pprint import pprint
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-cumulative', action='store_true')
    parser.add_argument('-save', action='store_true')
    parser.add_argument('-update', action='store_true')

    args = parser.parse_args()

    if args.cumulative:
        URL = URL2
        keys = keys2

    results = get_data(URL, keys)

    if args.update:
        check_and_save(results)

    pprint(results[0])
    pprint(results[-1])

    datekey = find_date_key(results[0])
    print(datekey)

    index = [to_date(x[datekey]) for x in results]

    for key in keys:
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

    
