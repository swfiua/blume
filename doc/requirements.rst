==============
 Requirements
==============

.. module:: blume

Since some maybe here just to get a `matplotlib.table` working in
matplotlib or just want to try examples with `blume.eggshow` no
requirements other than an appropriate version of `matplotlib` will be
required.

Some modules here may require `astropy` and/or `healpix`, but many
modules should just run fine.

All the interactive tools currently require `curio`_ and `networkx`_


Update
======

I have decided to change the requirements so any code that
*blume.magic* and *blume.farm* and the core that makes everything
work, will now install the relevant dependencies.

I will still try to keep dependencies minimal.

I am making this change as I am starting to use the core in other
projects, and I want to make it easy to install those projects.

Sorry for the inconvenience.

What about the table?
=====================

If you really need it and do not want the other dependencies, there
are options such as taking a copy of the code.

See `news`_ for updates on where the project currently is heading.
