=============================
 What is the plan from here?
=============================

First of all, what is going on here? 

It started as a place to draw tables with `matplotlib`.  Or rather a
home for a new version of the `matplotlib.table` module that I created
way back in the day.

The table tries to be clever and pick the biggest font it can find
that fits the data.  I barely knew what I was doing creating this
table, I was finding my way around `matplotlib` as I was writing the
code.   It quietly did the job for over ten years as I was busy
elsewhere.

More recently I tried to fix up some of its problems and add some new
features.  It was difficult to do this in backward compatible ways.

Hence, `blume` is a new home for the `table`.

I decided it would be a good place to accumulate some examples of
tables in use.   Examples of ideas that take my interest.

I try to look for common themes across the examples and let that guide
what happens next.

As things have progressed it has become clear that everybody already
has a table: pandas, astropy, mathematica, every database query.  So
the scope of this project has expanded somewhat, to how to explore
tables of data, with `matplotlib` generating all the pictures?

As far as python is concerned, I am leaning towards tables as lists of
dictionaries as the lowest common denominator.  With the same set of keys
for each item in the list, there is a natural mapping to dictionaries
with lists as values.

I am particularly interested in what I call, *spherical data*.  Data
where the observations lie on the surface of a sphere.  Cosmological
data and output from global climate reanalysis models.

Values that indicate a time or a place are of particular interest.  I
find myself repeatedly parsing and transforming such data to suit
some, often implicit, choice of coordinates.

It feels that 99.99% of computing is trying to transform data from one
coordinate system to another, one world view to another.

As an example, the `astropy` world is generally using the `healpy`
software to store and manipulate data in the `healpix` format, where
each pixel represents an equal area.  It comes with tools to do
spherical harmonic analysis, and was used to detect harmonics in the
COBE, Cosmic Microwave Background data.

It also comes with some built in plotting, using `matplotlib` as the
plotting engine.

Healpix does not have a table, as far as I know, but it is my current
favourite for spherical data.

The meteorologists are using a grid based approach, dividing the
planet into a rectangular grid of latitudes and longitudes.  This has
some benefits, in particular, it gives higher resolution at the
poles.  Computers like grid calculations.

The `astroquery` project provides tools to query data from a whole
host of astronomical projects, using a common query language and
returning results in common formats.

This may well reflect the extraordinary amount of international
collaboration there is in the world of astronomy.

There is also no shortage of fascinating data sets to work with, and
the set is growing too.

And gravitational waves are now a thing too.


Interactive magic
=================

I find myself writing a number of short scripts, 100 lines or so, to
display some data with `matplotlib`.  As I explore the data the script
acquires a number of variables that control what is displayed.

At this point I often resort to `argparse` to add a few command line
options to control the key variables.

A typical blume module creates a `blume.magic.Ball` and adds it to a
farm which ends up running the `Ball.run` co-routine in a loop.

It is possible to have keyboard events call co-routines which can in
turn change the values.

This is a fairly quick way to build an interactive tool to explore
data.

However, it soon gets tedious writing repetitive code for the
co-routines.  Then you have to decide what key to assign to each
routine.

The latest enhancement, is to simply allow me to scroll through the
attributes of the object, by pressing space, until I find the one I
wish to change.  Then a bunch of keys are matched to various
co-routines that offer various changes.

It is a bit like running code in an interactive debugger.

This is all managed by a `Shepherd`, via which you can browse the
values of the `Ball` objects, select one and change it.

Just run::

  python -m blume.mb -r

This one generates images of the Mandelbrot set.  It is a good one to
experiment with the interactive mode.

Run things from a console.  Type 'h' and you will see what keys do
what.  At this point it is a bit of an adventure game.  All going well
'q' should quit.  Failing that, 'Control-c' is your friend.

Pressing 'i' shows the attributes of the object that is currently
selected.  Spacebar lets you scroll through its attributes and then
press 'h' to see the keys that will change the value.

You can do much of what I am trying to do with a *Jupyter notebook*
and some *ipython widgets*.

I would really like to have dynamic key bindings that adapt to usage,
but that will have to wait for the `blume.magic.Roundabout` to
actually be magic.

Cosmology
=========

A number of modules relate to astronomical data.

  * `blume.gaia` downloads and displays data from the Gaia survey of
    our galaxy.  Over a billion observations and growing.

  * `blume.cpr` implements galactic rotation curves per [AP].  This
    module is a natural companion for Gaia data.

  * `blume.gw` plots waveforms for the waves generated by different
    mergers of black holes and neutron stars of specified sizes.

  * `blume.dss` visualise geodesics in de Sitter space, again per [AP].


At some point it will be productive to combine the ideas in the `cpr`
module with the data in the `gaia` module.  It would be good to try to
get good estimates of both the mass, given the angular velocity of the
black hole at the centre of our galaxy.

There are already a number of excellent projects processing this
data.  Many of these use some sort of Bayesian re-estimation to fit
some sort of galactic model to the data set.  It should be noted that
prior assumptions can still impact such models.

I suspect some of these will be using the assumption that Sagittarius
A* is at the centre of our galaxy and is just 26,000 light years away,
but I have not followed that up.

There is a fair amount of work in understanding all the follow on
processing that is being done on the dataset.  The raw observations
have a lot of sampling noise, multiple observations of each source.

For now, I think it is worth waiting for more data releases.  I do not
think it will be long before we have a much better picture of the
structure of our galaxy and our place in it.

The de Sitter module is just a stub at this point.  It has lead to the
discovery of the `einsteinpy` project.

That was where, I learnt that there is a *Gödel metric*, a solution to
Einstein's general relativty equations.

The fascinating thing is that his solution implied that the universe
should, in some sense be rotating.  He would often ask if observations
had yet confirmed this, only to be told, "not yet".

I have been fascinated by Kurt Gödel since I learned of his wonderful
incompleteness theorems, all mathematicians have cause to be greatful
for these theores.

I am curious what Gödel would have made of the Cosmic Microwave
Background.

Which reminds me, there is this delight to explore::

  Legacy Archive for Microwave Background Data Analysis

  https://lambda.gsfc.nasa.gov/

And the accelerating expansion of the universe.

Could this not be explained, in de Sitter space, by the probability
that a distant galaxy is a new arrival increases as you get further
away?

Some distant galaxies may be exibiting less red shift than would be
expected given their distance.

Dwarf, blue galaxies, if you like.

It should be possible to calculate what we would expect to see based
on [AP]


Putting it all together
=======================

Once the de Sitter module is a little further along, the goal is to
develop a model that might explain the gravitational waves we are
seeing, not as black hole mergers, but rather as waves arriving from
giant black holes at the edge of our visible universe.

The puzzle is why we are not seeing gamma ray bursts at the same time
as each gravitational wave.

The belief is that we should only see these when one component is a
neutron star, and even then, not always.

Paradox
=======

Simulataneously believing that rotating masses induce a rotation on
space time and that it is not possible for black hole mergers to
generate gravitational waves as they spiral into each other would
appear to be some sort of paradox.

How to resolve this?

Multi-messenger astronomy may very well hold the key to resolving this
mystery and many more.

The exciting part is that we already know some gravitational waves are
followed up by a short gamma ray burst, and observations further down
the spectrum too.

It would be surprising if these new observations do not change out
current thinking in some significant way.


[0] http://msp.warwick.ac.uk/~cpr/paradigm
