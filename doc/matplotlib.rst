============
 Matplotlib
============

As `blume` has evolved I have been reading a fair bit of the
*matplotlib* code, delving into how things are done.

I have also been trying to keep up with what is happening in the
mainstream `matplotlib`_ development and have seen some interesting
things that parallel some of my wishlist.   Managing `figures` without
using the `pyplot` interface is just one such area


I really like the recent `figure.subplot_mosaic()` in recent
releases.   Recursive descent into a mosaic of axes should be fun. 



Python in 2003
==============

Going back to the beginnings of matplotlib:

::

  git show 48111d043e


The first commit goes back to May 12 2003, but includes a changelog
with an entry for 2002-12-10.

It was a time when python needed help from C code to get performance.
In particular, graphics rendering generally involved some sort of C
library.

It is notable that the first version began using `pygtk` to do
rendering and provide a GUI framework. 

Figures, Canvases and Backends
==============================

By September 2003 there were multiple backends.  Creation of a backend
often did not require a great deal of code, as toolkits such as *GTK*,
*Tk* and *Qt* all has the same core components and philosophies.

*Windows* was the predominant platform at this time and these toolkits
aimed to give the same *look and feel* and function as *Windows*
toolkit of the time.

Typically, there was one toolkit per desktop system: KDE is based on
QT, Gnome had GTK, the Gnome Toolkit.

Now these toolkits in turn might support more than one library to do
the actual rendering to screen, so we see `agg` and `cairo` versions
of several backends.

At this time, it was necessary to write some C code in order to wrap
the backend libraries and to provide python interfaces to C code.

Each backend would at some point have a memory buffer representing the
area being rendered.  Exactly how all this worked is entirely up to
the backend.  In general, each back end is capable of doing more than
matplotlib asks, it sticks to a core that all backends can support.

The whole transition to C code generally happens around where their
ceases to be a standard representation of the figure: it is backend
specific. 


Artists
=======

The core of matplotlib is a collection of `Artist` objects, that can
be used to draw pretty much whatever you wish.

Figure and Axes are specialist artists that together work to display
data in a highly configurable way.



Callbacks
=========

Each GUI toolkit provides a mechanism to call functions when certain
events happen, such as a resize of a window or a draw of an area of
that window.

Keyboard and Mouse events are also handled by the toolkit.

Matplotlib provides a library for registering callbacks and each
backend implements the details.

Meanwhile, in `blume` I have my own mechanisms for handling callbacks.


rcParams
========

There is a module devoted to *rcParams*.

Currently, 304 specific variables that control the behaviour of matplotlib.

A collection of functions to validate input.   `blume.magic.Spell`
may be able to borrow some of this.


Drawing Text
============

Matplotlib relies on the GUI frameworks to render text.  It is not
until a renderer object is available, that text can be measured or
rendered.

Back in 2003 this was further complicated by font support being such
that only a small set of point sizes were available.

This very much complicates laying out of axes in a mosaic.


Legends
-------

The `legend` code uses the objects defined in `offsetbox`.  The idea
is that things such as padding around a box should be done as a
multiple of the fontsize in points.

Then as the fontsize is scaled, the whole legend scales in the same
way and maintains proportions.


Tables
------

The approach here was to try to find the largest font that made the
text fit the space available.


Ticks, Titles and more
----------------------

????

Breaking the rules
==================
