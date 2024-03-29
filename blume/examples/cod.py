"""Ottawa c19

Data thanks to open ottawa

https://open.ottawa.ca/datasets/covid-19-source-of-infection/geoservice

Known locally as "the COD" it is the open data behind the Ottawa
Public Health dashboard.

https://www.ottawapublichealth.ca/en/reports-research-and-statistics/daily-covid19-dashboard.aspx

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

Jan 9th 2021 update
===================

The example is still working and I am in the process of renaming
everything to *cod*.

Maybe start a fish theme.

The module has a lot of interesting pieces, the tracking of data in
git has been helpful, in this case.

There has been some general date confusion, that has migrated to the
blume.magic.Spell core, at least for the time being.




29th September 2020 update
==========================

Things are moving along.  An initial stab at downloading csv files and
checking differences into git is up and running.

Also starting to develop a class to help guessing what sort of values are in each column.

For now, I am just looking for int's, float's and dates.

As things are going it might work for a lot of the Ottawa datasets.

3rd October 2020
================

I've been using the automatic check for new data and check into git if
it changes for a few days now.

It is a bit clunky, but at least I now have history with the data.
There's a hard named filename, imaginitively called data.csv.

The Ottawa data changes every day, and often the changes go back quite
a way in time.

This is useful, as well as interesting for this data, as cases evolve.

I am having trouble with some of the columns, where the early rows
(where I try to guess what type of column it is), have no data, and
the latter are a mixture of integers and floats, since they are the
seven day average of the daily case numbers.  There is other
wierdness, related to the results of my attempts to guess column types
breaks in different ways for different commits.

I think the fix here is to get the magic spell working!

Update: bug in my code, wrote key where it should have been value.

Still need to get the magic spell working.

Back to the git tracking of data
================================

There are all sorts of reasons for updates, such as guidelines on how
to classify cases changing, or being clarified.  

As I write, there are emerging details of a spreadsheet fail in the
UK, where the sheet recently, and presumably, silently, ran out of
columns and so recent reports have been out of line (on the good
side).

I am assuming that this is really just the result of choosing excel as
the data exchange medium.
 
And having one column per case, which worked really well if there were
15 cases and very soon there would be none.

The spreadsheets perhaps generated by software, unaware of the column
limit, pulling data from some central database.

** UPDATE ** 

Turns out to be a data format problem.  *xls* rather than *xlsx*.  The
former limits to the pre-Excel 2007 limit of 65,536.

Still not clear if this is the ultimate database or just a file
created by a data pull. 

Using spreadsheets can, in theory, remove the "guess the type" issues
that I am dealing with here, but introduce a whole host of
complications, it would appear.

Exchanging data as `csv` files, stored in a git repository offers a
lot more flexibility.

Others are also using git for covid data:

https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports

Now about that magic spell...

"""

from matplotlib import pyplot as plt

import sys
import requests
import json
import datetime
import csv
from pprint import pprint

from pathlib import Path
from collections import deque, Counter

import numpy as np

import traceback
import hashlib
import functools

from blume import magic
from blume import farm as fm

import git
from dateutil.utils import today

def save_data(data, filename='data.csv'):

    #path = Path(str(datetime.datetime.now()) + self.format)
    path = Path(filename)
    path.write_text(data)


BASE_URL = 'https://www.arcgis.com/sharing/rest/content/items/'
ITEM_IDS = [
    'b87fb824d0514960b380cba68a2df0ba',
    '6bfe7832017546e5b30c5cc6a201091b',
    '26c902bf1da44d3d90b099392b544b81',
    '7cf545f26fb14b3f972116241e073ada',
    '5b24f70482fe4cf1824331d89483d3d3',
    'd010a848b6e54f4990d60a202f2f2f99',
    'ae347819064d45489ed732306f959a7e',
]

def data_to_rows(data):
    
    # figure out what we have
    for row in csv.reader(data):
        keys = [x.strip() for x in row]
        break

    for row in csv.DictReader(data[1:], keys):
        yield row
    

