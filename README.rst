==========
 mpltable
==========

Displaying data as tables in matplotlib.

Mpltable provides a replacement for the matplotlib table module.

It fixes a number of issues with the existing table and has:

* more reliable code for automatically setting the font size to make
  best use of the space available.

* Padding between text and the cell edges which works better across a
  range of text sizes.

* First row of cell data is now row 0 regardless of whether the table
  has a row header.  The row header is row -1.

* New options to allow cell edge colours to be specified.  

To use the new table, just import `mpltable.table` and use that to
create your tables instead of the `matplotlib.table.table`.
  
::

   from mpltable import table

   tab = table(ax, ..)


The first parameter to table should be an *matplotlib.axes*.

If you are using the *pyplot* interface, note that calling
*pyplot.table* will use `matplotlib.table.table`.

Instead import table from mpltable and use as follows::

  from mpltable.table import table
  tab = table(plt.gca(), ...)



Install
=======

Using pip::

  pip3 install mpltable


Examples
========

The *examples* folder has a number of demonstrations of what can be
done with this table.
  
   
Testing
=======

Run tests using::

  pytest tests

Image comparison tests
----------------------

???
