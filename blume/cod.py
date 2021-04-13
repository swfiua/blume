"""
cod 
===

csv data in git repos.

events: a place, a time, a value

meta data.

Tables.  

A list of headers, followed by a list of tuples.

"""
import csv
from collections import Counter, defaultdict
import argparse
from pprint import pprint

from blume import magic

def data_to_rows(data):
    """ Turn a list of strings into a list of dictionaries 
    
    Spell/magic should do all of this stuff.
    """
    
    # figure out what we have
    for row in csv.reader(data):
        keys = [x.strip() for x in row]
        break

    for ix, row in enumerate(csv.DictReader(data[1:], keys)):
        #print(ix, row)
        yield row
    


class Cod(magic.Ball):
    """Magically figure out what's in a table 

    
    The idea here is that the Spell will figure out tedious details
    such as what type everything is.

    The ultimate goal of a spell is to find a way to separate meta
    data from observations.

    An event is just a time and a place with a value.

    Everything else is meta data about that event.

    But first, find how to cast columns of data into appropriate types.

    Then look for columns that are indexes: a list of times or places?

    Or just a simple n-up counter?

    Positive floats, are they unix timestamps?

    """
    def __init__(self):

        super().__init__()
        
        # not sure what we need
        self.keys = []
        self.index = None
        self.meta = {}
        
    def cast(self, data=None):

        data = data or []
        
        self.data = list(data_to_rows(data))

        if self.data:
            self.update_meta()

    def update_meta(self):

        keys = self.data[0].keys()

        # simple counts of values can be informative
        counts = {}
        for key in keys:
            count = Counter([x[key] for x in self.data])
            counts[key] = count

            print(key, len(count))
            print(count.most_common(self.topn))
            print()

        self.counts = counts

        self.key_analysis()
        # now what?  More counts? let the user drive?
        # analyse the keys, group?
        # match beginnings of keys, look for sets that match

        
    def key_analysis(self):
        """ Look for relationships from the keys 
        
        See if keys are dates?
        run spell on the columns.
        
        """
        spell = magic.Spell()
        spell.find_casts(self.data[:1])
        print(spell.casts)
        groups = defaultdict(set)
        keys = set(spell.casts.keys())
        for key in keys:
            pass
        
        

    async def start(self):
        
        self.update_meta()

    async def run(self):
        """ Show what's there """
        print(self.counts.keys())
        

    def save(self):
        """ Save meta data ? """
        pass
        

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('infile')
    parser.add_argument('-topn', type=int, default=3)
    args = parser.parse_args()
    
    spell = Cod()
    
    spell.update(args)
    spell.cast(open(args.infile).readlines())


        
