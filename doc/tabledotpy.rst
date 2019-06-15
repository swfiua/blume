=========================
 Matplotlib and table.py
=========================

I have recently submitted a bunch of pull requests to *matplotlib* in
an attempt to address some issues with the code that go all the way
back to when it was first created some time in 2004.

I thought it might be worthwhile to describe a little of the history
of this particular module.

The dark ages
=============

Many years ago I was working with python and needed to produce a plot
something like this:
https://matplotlib.org/2.0.1/examples/pylab_examples/table_demo.html

A stacked bar chart, with a table of numbers beneath.  The result had
to be close enough to the spreadsheet based solution that my code was
replacing.

It was 2004, I believe.  A little googling let me to *matplotlib* and I
was able to get a copy of the latest source code.

I was working in Ireland, with a long commute involving car, train and
folding bicycle.  The train part of the journey provided 30 to 40
minutes coding time twice a day.  I was also suffering from an
undiagnosed mystery illness that left me fatigued all the time.  Later
I was diagnosed with Myasthenia Gravis.

On the train that evening and the following morning I started to
explore the code and was pleasantly surprised that adding *stacked bar
charts* to the *axis.barh* code not a big change.

When I arrived at work I created a small patch with my changes and
emailed it off to John Hunter and got busy with other problems I was
working on.

Shortly after 2pm Dublin time, I received a response from John.  It
was full of thanks and encouragement, along with a few suggestions for
improvements to my changes.   I cannot stress enough how encouraging
John's response was.

I wrote back and explained that I also needed a table beneath the bar
chart with the data underlying the plot.
 
John pointed me at the *patches* code and explained how I should be
able to create some sort of *Cell* object by combining *Rectangle*
objects with *Text* objects.

That is how the *table.py* came into being.  Over 2-3 weeks of train
journeys it slowly emerged, along with the table demo gallery
example.

Fonts, padding and renderers
============================

*Matplotlib* tries to make easy things easy and hard things possible.

With this in mind I wanted the table to automatically adjust the font
to make the best use of the space available.

There also needed to be some way to decide how much padding should be
placed between the text and the border of the cell.

All this is complicated by the fact it is not until a table is drawn
that the code gets to see *Renderer* object.  It is the *renderer*
that provides methods to measure things like how much space text will
need.

I also learned that there are more than one coordinate system in play,
*table* coordinates and some other coordinate system (axis
coordinates?) with affine transforms to change from one to the other.

It is important to realise that this code was written on a crowded
train, by someone who barely understood what they were doing, with a
debilitating auto-immune disease and a demanding job whilst learning
their way around as they went along.

John Hunter was wonderful throughout this process.  *Matplotlib* was
evolving rapidly and John's patience and guidance was helping grow the
developer community around the project.   It was fun to be part of this.

Padding
=======

For padding around the text a *PAD* class variable was added to the *Cell*
class.  The idea was to multiply the height and width of the text by
*PAD* to calculate how much padding to add to the cell.

Auto font sizing
================

The original code for this would start with a 10 point font (or rather
use the class variable *table.FONTSIZE*) and then reduced the fontsize
one point at a time until all the text fitted.

If you had space for a larger font, then you needed to set
*table.Table.FONTSIZE* either prior to creating the table, or after
creation, but before it was drawn.

Problems
========

Between the padding and the automatic font sizing, many table were not
pleasing to the eye.  Text too close to the cell borders, excessive
horizontal padding for cells with long text strings and not enough for
1-2 character strings.  The *table_demo* example was always the ugly
duckling of the matplotlib gallery.   Over the years a few bug fix here
and a change of colour palette had improved things somewhat, but the
table was still not the beautiful swan I had in mind.

When viewing plots with *matplotlib's* interactive viewers other
problems become apparent.   Resizing windows results in re-calculation
of the font size and often resulted in a tiny font, making it
difficult to read the text.

Some of the names used for methods and data attributes lack
consistency with the rest of *matplotlib*.  In particular, I have a
tendency to use English rather than US spelling, so *color* might be
spelt *colour* and *center* spelt *centre*.  *row* was spelt *col*
or vice versa in a couple of places too.

I recall spending some time try to get the code to behave, but was
unable to tame it and moved on to other things.

Fast forward to today
=====================

I had always had good intentions to go back and fix up the issues in
the table, but before I knew it nearly 13 years had passed.

A couple of years back I was working on a project that needed a table
of data as well as plots of the same.

I seem to have spent an inordinate amount of time over the years
getting tables of various sorts (html, gtk tables, qt and wx too) to
display nicely.  Most of these efforts involved proprietary code that
I no longer have access to.

I remembered the *matplotlib* table widget and decided it was time to
take another look at this, maybe it could be the last table I would
ever need.

I made some changes to the automatic font size selection code, in
particular, allowing it to grow as well as shrink the font.

I changed the horizontal alignment from *center* to *center-baseline*.

I also started to experiment with colouring the cells according to
their values.  I found the black cell borders unpleasing to the eye
and felt the tables would look better if these edges were painted the
same colour as the cells, as per the image below.

.. image:: blume.png

Now in the intervening time *matplotlib* has moved on from a fledgling
project to a key part of the python data science stack.

As a mature project, changes to API's, method or attribute names need
careful consideration.  Given some of the problems with
the table code, there is this *Catch-22* it was likely that user code
was delving into *Table* internals making it more likely that fixes
would break end user code.

Software engineering and python have both moved on too.  Python now at
3.8 was only at 2.4.

Back in 2003, test driven development had not quite hit the mainstream
and decentralised version control systems were just starting to show
promise, but again not quite mainstream.

I worked on a pull request, but it did not quite get over the line
before the *matplotlib* version jumped to 3.0 and there were enough
changes that my *git* skills were not up to the job of merging the new
*master* with my changes.

A change of job also meant that my immediate need for a table
disappeared and so the fixes languished.

Now I have more time on my hands and so have had another go at fixing
up the table.

It has been a strange experience getting back into the code.  Over the
years 75% of the lines have had some sort of change.  A large
proportion of the changes are just formatting, mostly to make *sphinx*
happier, but there are some important bug fixes along the way.  So I
find myself asking did I write things this way?

There are also some new features, in particular CustomCell.  This one
was strange, since the code looked like something I might have
written.  

Then there wonders such as this, which is one of mine I believe::


    def _approx_text_height(self):
        return (self.FONTSIZE / 72.0 * self.figure.dpi /
                self._axes.bbox.height * 1.2)


I think the idea is to set the cell height such that it would give 72
lines of text if it covered the full axes, but actually have no idea
what this is about.

Overall, much of he code is more complex than I would like.  Some of
this complexity comes from attempts to work around issues related to
the font-sizing.  In short, me trying to figure out what was going.

I had hoped that over the years that someone with a good grasp of
*matplotlib* internals might have been able to figure out what was
going on in the *table* code, but given the effort it has taken for me
to understand my own code, this maybe was never going to happen.

The good news is I finally got to the bottom of some of the font
sizing issues I was seeing.

In short, confusion in the code about which coordinate system is being
used.   Some functions called from two different places in the code
with different assumptions about the coordinate system.

Cell padding was one area affected by this.  Since the padding is just
a multiple of the text length and the coordinate transforms are
(always?) affine, it does not matter of you calculate the padding and
then transform or transform and then calculate padding.

But when I tried to change the padding to be a simple multiple of the
fontsize, things blew up, since the two operations are no longer
transitive. 

