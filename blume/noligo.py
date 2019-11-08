import random
from datetime import date

from collections import Counter

import argparse

def sim(days, rate):
    hits = []
    for day in range(days):
        if random.random() < rate:
           hits.append(1)
        else:
           hits.append(0)
    return hits


def longrun(hits):
    run = 0
    best = 0
    for hit in hits:
        if not hit:
            run += 1
        else:
            best = max(best, run)
            run = 0

    best= max(best, run)
    
    return best

def to_date(value):

    if not value:
        return date.today()

    year, month, day = [int(x) for x in value.split('/')]

    return date(year, month, day)

parser = argparse.ArgumentParser()

parser.add_argument('-t', type=int, default=1000)
parser.add_argument('--hits', type=int, default=43)
parser.add_argument('--start', default='2019/4/1')
parser.add_argument('--last', default='2019/9/30')
parser.add_argument('--end')

args = parser.parse_args()

# do the simulation
n = args.t
cc = Counter()

start = to_date(args.start)
end = to_date(args.end)
last = to_date(args.last)

days = (end - start).days
hits = args.hits

rate = hits / days

print(f'hit rate: {rate} events per day')

for x in range(n):
    
    cc.update([longrun(sim(days, rate))])


total = 0    
for k in sorted(cc.keys()):
    total += cc[k]
    print(k, n-total)

print(f'days since last event {(end - last).days}')
