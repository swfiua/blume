================
 The Magic Farm
================

A collection of objects, each a `magic.Ball`, some that *start* and *run*.

Connected in a graph.

Each edge of the graph, an information pipeline.

A `magic.Shepherd` to take care of it all, also a `magic.Ball`.

Connections to the outside world such as `teakhat.Hat`.

Wouldn't it be nice if the farm could sort out itself, connect things
up so it all runs along?

Perhaps a `magic.RoundAbout` or two will help?

Unix philosophy
===============

Think of *magic.Ball* as a process and all the edges just unix files,
streams of bytes.   Except each stream is a stream of python objects.

It is tempting to restrict things to having at most one input and at
most one output.  In this case we would have:

   * information sources: no input, one output
   * information sinks:   one input, no output
   * filters:             one input, one output
   * cpu hogs?            no input, no output

But even filters might also need to listen to keyboard input asking to
change the filter parameters?

In general, a process has no idea what its inputs and outputs really
are.

It would be good to be able to write something like::

  value = await self.input.get()

In a way that lets other objects manipulate *self.input*.

So perhaps, the following for getting things in and putting things out::

  data = await self.magic.get()

  status = await self.magic.put(data)

And if you want to use something other than the default queues::

  key = await self.magic.get('event')

  status = await self.magic.put(data, 'image')
  
`Ball.get` and `Ball.put` actually work with `ball.radii` which is
some sort of `magic.RoundAbout`.

So have a shepherd or two or more to take care of all the balls and
roundabouts.

Graphs showing connection, one shepherd per connected graph in the
bigger picture.

File systems
============

If farm graph is a tree?

Queue names as `pathlib.Path` 

*stdin*, *stdout*, *stderr* ?

And finally...
==============

**Here's the docs from the `blume.farm` module.**

.. automodule:: blume.farm
   :members:
