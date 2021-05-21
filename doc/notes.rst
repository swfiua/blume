Blume
=====

It started with just a class to draw tables alongside matplotlib
plots.  Years ago I wrote some matplotlib python to do the job of
displaying a grid of text boxes.  How to create a general interface
that allows for things such as nested row and column labels?

So this got me thinking about tables.

Rows and columns of data.

Sometimes with column or row labels.

Tables: rows of data, each row a number of columns.

How to explore and share the data?

An aside that two types of tables are in mind: csv files of data and
image files.  An image is just a rectangular grid of values, so it
fits the model.

Sometimes (usually?) I want to use both.  An image in the background,
overlaid with other data.

Then there is this idea of content addressable filesystems, and how
this relates to git.

For starters, if blume is running in a git repository it would be good
to let you navigate the git history of a file.  I think I know enough
now to do that reasonably efficiently without doing any changes to the
files on the disk.

My inclination here is to let git do as much of the work that needs to
be done.

Git is really good at lots of things.

I have also been thinking about bots in relation to blume and
exploring data.

I am imagining some sort of bot that randomly plays with the
attributes of things running in the system.

Perhaps manipulate meta data and save it in a git branch, in case it
turns out to be useful later.