class Cod(magic.Ball):
    """ Ottawa COD data viewer 

    Fixme: make a table that works for Ottawa and John Hopkins University data too.

    There are csv files under git control there too.

    Data is tilted, with each row giving the region and time series.

    Again, what we need is a magic.Spell that works.
    """


    def __init__(self):

        super().__init__()
        self.sleep *= 3
        self.spell = None
        self.fields = None
        self.filtered = set()
        self.shorten = 100
        self.fudge = 1.

    @functools.cache
    def get_data(self, commit):

        repo.git.checkout(commit)

        path = Path(self.filename)

        if not path.exists():
            return

        data = list(data_to_rows(path.open().read().split('\n')))
        if not data:
            return

        if self.spell is None:
            self.spell = magic.Spell()
            self.spell.find_casts(data, self.sniff)
            #print(self.spell.casts)
        else:
            self.spell.check_casts(data, self.sniff)
            
        results = list(self.spell.spell(data))
        
        return results

    async def start(self):

        self.load_commits()


    def load_commits(self):

        self.repo = git.Repo(search_parent_directories=True)
        self.repo.git.checkout('master')

        self.commits = deque(self.repo.iter_commits(paths=self.filename))
        while len(self.commits) > self.history:
            self.commits.pop()
        self.master = self.commits[0]
        
        
    async def run(self):

        from matplotlib import dates as mdates

        # Make dates on X-axis pretty
        locator = mdates.AutoDateLocator()
        formatter = mdates.ConciseDateFormatter(locator)

        self.scale = 'Total Active Cases by Date'
        self.scale = '7-day Average of Newly Reported cases by Reported Date'

        ax = await self.get()
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)

        last_dcases = None
        while True:

            commit = self.commits[0]
            results = self.get_data(commit)

            if self.fields is None:
                self.fields = deque(self.spell.fields())

            key = self.fields[0]

            # skip data/index key
            if key == self.spell.datekey:
                self.fields.rotate()
                continue

            if self.filter and self.filter in key:

                self.filtered.add(key)
                self.fields.rotate()
                continue

            if results:
                # fixme: give spell an index
                spell = self.spell
                index = [x[spell.datekey] for x in results]
                if self.scale:
                    scale = [x[self.scale] for x in results]
                else:
                    scale = np.ones(len(results))

                # not sure what this was about ???
                #for ii in index:
                #    # fixme 2: let's use matplotlib's mdates.
                #    if type(index) == mdates.datetime:
                #        print('date oops')

                try:
                    data = np.array([x[key] for x in results])

                    # sort according to index
                    xyz = sorted(zip(index, data, scale))
                    index = [foo[0] for foo in xyz]
                    data = np.array([foo[1] for foo in xyz])
                    scale = np.array([foo[2] for foo in xyz])


                    try:
                        factor = np.nanmean(data) / np.nanmean(scale)
                        expected = scale * factor
                        #print('means',
                        #      np.nanmean(data),
                        #      np.nanmean(expected), np.nanmean(scale))
                    except Exception as e:
                        print('cannot scale', key)
                        print(e)
                        print(type(data[0]), type(scale[0]))
                        print(data[0], scale[0])
                        expected = data

                    if self.days:
                        # only keep data later than self.days ago
                        start = today() - datetime.timedelta(days=self.days)
                                    
                        index = [x for x in index if x >= start]
                        data = data[-len(index):]
                        expected = expected[-len(index):]        
                        
                    # plot the data for this key on the axes
                    ax.plot(index, data, label='observed')
                    if self.fudge == 1:
                        label = 'expected'
                    else:
                        label = f'expected/{self.fudge}'
                    try:
                        ax.plot(index, expected/self.fudge, label=label)
                    except Exception as e:
                        print(e)
                        print(key)
                        print(self.scale)
                        print()

                    if self.history == 1:
                        ax.legend()
                    
                    from blume import taybell

                    title = taybell.shortify_line(key, self.shorten)
           
                    ax.set_title(title)
                    ax.grid(True)

                except Exception as e:
                    print(f'oopsie plotting {key} {commit}')
                    import traceback
                    traceback.print_exc()
                    print(f'{e}') 


            self.commits.rotate()
            if self.commits[0] is self.master:
                self.load_commits()
                keytype = str
                while keytype not in (float, int):
                    self.fields.rotate()
                    key = self.fields[0]
                    keytype = self.spell.casts[key]
                    
                # that is these plots finished
                break

        ax.show()
        #ax.please_draw()

def drange(data):

    return min(data), max(data)
        
def stats(data):

    data = np.array(data)
    results = {}
    results['count'] = len(data)
    results['mean'] = data.mean()
    results['std'] = data.std()
    for percentile in [50, 75, 90, 95]:
        results[percentile] = np.percentile(data, percentile)

    return results

async def run(args):
    
    fish = Cod()
    fish.update(args)
    
    farm = fm.Farm()
    
    farm.add(fish)
    farm.shep.path.append(fish)

    print('FARM STARTING')
    await farm.start()
    print('FARM RUNNING')
    await farm.run()


def hexarg(value):

    hexx = set('abcdef0123456789')
    for char in str(value):
        if char.lower() not in hexx:
            return False
            
    return True

if __name__ == '__main__':

    from pprint import pprint
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('paths', nargs='*', default='.')
    parser.add_argument('--cumulative', action='store_true')
    parser.add_argument('--update', action='store_true')
    parser.add_argument('--itemid', default=None)
    parser.add_argument('--filename', default='data.csv')
    parser.add_argument('--rotate', action='store_true')
    parser.add_argument('--hint', action='store_true')
    parser.add_argument('--monitor', action='store_true')
    parser.add_argument('--download', action='store_true')
    parser.add_argument('--sniff', type=int, default=10)
    parser.add_argument('--days', type=int, default=100)
    parser.add_argument('--history', type=int, default=14)
    parser.add_argument('--filter')

    args = parser.parse_args()

    if args.hint:
        print('Try these with --itemid:')
        for x in ITEM_IDS:
            print(x)
        import sys
        sys.exit(0)

    """ # FIXME: create an object that digests the inputs and gives filename and itemid

    aiming to support a range of possibilities

    a better approach would just be to look and see what is there and figure out what is what.

    imagine a folder:

          foo/data.csv
              26c902bf1da44d3d90b099392b544b81/data.csv

    problem: want to check out different git commits, so need to re-scan for each commit

    later: learning more about git internals and the python git module it should be possible
           to do this cheaply.

    so this code needs putting in a function somewhere
    """
    itemid = args.itemid or ITEM_IDS[0]
    for path in args.paths:
        path = Path(path)

        # if it is a folder, assume target is data.csv
        if path.is_dir():
            path = path / 'data.csv'

        if path.name == 'data.csv':
            tag = path.parent
            if len(str(tag)) == 32 and hexarg(tag):
                itemid = str(tag)
                args.filename = path
                break

    repo = git.Repo(search_parent_directories=True)
    if list(repo.iter_commits('--all')):
        repo.git.checkout('master')

    if args.download:
        url = BASE_URL + itemid + '/data' 

        resp = requests.get(url)

        print(args.filename)
        print(itemid)
        save_data(resp.text, args.filename)
    
        if args.filename in repo.untracked_files:
            print(f"Add {args.filename} to git repo to track")
            sys.exit(0)

        if diff:=repo.index.diff(None):
            print('New data, updating git repo')
            repo.index.add(diff[0].a_path)
            repo.index.commit('latest data')
        
    magic.run(run(args))
    
            

    
