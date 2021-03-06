#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygimli as pg

from math import sqrt, floor, ceil

def trimDocString(docstring):
    """
        Handling Docstring Indentation.
        From: https://www.python.org/dev/peps/pep-0257/
    """
    if not docstring:
        return ''
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = 2**16-1
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < 2**16-1:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return '\n'.join(trimmed)

def unicodeToAscii(text):
    if type(text) == str:
        return text.encode("iso-8859-1", "ignore")
    else:
        return text

def logDropTol(p, droptol = 1e-3):
    """"""
    tmp = pg.RVector(p);

    tmp = pg.abs(tmp / droptol)
    tmp.setVal(1.0, pg.find(tmp < 1.0))

    #for i, v in enumerate(tmp):
        #tmp[ i ] = abs(tmp[ i ] / droptol);
        #if tmp[ i ] < 1.0: tmp[ i ] = 1.0;

    tmp = pg.log10(tmp);
    tmp *= pg.sign(p);
    return tmp;
# def logDropTol

def grange(start, end, dx=0, n=0, log=False, verbose=False):
    """
        Create either an array from start step-wise filled with dx until end reached [start, end] (like np.array with defined end)\\n
        or an array that is filled from start to end with n steps. [start, end] (like np.linespace) \\n
        or an array with with logarithmic spacing if n is given, dx will be ignored.        
    
    Parameters
    ----------
    start: float
        First value of the resulting array
    end: float
        Last value of the resulting array
    dx: float
        Linear step length, n will be ignored
    n: int
        Amount of steps
    log: bool
    
    Returns
    -------
    ret: :gimliapi:`GIMLI::RVector`
        Return resulting array
    """
    
    s = float(start)
    e = float(end)
    d = float(dx)

    if dx != 0:
        if end < start and dx > 0:
            #print("grange: decreasing range but increasing dx, swap dx sign")
            d = -d
        if end > start and dx < 0:
            #print("grange: increasing range but decreasing dx, swap dx sign")
            d = -d
        ret = pg.RVector(range(int(floor(abs((e - s) / d)) + 1)))
        ret *= d
        ret += s
        return ret

    elif n > 0:
        if not log:
            return grange(start, end, dx = (e - s) / (n - 1))
        else:
            raise Exception('not yet implemented.')

    else:
        raise Exception('Either dx or nSteps have to be given.')

def diff(v):
    '''
        Return RVector as approximate derivative from v as r[v_1-v_0, v2-v_1,...]
    '''
    r = pg.RVector(len(v) -1)
    for i in range(len(r)):
        r[ i ] = v[ i + 1 ] - v[ i ]
    return r

def xyToLength(x, y):
    """return RVector of lengths from two RVectors x and y starting from 0 to
    end."""
    ret = pg.RVector(len(x), 0.0)

    for i in range(len(ret) -1):
        dx = x[ i + 1] - x[ i ]
        dy = y[ i + 1] - y[ i ]

        ret[ i + 1 ] = ret[ i ] + sqrt(dx * dx + dy * dy)
        #ret[ i + 1 ] = ret[ i ] + abs(l[ i + 1 ] - l[ i ])

    return ret

def getIndex(seq, f):
    #DEPRECATED_SLOW
    idx = [ ]
    if isinstance(seq, pg.RVector):
        for i in range(len (seq)):
            v = seq[ i ]
            if f(v): idx.append(i)
    else:
        for i, d in enumerate(seq):
            if f(d): idx.append(i)
    return idx

def filterIndex(seq, idx):
    if isinstance(seq, pg.RVector):
        #return seq(idx)
        ret = pg.RVector(len(idx))
    else:
        ret = list(range(len(idx)))

    for i, id in enumerate(idx):
        ret[ i ] = seq[ id ]
    return ret

def findNearest(x, y, xp, yp, radius = -1):
    idx = 0
    minDist = 1e9
    startPointDist = pg.RVector(len(x))
    for i in range(len(x)):
        startPointDist[ i ] = sqrt((x[ i ] - xp) * (x[ i ] - xp) + (y[ i ] - yp) * (y[ i ] - yp))

        if startPointDist[ i ] < minDist and startPointDist[ i ] > radius:
            minDist = startPointDist[ i ]
            idx = i
    return idx, startPointDist[ idx ]



def unique_everseen(iterable, key=None):
    """
    List unique elements, preserving order.

    Remember all elements ever seen.
    http://docs.python.org/library/itertools.html#recipes
    """
    # unique_everseen('AAAABBBCCDAABBB') --> A B C D
    # unique_everseen('ABBCcAD', str.lower) --> A B C D
    try:
        from itertools import ifilterfalse
    except:
        from itertools import filterfalse

    seen = set()
    seen_add = seen.add
    if key is None:
        try:
            for element in ifilterfalse(seen.__contains__, iterable):
                seen_add(element)
                yield element
        except:
            for element in filterfalse(seen.__contains__, iterable):
                seen_add(element)
                yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element

def unique(a):
    return list(unique_everseen(a))

