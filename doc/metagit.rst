======================================
 From here to there and back with git
======================================

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


