
It's just been declared in Quebec that "snow sports instructors" are
essential workers (?), so it looks like I am going to be busy from
Sunday onwards, although we have rain forecast for Xmas so who knows.

Something has happened with the Ottawa data resulting in this
thrashing around to get things working again:

https://github.com/swfiua/blume/commit/5b1b5f81bd34dab87cb4c65cee7ecf1e9574ceb9

I can't leave the magic like that.... I want to keep the magic simple,
also want the magic to figure out stuff and do the right thing.

What am I trying to do with the `magic.Spell` part of blume?

The thing that turns data into blume tables?

I am increasingly needing to write something to generate "meta data".
Clues, if you like to help the blume programs interpret what is
there.  

I have a whole folder on my laptop of various folders of data from
different sources, data from sensors on various raspberry pi's I have
had running at various points.

Most of the data is just csv files, but they are all messed up in
different ways. The good news is it is mostly from code I wrote, so I
know some of the ways it is broken.

The data from the sensehats is a good example. 

The karmapi code just reads the sensors, records the values as a
record to a file. It sounds simple, what could go wrong?

I have different folders for each year/month/day, with a bunch of
files: weather, compass, gyro and accel.

The problem is that when the pi's wake up, they don't know where they
are or what time it is. 

And my code just tries to append to the files for the day. And
sometimes it all goes wrong and the append ends up over-writing data
and the header might be missing.

I also use a thing called cron to schedule a new task each day and
combine it with the monitoring code exiting at midnight, it all sort
of works -- and for the pi's that have stayed in one place for a
while, the whole thing has worked pretty well.

... back to blume and the ocixx example.

I hadn't run the code for a week or so, so I can't pin when, but they
changed from yyyy-mm-dd to yy-mm-dd for the dates in one of the data
feeds -- I am sure there is a story to why it changed.

Suffice to say it gave matplotlib's magic date handling for axis
labels some indigestion.

Dates always cause trouble eventually. 

The observations are all good in the karmapi data, it is just that
there is some uncertainty in the actual time and place of the event.

Dates and locations, the very things that define an event are the very
thing we have difficulty with.

There is a clue in the timestamp that might help with time and place.
There's also weather data and data from surrounding times that might
help adjust the window.

Some data comes with pictures too, if the pi has a camera, with
consistent timestamps.

The fixes here were just a minimum to figure out what was up and then
get it working so I can see the latest Ottawa plots again.

There are so many little changes like this data throws at us. 

Maybe the meta data just gives us information about expected
distribution of values?

I think what I am looking for is something that allows me to tune
things, but somehow make those tunings available more generally -- the
way to do that might be to go up a level and re-generate the meta
data, given your new knowledge.

And the probability that the year includes the century too?

Update
======

Just came across this old note that git wasn't managing for me.

No actual magic yet.  But things are warming up and it won't be long
until I have more time on my hands to think of reasons not to write
code.

I have been skiing with what I call piski.

It is raspberry pi with a sense hat and a fairly low resolution,
fish-eye camera.

It records all the data from the sense hat, currently ten times a
second, as well as taking a picture once a minute.









