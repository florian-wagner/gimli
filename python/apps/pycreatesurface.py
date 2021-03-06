#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from os import system

try:
    import pygimli as pg
except ImportError:
    sys.stderr.write('ERROR: cannot import the library pygimli.' +
                     'Ensure that pygimli is in your PYTHONPATH')
    sys.exit(1)


def createCoarsePoly(coarseData):
    boundary = 1250.0
    mesh = pg.Mesh()

    x = pg.x(coarseData)
    y = pg.y(coarseData)
    z = pg.z(coarseData)

    xMin, xMax = min(x), max(x)
    yMin, yMax = min(y), max(y)
    zMin, zMax = min(z), max(z)

    print(xMin, xMax, yMin, yMax)
    border = max((xMax - xMin) * boundary, (yMax - yMin) * boundary) / 100.

    n1 = mesh.createNode(xMin - border, yMin - border, zMin, 1)
    n2 = mesh.createNode(xMax + border, yMin - border, zMin, 2)
    n3 = mesh.createNode(xMax + border, yMax + border, zMin, 3)
    n4 = mesh.createNode(xMin - border, yMax + border, zMin, 4)

    mesh.createEdge(n1, n2, 12)
    mesh.createEdge(n2, n3, 23)
    mesh.createEdge(n3, n4, 34)
    mesh.createEdge(n4, n1, 41)

    for p in coarseData:
        mesh.createNode(p)

    return mesh


def createFinePoly(coarseMesh, ePos):
    paraBoundary = 10
    mesh = pg.Mesh()

    n1, n2, n3, n4 = None, None, None, None
    for n in coarseMesh.nodes():
        if n.marker() == 1:
            n1 = mesh.createNode(n.pos(), 1)
        elif n.marker() == 2:
            n2 = mesh.createNode(n.pos(), 2)
        elif n.marker() == 3:
            n3 = mesh.createNode(n.pos(), 3)
        elif n.marker() == 4:
            n4 = mesh.createNode(n.pos(), 4)

    mesh.createEdge(n1, n2, 12)
    mesh.createEdge(n2, n3, 23)
    mesh.createEdge(n3, n4, 34)
    mesh.createEdge(n4, n1, 41)

    x = pg.x(ePos)
    y = pg.y(ePos)
    z = pg.z(ePos)

    xMin, xMax = min(x), max(x)
    yMin, yMax = min(y), max(y)
    zMin, zMax = min(z), max(z)

    maxSpan = max(xMax - xMin, yMax - yMin)
    borderPara = maxSpan * paraBoundary / 100.0

    n5 = mesh.createNode(xMin - borderPara, yMin - borderPara, 0.0, 5)
    n6 = mesh.createNode(xMax + borderPara, yMin - borderPara, 0.0, 6)
    n7 = mesh.createNode(xMax + borderPara, yMax + borderPara, 0.0, 7)
    n8 = mesh.createNode(xMin - borderPara, yMax + borderPara, 0.0, 8)

    mesh.createEdge(n5, n6, 56)
    mesh.createEdge(n6, n7, 67)
    mesh.createEdge(n7, n8, 78)
    mesh.createEdge(n8, n5, 85)

    for p in ePos:
        mesh.createNode(p)

    return mesh


def main(argv):
    from optparse import OptionParser

    parser = OptionParser("usage: %prog [options] data|topo-xyz-list")
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                      help="be verbose", default=False)

    (options, args) = parser.parse_args()

    print(options, args)

    if len(args) == 0:
        parser.print_help()
        print("Please add a mesh or model name.")
        sys.exit(2)
    else:
        datafile = args[0]

    topoList = None
    try:
        data = pg.DataContainer(datafile)
        print(data)
        topoList = data.electrodePositions()
    except:
        topoList = pg.loadRVector3(datafile)

    localiseOffset = pg.RVector3(308354.26737118, 6008130.1579486, 91.23)
    for i, p in enumerate(topoList):
        topoList[i] = p - localiseOffset

    coarsePoly = createCoarsePoly(topoList)
    coarseTopoZ = pg.z(coarsePoly.positions())

    tri = pg.TriangleWrapper(coarsePoly)
    tri.setSwitches("-pzeAfaq0")
    coarseMesh = pg.Mesh()
    tri.generate(coarseMesh)

    if coarseMesh.nodeCount() == len(coarseTopoZ):
        for n in coarseMesh.nodes():
            n.pos().setZ(coarseTopoZ[n.id()]);
    else:
        print(" this should not happen. " + str( coarseMesh.nodeCount() )  +
              "/=" + str(len(coarseTopoZ)))

    coarsePoly.exportVTK('meshCoarsePoly.vtk')
    coarseMesh.exportVTK('meshCoarseMesh.vtk')

    finePoly = createFinePoly(coarseMesh, topoList)

    tri = pg.TriangleWrapper(finePoly)
    tri.setSwitches("-pzeAfaq34")
    fineMesh = pg.Mesh()
    tri.generate(fineMesh)

    finePoly.exportVTK('meshFinePoly.vtk')
    fineMesh.exportVTK('meshFineMesh.vtk')

    pg.interpolateSurface(coarseMesh, fineMesh)

    fineMesh.exportVTK('meshFine.vtk')
    fineMesh.exportAsTetgenPolyFile("meshFine.poly")
    system('closeSurface -v -z 40.0 -a 1000 -o mesh meshFine.poly')

    # system( 'polyAddVIP -f ../../para/all.vip mesh.poly')

    translate = 'polyTranslate -x ' + str(localiseOffset[0]) + \
                ' -y ' + str(localiseOffset[1]) + \
                ' -z ' + str(localiseOffset[2]) + ' mesh.poly'

    system(translate)

    #fineMesh.exportAsTetgenPolyFile( "meshFine.poly" );

if __name__ == "__main__":
    main(sys.argv[1:])
