==================
 Where are we at?
==================

What's happening with the `blume.table.Table`?

2020/02/03
==========

It's winter.   So that means I am spending a lot of time teaching
people to ski and not so much on other projects, *blume* included.




Beautiful
---------

A simple interface to view images (*matplotlib plots*) produced by
objects connected together by a graph of asychronous queues.


View the queues.


Little
------

The aim is to keep the code here to a minimum.   A few thousand lines.



Universal
---------

I am on a bit of a cosmological diversion thanks to the wonderful work
of Colin P. Rourke.  In particular, his book, *Another Paradigm for
the Universe* [1]

His book has some mathematica code that allows you to simulate
galactic rotation curves, using the mathematics of the book.

The `blume.cpr` module is an attempt to re-implement that code in
python.


Matplotlib
----------

The tenuous link with the `blume.table` is that the *mathematica* code
in the book makes use of a *mathematica table*  object.

Engines
-------


curio
'''''

healpix
'''''''



Pandas
''''''

For another take on *table* there is `pandas.DataFrame`.

Roadblocks
----------

Assigning events to keyboard actions
''''''''''''''''''''''''''''''''''''

I have spent a disproportionate amound of time thinking about this
part of the user interface side of things.

I am focussing on keyboards and wanting to keep things simple the code
generally just maps a key to a co-routine.

Does not feel like it should be part of this code at all, the code
just needs to advertise what co-routines are available for interactive
use and let some other tool deal with what events trigger what?

Maybe the code just hints which co-routines are more likely to be
called?

I am wondering if this can be done in a way that isn't annoying:  you
have to re-teach the computer every time you play?

How to let the user navigate their way?

Magic roundabouts?

Directed graphs of co-routines sharing data with queues.

[1]  http://msp.warwick.ac.uk/~cpr/paradigm/
