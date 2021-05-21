========
 Issues
========

A handful of issues have been raised on *github*.

For now, I will document things that I am still thinking about.




Add ability to ellipsize text overflowing in table cell
=======================================================

https://github.com/swfiua/blume/issues/2

The current code is supposed to shrink the font until the text fits,
but I seem to recall there are subtleties with the row labels.

A simple fix would be to have a wrapper that is passed a maximum cell
width in characters and runs a shortening algorithm on inputs as
necessary and feed the result into the existing table code.


https://github.com/swfiua/blume/commit/4f4ddb1849e62d7d2d3f42bc8ef73f881680d6ba


Allow cells to span multiple rows and columns?
==============================================

https://github.com/swfiua/blume/issues/3

The main issue here is that the current code assumes each cell just
spans a single row/column.

There is also some weirdness relating to row labels, which is one of
the places where I see spanning multiple cells could be particularly
useful. 

Another puzzle is how to specify the input?

Working at the `Table.add_cell` level we just need to add a span.

Making it all work is quite a bit more complex, but the end result
might simplify a lot of things.

For now I am thinking more generally about tables and just how
flexible things can be without writing an entire spreadsheet.

Core class should not treat negative rows specially
===================================================

Rather, the wrapper function should indicate that the negative rows
are special by setting the appropriate cell options.

More generally, a core class that just lays out grids of cells with
various constraints on rows and columns, provided as data.

The core needs to handle things like 

