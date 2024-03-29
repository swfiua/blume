# dataklasses.py
# 
#     https://github.com/dabeaz/dataklasses
#
# Author: David Beazley (@dabeaz). 
#         http://www.dabeaz.com
#
# Copyright (C) 2021-2022.
#
# Permission is granted to use, copy, and modify this code in any
# manner as long as this copyright message and disclaimer remain in
# the source code.  There is no warranty.  Try to use the code for the
# greater good.

# dataklasses
"""# Readme

The original Readme.md, included here to encourage the concept of a
single file git repository.  A git repository that comes with just one
file.


Dataklasses is a library that allows you to quickly define data
classes using Python type hints. Here's an example of how you use it:

```python
from dataklasses import dataklass

@dataklass
class Coordinates:
    x: int
    y: int
```

The resulting class works in a well civilised way, providing the usual
`__init__()`, `__repr__()`, and `__eq__()` methods that you'd normally
have to type out by hand:

```python
>>> a = Coordinates(2, 3)
>>> a
Coordinates(2, 3)
>>> a.x
2
>>> a.y
3
>>> b = Coordinates(2, 3)
>>> a == b
True
>>>
```

It's easy! Almost too easy.

## Wait, doesn't this already exist?

No, it doesn't.  Yes, certain naysayers will be quick to point out the
existence of `@dataclass` from the standard library. Ok, sure, THAT
exists.  However, it's slow and complicated.  Dataklasses are neither
of those things.  The entire `dataklasses` module is less than 100
lines.  The resulting classes import 15-20 times faster than
dataclasses.  See the `perf.py` file for a benchmark.

## Theory of Operation

While out walking with his puppy, Dave had a certain insight about the nature
of Python byte-code.  Coming back to the house, he had to try it out:

```python
>>> def __init1__(self, x, y):
...     self.x = x
...     self.y = y
...
>>> def __init2__(self, foo, bar):
...     self.foo = foo
...     self.bar = bar
...
>>> __init1__.__code__.co_code == __init2__.__code__.co_code
True
>>>
```

How intriguing!  The underlying byte-code is exactly the same even
though the functions are using different argument and attribute names.
Aha! Now, we're onto something interesting.

The `dataclasses` module in the standard library works by collecting
type hints, generating code strings, and executing them using the
`exec()` function.  This happens for every single class definition
where it's used. If it sounds slow, that's because it is.  In fact, it
defeats any benefit of module caching in Python's import system.

Dataklasses are different.  They start out in the same manner--code is
first generated by collecting type hints and using `exec()`.  However,
the underlying byte-code is cached and reused in subsequent class
definitions whenever possible. Caching is good. 

## A Short Story

Once upon a time, there was this programming language that I'll refer
to as "Lava."  Anyways, anytime you started a program written in Lava,
you could just tell by the awkward silence and inactivity of your
machine before the fans kicked in.  "Ah shit, this is written in Lava"
you'd exclaim.

## Questions and Answers

**Q: What methods does `dataklass` generate?**

A: By default `__init__()`, `__repr__()`, and `__eq__()` methods are generated.
`__match_args__` is also defined to assist with pattern matching.

**Q: Does `dataklass` enforce the specified types?**

A: No. The types are merely clues about what the value might be and
the Python language does not provide any enforcement on its own. 

**Q: Are there any additional features?**

A: No. You can either have features or you can have performance. Pick one.

**Q: Does `dataklass` use any advanced magic such as metaclasses?**

A: No. 

**Q: How do I install `dataklasses`?**

A: There is no `setup.py` file, installer, or an official release. You
install it by copying the code into your own project. `dataklasses.py` is
small. You are encouraged to modify it to your own purposes.

**Q: What versions of Python does it work with?**

A: The code will work with versions 3.9 and later.

**Q: But what if new features get added?**

A: What new features?  The best new features are no new features. 

**Q: Who maintains dataklasses?**

A: If you're using it, you do. You maintain dataklasses.

**Q: Is this actually a serious project?**

A: It's best to think of dataklasses as more of an idea than a project.
There are many tools and libraries that perform some form of code generation.
Dataklasses is a proof-of-concept for a different approach to that.  If you're
a minimalist like me, you'll find it to be perfectly functional.  If you're
looking for a lot of knobs to turn, you should probably move along.

**Q: Should I give dataklasses a GitHub star?**

A: Yes, because it will help me look superior to the other parents with
kids in the middle-school robot club.

**Q: Who wrote this?**

A: `dataklasses` is the work of David Beazley. http://www.dabeaz.com.

"""

__all__ = ['dataklass']

from functools import lru_cache, reduce

def codegen(func):
    @lru_cache
    def make_func_code(numfields):
        names = [ f'_{n}' for n in range(numfields) ]
        exec(func(names), globals(), d:={})
        print('DDDD', d)
        return d.popitem()[1]
    return make_func_code

def patch_args_and_attributes(func, fields, start=0):
    return type(func)(func.__code__.replace(
        co_names=(*func.__code__.co_names[:start], *fields),
        co_varnames=('self', *fields),
    ), func.__globals__)

def patch_attributes(func, fields, start=0):
    return type(func)(func.__code__.replace(
        co_names=(*func.__code__.co_names[:start], *fields)
    ), func.__globals__)
    
def all_hints(cls):
    return reduce(lambda x, y: getattr(y, '__annotations__',{}) | x, cls.__mro__, {})

@codegen
def make__init__(fields):
    code = 'def __init__(self, ' + ','.join(fields) + '):\n'
    return code + '\n'.join(f' self.{name} = {name}\n' for name in fields)

@codegen
def make__repr__(fields):
    return 'def __repr__(self):\n' \
           ' return f"{type(self).__name__}(' + \
           ', '.join('{self.' + name + '!r}' for name in fields) + ')"\n'

@codegen
def make__eq__(fields):
    selfvals = ','.join(f'self.{name}' for name in fields)
    othervals = ','.join(f'other.{name}' for name in fields)
    return  'def __eq__(self, other):\n' \
            '  if self.__class__ is other.__class__:\n' \
           f'    return ({selfvals},) == ({othervals},)\n' \
            '  else:\n' \
            '    return NotImplemented\n'

@codegen
def make__iter__(fields):
    return 'def __iter__(self):\n' + '\n'.join(f'   yield self.{name}' for name in fields)

@codegen
def make__hash__(fields):
    self_tuple = '(' + ','.join(f'self.{name}' for name in fields) + ',)'
    return 'def __hash__(self):\n' \
          f'    return hash({self_tuple})\n'

def dataklass(cls):
    fields = all_hints(cls)
    nfields = len(fields)
    clsdict = vars(cls)
    if not '__init__' in clsdict: cls.__init__ = patch_args_and_attributes(make__init__(nfields), fields)
    if not '__repr__' in clsdict: cls.__repr__ = patch_attributes(make__repr__(nfields), fields, 2)
    if not '__eq__' in clsdict: cls.__eq__ = patch_attributes(make__eq__(nfields), fields, 1)
    # if not '__iter__' in clsdict:  cls.__iter__ = patch_attributes(make__iter__(nfields), fields)
    # if not '__hash__' in clsdict:  cls.__hash__ = patch_attributes(make__hash__(nfields), fields, 1)
    cls.__match_args__ = tuple(fields)
    return cls

# Example use
if __name__ == '__main__':
    @dataklass
    class Coordinates:
        x: int
        y: int


