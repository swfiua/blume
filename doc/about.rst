=====================================================
 BLUME, Better Looking, Universal, Matplotlib Engine
=====================================================

*blume*, like bloom, a place where seedlings, orphans looking for a
new home, to turn into flowers.


Better Looking?
===============

*Better Looking?*  Really?

Maybe BL stands for something else?

BL big and little?

Universal
=========


Well right now there's only me here, so that's hardly Universal.

But the code I am building here `blume.magic` and `blume.farm` are
aimed at helping me build and run software that is exploring,
modelling, simulating, forecasting and displaying information.


Matplotlib
==========

Turns data into pictures.

There is not much that *matplotlib* cannot do in the world of drawing.


Engine
======

Run small snippets of code that create an interesting *matplotlib*
figure?

The *Farm* and its *Magic*.

The idea with the farm is a collection of *Balls* you can *start* and
*run* as you like.

Connections between *balls* turn them into a graph which `networkx`
handles very nicely.



*matplotlib*

*curio*

*networkx*


Matplotlib and python and other magic wonders
=============================================



curio
-----


Beginning with Tables
---------------------

The initial motivation for this

See `tabledotpy` for an account.

An initial *seedling* is `blume.table`.

The initial goal here is to provide an upgrade to the
`matplotlib.table` module.

There is a version here that tries to work around problems in the
current module.

There are improvements in the automatic font sizing and cell padding and
some new options available.

In amongst all this are some changes to the API the current module
(matplotlib>=3.1) module exposes.

There is a good chance if you switch your code to use the table here
that everything will work just fine, hopefully with some slightly
better looking tables.

So the question remains on how best to transition to the new table?

In particular,

  #. what does the end goal look like and

  #. do we need an interim fix to existing `matplotlib` table?


It may be too early to decide, but if there is some sort of working
precedent to follow that would be great.

As far as the tables are concerned, my plan is to work on a few
examples, using tables in a variety of ways and see what ideas come
out from the API point of view.


Karma Pi too
------------

A personal tool kit for working on collecting analysing and displaying
data.  How to do this in a collabortive way?

A collection of 50 or so short python modules that provide some tools
for displaying and collecting data. Some aimed at a specific problem
or data set, others more general purpose.   Random explorations.

It is time to take some of the core ideas in karma pi and re-implement
them here.

Data
''''

A time, a place, a value.

And meta data explaining what the value represents.

But data often in rectangular grids with a particular focus on grids
which are just projections of grids laid on the surface of a sphere.

And finally
-----------

Interactive *matplotlib*, with *async* support.


Blume Zen
=========

*Everything is perfect, blume no longer exists.*

Big and Little.


Evolution of a module
=====================

An idea.  2-300 lines of code maybe?

Oh and I can start with *foo.py* which has half of what I need.

Hack around until it works well enough for current needs.

  #. it works

  #. it turns out to be rather more work than you had hoped

  #. it has created enough new ideas that it has been abandonned for
     now
     
  #. realised we have had this problem before and are going round in circles



