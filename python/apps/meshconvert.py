#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This program is part of pygimli
Visit http://www.resistivity.net for further information or the latest version.
"""

import sys
import os
import pygimli as pg
import numpy as np


def strToRVector3(s):
    vals = s.split(',')
    if len(vals) == 1:
        return pg.RVector3(float(vals[0]), 0.0)
    if len(vals) == 2:
        return pg.RVector3(float(vals[0]), float(vals[1]))
    if len(vals) == 3:
        return pg.RVector3(float(vals[0]), float(vals[1]), float(vals[2]))


def parseDataStr(s):
    vals = s.split(':')
    data = pg.RVector(0)

    if len(vals) > 0:
        pg.load(data, vals[0])
        if len(data) == 0:
            pg.load(data, vals[0], pg.Binary)

    if len(vals) == 1:
        return vals[0], data
    if len(vals) == 2:
        return vals[1], data
    if len(vals) == 3:
        modificator = getattr(pg, vals[2])

        if modificator == pg.log10 and min(data) <= 0.0:
            return vals[1], pg.prepExportPotentialData(pg.RVector(vals[0]))
        else:
            return vals[1], modificator(data)
    if len(vals) == 4:
        modificator = getattr(pg, vals[2])

        if modificator == pg.log10 and min(data) <= 0.0:
            return vals[1], pg.prepExportPotentialData(data, float(vals[3]))
        else:
            return vals[1], modificator(data)


def applyInterpolation(filename, mesh, verbose=False):
    '''
        needs to be moved into libgimli
        needs to be documented
    '''

    A = None
    try:
        data = pg.DataContainer(filename)
        A = np.zeros((3, data.sensorCount()))
        A[1] = pg.x(data.sensorPositions())
        A[2] = pg.y(data.sensorPositions())
        for i, p in enumerate(data.sensorPositions()):
            if i > 0:
                A[0, i] = A[0, i-1] + data.sensorPositions()[i-1].distance(p)
        if verbose:
            print(("loaded DataContainer: ", filename))
    except:
        A = np.loadtxt(filename).T
        if verbose:
            print(("loaded txtfile: ", filename))

    tn = [n.pos()[0] for n in mesh.nodes()]
    zn = [n.pos()[1] for n in mesh.nodes()]

    xn = np.interp(tn, A[0], A[1])
    yn = np.interp(tn, A[0], A[2])

    for i, n in enumerate(mesh.nodes()):
        n.setPos(pg.RVector3(xn[i], yn[i], zn[i]))

# def applyInterpolation(...)


def main(argv):
    from optparse import OptionParser

    parser = OptionParser("usage: %prog [options] mesh|mod|vtk",
                          version="%prog: " + pg.__version__)
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                      help="be verbose", default=False)
    parser.add_option("-V", "--outVTK", dest="outVTK", action="store_true",
                      help="export VTK format", default=False)
    parser.add_option("" , "--outBoundaryVTU", dest="outBoundaryVTU",
                      action="store_true", default=False,
                      help="export mesh boundary in VTU format")
    parser.add_option("-B", "--outBMS", dest="outBMS", action="store_true",
                      help="export GIMLi internal Binary Mesh (BMS) Format ",
                      default=False)
    parser.add_option("", "--outBMS2", dest="outBMS2", action="store_true",
                      help="export GIMLi internal Binary Mesh (BMS) v2 Format",
                      default=False)
    parser.add_option("-m", "--outMidCellAscii", dest="outMidCell",
                      action="store_true",
                      help="Export simple xy[z]r[i] data. xy[z] are 2d[3d] cell center coordinates. r are resistivity and i optional ip-data values. Import data with the names r and i.", default=False)
    parser.add_option("-d", "--data", dest="data", action='append',
                      help="data file with optional name or modificator. This option can appended multiple. e.g.: -d data.vector (adds the data from file data.vector)\n"+
                      "-d data.vector:Data (adds the data from file data.vector and name it Data \n"+
                      "-d data.vector:Data:Log10 (adds the data from file data.vector, name it Data and stores log10(data)\n" +
                      "-d data.vector:Data:Log10:1e-4 (adds the data from file data.vector, name it Data and stores log10(data) with droptolerancs 1e-4 for neg. data values()")

    parser.add_option("-o", "--output", dest="outFileName", metavar="File",
                      help="Filename for the resulting export. Suffix may define fileformat (.bms|.vtk)")

    parser.add_option("-r", "--rotate", dest="rotate",
                      help="rotate the mesh, "'"x,y,z"'" ")
    parser.add_option("-s", "--scale", dest="scale",
                      help="scale the mesh "'"x,y,z"'" ")
    parser.add_option("-t", "--translate", dest="translate",
                      help="translate the mesh. "'"x,y,z"'" ")

    parser.add_option("", "--interpolateCoords", dest="interpolateCoords", metavar="File",
                      help = " Interpolate a 2D mesh into 3D Coordinates." +
                      "File is a 3-column-ascii-file (dx x y)")
    parser.add_option("", "--interpolateMesh", dest="interpolateMesh", metavar="File",
                      help = " Interpolate the data of mesh into the mesh given by File." +
                      "File is a bms|mod|vtk")

    (options, args) = parser.parse_args()

    if options.verbose:
        print(options, args)

    if len(args) == 0:
        parser.print_help()
        print("Please add a mesh or model name.")
        sys.exit(2)
    else:
        meshname = args[0]

    mesh = pg.Mesh(meshname)

    if options.verbose:
        print(meshname, mesh)

    if options.interpolateCoords is not None:
        applyInterpolation(filename=options.interpolateCoords,
                           mesh=mesh,
                           verbose=options.verbose)

    if options.interpolateMesh is not None:
        imesh = pg.Mesh(options.interpolateMesh)
        pg.interpolate(mesh, imesh)
        mesh = imesh

    if options.rotate is not None:
        rot = strToRVector3(options.rotate)
        if options.verbose:
            print("rotate: ", rot)
        mesh.rotate(pg.degToRad(rot))

    if options.translate is not None:
        tra = strToRVector3(options.translate)
        if options.verbose:
            print("translate: ", tra)
        mesh.translate(tra)

    if options.scale is not None:
        sca = strToRVector3(options.scale)
        if options.verbose:
            print("scale: ", sca)
        mesh.scale(sca)

    if options.data is not None:
        for dataStr in options.data:
            data = parseDataStr(dataStr)

            if options.verbose:
                print(dataStr, data[0], data[1])

            mesh.addExportData(data[0], data[1])

    # prepare output starts here
    outfileBody = None

    if options.outFileName is not None:
        (outfileBody, fileExtension) = os.path.splitext(options.outFileName)
        if fileExtension == '.bms':
            options.outBMS = True
        elif fileExtension == '.vtk':
            options.outVTK = True
    else:
        (outfileBody, fileExtension) = os.path.splitext(meshname)

    if options.outMidCell:
        if options.verbose:
            print("write Ascii cell center: ", outfileBody)

        suff = '.xy'
        if mesh.dimension() == 3:
            suff += 'z'

        if 'r' in mesh.exportDataMap() and 'i' in mesh.exportDataMap():
            mesh.exportMidCellValue(outfileBody + suff + 'ri',
                                    mesh.exportData('r'), mesh.exportData('i'))
        elif 'r' in mesh.exportDataMap():
            mesh.exportMidCellValue(outfileBody + suff + 'r',
                                    mesh.exportData('r'))
        else:
            print("Sry!, no resistivity data with name r found")

    if options.outVTK:
        if options.verbose:
            print("write vtk: ", outfileBody + ".vtk")
        mesh.exportVTK(outfileBody)

    if options.outBoundaryVTU:
        mesh.exportBoundaryVTU(outfileBody)

    if options.outBMS:
        if options.verbose:
            print("write bms: ", outfileBody + ".vtk")
        mesh.save(outfileBody)

    if options.outBMS2:
        if options.verbose:
            print("write bms.v2: ", outfileBody + ".bms")
        mesh.saveBinaryV2(outfileBody)
        mesh.loadBinaryV2(outfileBody)
        print(mesh)


if __name__ == "__main__":
    main(sys.argv[1:])
