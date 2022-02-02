"""From here to there and back with git.

A server with terrabytes of open data.  How to share the work of
sharing the data?

A server with petabytes of data, but how to share that data?

Let's begin with an idea of an event.  A time, a place and a value.

Everything else about the event can be thought of as meta data.

Time and place may only be known approximately, or inferred from the
meta data.

So chop the data into chunks, where each chunk is described by a
relatively small amount of meta data (a line in a csv file).

If the meta data is large, chop it into blocks, also described by meta
data, until meta data reaches a size that is manageable in git.

Share the git repository.

Build a simple server, that has a magic function, that can generate
the block given the meta data, cache and serve those blocks, wnen
asked for by checksum.

The server checks the cache before generating a block, so is efficient
for repeated calls to the same block.

When the disk gets full, delete old blocks.

Now build tools to use the meta data to browse the data.

Sometimes there is just the data, no meta data.  In this case, see
what meta data can be generated from the data and store that in git.

**Wait this all sounds familiar**

It is essentially a discription of git,  the magic function being
whatever creates the blob of data.

I suspect it will also turn out that *git* is fine at creating large
repositories of data, just you probably do not want to serve the whole
thing at once.

That might be gits downfall, if its hash function includes the parent
commit id, which I believe it does.

I am guessing we can supply our own function if need be.

Time to write some metagit python and see what happens.

More thoughts: branches of course, part of the meta data puzzle.

Merge branches into collections of blobs.

And merge those into branches again.

met-a-git
=========

Pronounced in a strong Quebecois accent, "met-a-geet"

Or is it me-tag-it?  

Create the meta data to help you navigate the data.

It started as meta-git.  Meta data and data too, in git.

I've lots of csv files, sorted in folders, so it would be good to
generate some meta data and browse them.

That's the me-tag-it.

What if it is already in git?  

We will create a branch and celebrate, let's call it metagit.

And in the every silver lining has a cloud stakes, it turns out that
John Hopkins University is using git to host global Covid-19 data.

https://github.com/CSSEGISandData/COVID-19

I cloned it a while ago, it was too depressing.  But there are lots of
good stories in this data too.

Now let's make some meta-data so this cloud has a silver lining.

"""

# Standard library
import argparse
from pathlib import Path

# might as well print pretty -- hmm syntax highlighter looks confused
from pprint import pprint as print

# blume
from blume import magic

from blume.farm import Farm

# talk to git
import git

def meta(repo):
    
    return None



class Globe(magic.Ball):

    async def start(self):

        print('hello')
        repo = git.Repo(self.path)

        if self.info:
            self.status()

    def status(self):
        """ Summarise what is here """

        # get list of paths
        

    
if __name__ == '__main__':

    farm = Farm()

    globe = Globe()

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-sniff', type=int, default=10)
    parser.add_argument('-history', type=int, default=14)
    parser.add_argument('-suffix', default='csv')
    parser.add_argument('-info', action=store_true)

    args = parser.parse_args()

    globe.update(args)
    
    farm.add(globe)
    
    farm.run()


    
