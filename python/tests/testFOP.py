#!/usr/bin/env python

import pygimli as pg

ab2 = pg.RVector(2, 1.0)
ab2[1]=2.0
mn2 = pg.RVector(2, 3.0)
mn2[1]=4.0

nlay = 2 
model = pg.RVector( 3, 10. )

F = pg.DC1dModelling( nlay, ab2, mn2 )

print F.response( model )