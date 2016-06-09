# -*- coding: utf-8 -*-

import os
from math import pi
import numpy as np
import pygimli as pg

if __name__ != "__main__":
    from . import polytools as plc


def createMesh(poly, quality=30, area=0.0,
               smooth=None, switches=None,
               regions=None, holes=None,
               verbose=False, *args, **kwargs):
    """
    Create a mesh for a given geometry polygon.

    The mesh is created by :term:`triangle` or :term:`tetgen` if the
    gimli support for these mesh generators are installed.
    The geometry needs to contain nodes and boundaries and should be valid
    in the sense that the boundaries are non intersecting.

    If poly is a list of coordinates a simple Delaunay mesh of the convex hull
    will be created.

    TODO: Tetgen support need to be implemented

    Parameters
    ----------
    poly: :gimliapi:`GIMLI::Mesh` or list
        * 2D or 3D gimli mesh that contains the PLC.
        * 2D mesh needs edges
        * 3D mesh needs ... to be implemented
        * List of x y pairs [[x0, y0], ... ,[xN, yN]]
        * PLC or list of PLC
    quality: float
        2D triangle quality sets a minimum angle constraint.
        Be careful with values above 34 degrees.
    area: float
        2D maximum triangle size in m*m
    smooth: tuple
        [smoothing algorithm, number of iterations]
        0, no smoothing
        1, node center
        2, weighted node center
    switches: str
        Force triangle to use the gives command switches.

    Returns
    -------
    mesh: :gimliapi:`GIMLI::Mesh`
    """

#    poly == [pg.Mesh, ]
    if isinstance(poly, list):
        if isinstance(poly[0], pg.Mesh):
            return createMesh(plc.mergePLC(poly),
                              quality, area, smooth, switches, verbose)
#    poly == [pos, pos, ]
    if isinstance(poly, list) or isinstance(poly, type(zip)):
        delPLC = pg.Mesh(2)
        for p in poly:
            delPLC.createNode(p[0], p[1], 0.0)
        return createMesh(delPLC, switches='-zeY')

#    poly == Mesh
    if poly.dim() == 2:
        if poly.nodeCount() == 0:
            raise Exception("No nodes in poly to create a valid mesh")

        tri = pg.TriangleWrapper(poly)

        if switches is None:
            # -D Conforming delaunay
            # -F Uses Steven Fortune's sweepline algorithm
            # no -a here ignores per region area
            switches = 'pzaeA'

            if area > 0:
                switches += 'a' + str(area)

            switches += 'q' + str(quality)

        if not verbose:
            switches += 'Q'

        if verbose:
            print(switches)
        tri.setSwitches(switches)
        mesh = tri.generate()

        if smooth is not None:
            mesh.smooth(nodeMoving=kwargs.pop('node_move', False),
                        edgeSwapping=False,
                        smoothFunction=smooth[0],
                        smoothIteration=smooth[1])
        return mesh

    else:
        raise('not yet implemented')


def refineQuad2Tri(mesh, style=1):
    """Refine mesh of quadrangles into a mesh of triangle cells.

        TODO mixed meshes

    Parameters
    ----------
    mesh : :gimliapi:`GIMLI::Mesh`
        mesh containing quadrangle cells

    style: int [1]
        * 1 bisect each quadrangle into 2 triangles
        * 2 bisect each quadrangle into 4 triangles

    Returns
    -------
    ret : :gimliapi:`GIMLI::Mesh`
        mesh containing triangle cells

    """
    out = pg.Mesh(2)
    newNode = None

    for n in mesh.nodes():
        out.createNode(n.pos())

    for c in mesh.cells():

        if style == 1:
            out.createCell([c.node(0).id(),
                            c.node(1).id(),
                            c.node(2).id()])
            out.createCell([c.node(0).id(),
                            c.node(2).id(),
                            c.node(3).id()])

        elif style == 2:
            newNode = out.createNodeWithCheck(c.center())

            for i in range(4):
                out.createCell([c.node(i).id(),
                                c.node((i+1)%4).id(),
                                newNode.id()])

        for i in range(c.boundaryCount()):
            b = c.boundary(i)
            if b.marker() != 0:
                out.createBoundary([b.node(0).id(), b.node(1).id()], b.marker())

    out.createNeighbourInfos()

    return out

def readGmsh(fname, verbose=False):
    """
    Read :term:`Gmsh` ASCII file and return instance of GIMLI::Mesh class.

    Parameters
    ----------
    fname : string
        Filename of the file to read (\\*.msh). The file must conform
        to the `MSH ASCII file version 2 <http://geuz.org/gmsh/doc/
        texinfo/gmsh.html#MSH-ASCII-file-format>`_ format.
    verbose : boolean, optional
        Be verbose during import.

    Notes
    -----
    Physical groups specified in Gmsh are interpreted as follows:

    - Points with the physical number 99 are interpreted as sensors.
    - Physical Lines and Surfaces define boundaries in 2D and 3D, respectively.
        - Physical Number 1: homogeneous Neumann condition
        - Physical Number 2: mixed boundary condition
        - Physical Number 3: homogeneous Dirichlet condition
        - Physical Number 4: Dirichlet condition
    - Physical Surfaces and Volumes define regions in 2D and 3D, respectively.
        - Physical Number 1: No inversion region
        - Physical Number >= 2: Inversion region

    Examples
    --------
    >>> import tempfile, os
    >>> from pygimli.meshtools import readGmsh
    >>> gmsh = '''
    ... $MeshFormat
    ... 2.2 0 8
    ... $EndMeshFormat
    ... $Nodes
    ... 3
    ... 1 0 0 0
    ... 2 0 1 0
    ... 3 1 1 0
    ... $EndNodes
    ... $Elements
    ... 7
    ... 1 15 2 0 1 1
    ... 2 15 2 0 2 2
    ... 3 15 2 0 3 3
    ... 4 1 2 0 1 2 3
    ... 5 1 2 0 2 3 1
    ... 6 1 2 0 3 1 2
    ... 7 2 2 0 5 1 2 3
    ... $EndElements
    ... '''
    >>> fname = tempfile.mktemp()
    >>> with open(fname, "w") as f:
    ...     f.writelines(gmsh)
    >>> mesh = readGmsh(fname)
    >>> print(mesh)
    Mesh: Nodes: 3 Cells: 1 Boundaries: 3
    >>> os.remove(fname)
    """
    inNodes, inElements, ncount = 0, 0, 0
    fid = open(fname)
    if verbose:
        print('Reading %s... \n' % fname)

    for line in fid:

        if line[0] == '$':
            if line.find('Nodes') > 0:
                inNodes = 1
            if line.find('EndNodes') > 0:
                inNodes = 0
            if line.find('Elements') > 0:
                inElements = 1
            if line.find('EndElements') > 0:
                inElements = 0

        else:
            if inNodes == 1:
                if len(line.split()) == 1:
                    nodes = np.zeros((int(line), 3))
                    if verbose:
                        print('  Nodes: %s' % int(line))
                else:
                    nodes[ncount, :] = np.array(line.split(), 'float')[1:]
                    ncount += 1

            elif inElements == 1:
                if len(line.split()) == 1:
                    if verbose:
                        print('  Entries: %s' % int(line))
                    points, lines, triangles, tets = [], [], [], []

                else:
                    entry = list(map(int, line.split()))[1:]

                    if entry[0] == 15:
                        points.append((entry[-2], entry[-3]))
                    elif entry[0] == 1:
                        lines.append((entry[-2], entry[-1], entry[2]))
                    elif entry[0] == 2:
                        triangles.append((entry[-3], entry[-2],
                                          entry[-1], entry[2]))
                    elif entry[0] == 4:
                        tets.append((entry[-4], entry[-3], entry[-2],
                                     entry[-1], entry[2]))
    fid.close()

    lines = np.asarray(lines)
    triangles = np.asarray(triangles)
    tets = np.asarray(tets)

    if verbose:
        print('    Points: %s' % len(points))
        print('    Lines: %s' % len(lines))
        print('    Triangles: %s' % len(triangles))
        print('    Tetrahedra: %s \n' % len(tets))
        print('Creating mesh object... \n')

    # check dimension
    if len(tets) == 0:
        dim, bounds, cells = 2, lines, triangles
        zero_dim = np.abs(nodes.sum(0)).argmin()  # identify zero dimension
    else:
        dim, bounds, cells = 3, triangles, tets
    if verbose:
        print('  Dimension: %s-D' % dim)

    # creating instance of GIMLI::Mesh class
    mesh = pg.Mesh(dim)

    # replacing boundary markers (gmsh does not allow negative phys. regions)
    bound_marker = (pg.MARKER_BOUND_HOMOGEN_NEUMANN, pg.MARKER_BOUND_MIXED,
                    pg.MARKER_BOUND_HOMOGEN_DIRICHLET,
                    pg.MARKER_BOUND_DIRICHLET)

    if len(bounds) == 0:
        for i in range(4):
            bounds[:, dim][bounds[:, dim] == i + 1] = bound_marker[i]

        # account for CEM markers
        bounds[:, dim][bounds[:, dim] >= 10000] *= -1

        if verbose:
            bound_types = np.unique(bounds[:, dim])
            print('  Boundary types: %s ' % len(bound_types) +
                str(tuple(bound_types)))
    else:
        if verbose:
            print("WARNING: No boundary conditions found.")

    if verbose:
        regions = np.unique(cells[:, dim + 1])
        print('  Regions: %s ' % len(regions) + str(tuple(regions)))

    for node in nodes:
        if dim == 2:
            mesh.createNode(node[0], node[3 - zero_dim], 0)
        else:
            mesh.createNode(node)

    for cell in cells:
        if dim == 2:
            mesh.createTriangle(
                mesh.node(int(cell[0] - 1)), mesh.node(int(cell[1] - 1)),
                mesh.node(int(cell[2] - 1)), marker=int(cell[3]))
        else:
            mesh.createTetrahedron(
                mesh.node(int(cell[0] - 1)), mesh.node(int(cell[1] - 1)),
                mesh.node(int(cell[2] - 1)), mesh.node(
                    int(cell[3] - 1)),
                marker=int(cell[4]))

    mesh.createNeighbourInfos()

    for bound in bounds:
        if dim == 2:
            mesh.createEdge(
                mesh.node(int(bound[0] - 1)),
                mesh.node(int(bound[1] - 1)),
                marker=int(bound[2]))
        else:
            mesh.createTriangleFace(
                mesh.node(int(bound[0] - 1)), mesh.node(int(bound[1] - 1)),
                mesh.node(int(bound[2] - 1)), marker=int(bound[3]))

    # assign marker to corresponding nodes (sensors, reference nodes, etc.)
    if len(points) > 0:
        for point in points:
            mesh.node(point[0] - 1).setMarker(-point[1])

    if verbose:
        if len(points) > 0:
            points = np.asarray(points)
            node_types = np.unique(points[:, 1])
            print('  Marked nodes: %s ' % len(points) + str(tuple(node_types)))
        print('\nDone. \n')
        print('  ' + str(mesh))

    return mesh


def readTriangle(fname, verbose=False):
    """
    Read :term:`Triangle` :cite:`Shewchuk96b` mesh.

    Read :term:`Triangle` :cite:`Shewchuk96b` ASCII mesh files and return an
    instance of GIMLI::Mesh class.
    See: ://www.cs.cmu.edu/~quake/triangle.html

    Parameters
    ----------
    fname : string
        Filename of the file to read (\\*.n, \\*.e)

    verbose : boolean, optional
        Be verbose during import.

    """

    raise("implement me!")
    os.system('meshconvert -d2 ' + fname)
    return pg.Mesh(2)


def readTetgen(fname, verbose=False):
    """
    Read :term:`Tetgen` :cite:`Si2004` mesh.

    Read :term:`Tetgen` :cite:`Si2004` ASCII files and return instance
    of GIMLI::Mesh class.
    See: http://tetgen.org/

    Parameters
    ----------
    fname : string
        Filename of the file to read (\\*.n, \\*.e \\*.f)

    verbose : boolean, optional
        Be verbose during import.

    """
    raise("implement me!")
    os.system('meshconvert -d3 -D ..' + fname)
    return pg.Mesh(3)


def readHydrus2dMesh(fname='MESHTRIA.TXT'):
    """
    Import mesh from Hydrus2D.

    Parameters
    ----------
    fname : str, optional
        Filename of Hydrus output file.

    See Also
    --------
    readHydrus3dMesh : Similar routine for three-dimensional meshes.

    References
    ----------
    .. [1] http://www.pc-progress.com/en/Default.aspx?h3d-description
    """
    fid = open(fname)
    line = fid.readline().split()
    nnodes = int(line[1])
    ncells = int(line[3])
    mesh = pg.Mesh()
    for i in range(nnodes):
        line = fid.readline().split()
        mesh.createNode(
            pg.RVector3(float(line[1]) / 100., float(line[2]) / 100., 0.))

    for i in range(3):
        line = fid.readline()

    for i in range(ncells):
        line = fid.readline().split()
        if len(line) == 4:
            mesh.createTriangle(
                mesh.node(int(line[1]) - 1),
                mesh.node(int(line[2]) - 1),
                mesh.node(int(line[3]) - 1),
                1)
        elif len(line) == 5:
            mesh.createTetrahedron(
                mesh.node(int(line[1]) - 1), mesh.node(int(line[2]) - 1),
                mesh.node(int(line[3]) - 1), mesh.node(int(line[4]) - 1), 1)

    fid.close()
    mesh.createNeighbourInfos()
    return mesh


def readHydrus3dMesh(filename='MESHTRIA.TXT'):
    """
    Import mesh from Hydrus3D.

    Parameters
    ----------
    fname : str, optional
        Filename of Hydrus output file.

    See Also
    --------
    readHydrus2dMesh : Similar routine for two-dimensional meshes.

    References
    ----------
    .. [1] http://www.pc-progress.com/en/Default.aspx?h3d-description
    """
    f = open(filename, 'r')
    for i in range(6):
        line1 = f.readline()

    nnodes = int(line1.split()[0])
    ncells = int(line1.split()[1])
    print(nnodes, ncells)
    line1 = f.readline()
    nodes = []
    dx = 0.01
    mesh = pg.Mesh()
    for ni in range(nnodes):
        pos = f.readline().split()
        p = pg.RVector3(
            float(pos[1]) * dx,
            float(pos[2]) * dx,
            float(pos[3]) * dx * (-1.))
        n = mesh.createNode(p)
        nodes.append(n)

    line1 = f.readline()
    line1 = f.readline()
    cells = []
    for ci in range(ncells):
        pos = f.readline().split()
        i, j, k, l = int(pos[1]), int(pos[2]), int(pos[3]), int(pos[4]),
        c = mesh.createTetrahedron(
            nodes[i - 1],
            nodes[j - 1],
            nodes[k - 1],
            nodes[l - 1])
        cells.append(c)

    f.close()
    mesh.createNeighbourInfos()
    return mesh


def readGambitNeutral(filename, verbose=False):
    """
    Import Gambit Neutral meshes *.neu

    See. https://www.sharcnet.ca/Software/Gambit/html/users_guide/ug01.htm

    Not fully implemented. If needed, we can improve this importer just send us
    an example file.

    Parameters
    ----------
    fname : string
        Filename of the file to read (\\*.n, \\*.e \\*.f)

    verbose : boolean, optional
        Be verbose during import.

    """
    with open(filename, 'r') as fi:
        content = fi.readlines()
    fi.close()

    mesh = pg.Mesh(2)

    for i, line in enumerate(content):
        if 'ENDOFSECTION' in line: break

    try:
        nVerts = int(content[i-1].split()[0])
        nElements = int(content[i-1].split()[1])
    except:
        raise BaseException("Cannot interpret GAMBIT Neutral header: " + content[0:i])

    for i, line in enumerate(content):
        if 'NODAL COORDINATES' in line: break
    for j in range(nVerts):
        vertx = float(content[i+j+1].split()[1])
        verty = float(content[i+j+1].split()[2])
        mesh.createNode((vertx, verty))

    for i, line in enumerate(content):
        if 'ELEMENTS/CELLS' in line: break
    for j in range(nElements):
        nNodes = int(content[i+j+1].split()[1])
        nodes = []
        for k in range(nNodes):
            nodes.append(int(content[i+1+j].split()[3 + k])-1)
        mesh.createCell(nodes)

    if verbose:
        print("Gambit neutral file imported: ", mesh)

    mesh.createNeighbourInfos()
    return mesh


def transform2DMeshTo3D(mesh, x, y, z=None):
    """
    Transform a 2D mesh into 3D coordinates using a point list (e.g. from GPS)

    Parameters
    ----------
    mesh: :gimliapi:`GIMLI::Mesh`

    x,y: [float]
        array of x/y positions along 2d profile

    z: [float]
        optional height to add (topographical correction on top of flat earth)

    See Also
    --------

    References
    ----------
    """

    # get mesh node positions
    mt, mz = pg.x(mesh.positions()), pg.y(mesh.positions())  # mesh tape and z
    # compute length of reference points along tape
    pt = np.hstack((0., np.cumsum(np.sqrt(np.diff(x)**2 + np.diff(y)**2))))
    #  interpolate node positions from tape to x/y using tape positions
    mx = np.interp(mt, pt, x)
    my = np.interp(mt, pt, y)
    # compute z offset by interpolating z
    if z is None:
        oz = np.zeros(len(mt))
    else:
        oz = np.interp(mt, pt, z)

    # set the positions in the mesh
    for i, node in enumerate(mesh.nodes()):
        node.setPos(pg.RVector3(mx[i], my[i], mz[i] + oz[i]))


def rot2DGridToWorld(mesh, start, end):
    """
    ..

    todo:: Complete Documentation. ...rotate a given 2D grid in...
    """
    mesh.rotate(pg.degToRad(pg.RVector3(-90.0, 0.0, 0.0)))

    src = pg.RVector3(0.0, 0.0, 0.0).norm(pg.RVector3(0.0, 0.0, -10.0),
                                          pg.RVector3(10.0, 0.0, -10.0))
    dest = start.norm(start - pg.RVector3(0.0, 0.0, 10.0), end)

    q = pg.getRotation(src, dest)
    rot = pg.RMatrix(4, 4)
    q.rotMatrix(rot)
    mesh.transform(rot)
    mesh.translate(start)


def merge2Meshes(m1, m2):
    """Merge two meshes into one new mesh and return combined mesh."""

    mesh = pg.Mesh(m1)

    for c in m2.cells():
        mesh.copyCell(c)

    for b in m2.boundaries():
        mesh.copyBoundary(b)

    for key in list(mesh.exportDataMap().keys()):
        d = mesh.exportDataMap()[key]
        d.resize(mesh.cellCount())
        d.setVal(m1.exportDataMap()[key], 0, m1.cellCount())
        d.setVal(
            m2.exportDataMap()[key],
            m1.cellCount(),
            m1.cellCount() + m2.cellCount())
        mesh.addExportData(key, d)

    return mesh


def mergeMeshes(meshlist):
    """
    Merge several meshes into one new mesh and return the new mesh.

    Parameters
    ----------
    meshlist : list
        List of at least two meshes to be merged.

    See Also
    --------
    merge2Meshes
    """

    if not isinstance(meshlist, list):
        raise "argument meshlist is no list"

    if len(meshlist) < 2:
        raise "to few meshes in meshlist"

    mesh = meshlist[0]

    for m in range(1, len(meshlist)):
        mesh = merge2Meshes(mesh, meshlist[m])

    return mesh


def createParaDomain2D(*args, **kwargs):
    """
        API change here .. use createParaMeshPLC instead
    """
    print("createParaDomain2D: API change: use createParaMeshPLC instead")
    return createParaMeshPLC(*args, **kwargs)


def createParaMeshPLC(sensors, paraDX=1, paraDepth=0,
                      paraBoundary=2, paraMaxCellSize=0, boundary=-1,
                      boundaryMaxCellSize=0,
                      verbose=False, *args, **kwargs):
    """
    Create a PLC mesh for an inversion parameter mesh.

    Create a PLC mesh for an inversion parameter mesh for a given list of
    sensor positions.
    Sensor position assumed on the surface and must be sorted and unique.

    The PLC is a :gimliapi:`GIMLI::Mesh` and contain nodes, edges and
    two region markers, one for the parameters domain (marker=2) and
    a larger boundary around the outside (marker=1)

    TODO:

        * closed domains (boundary == 0)
        * additional topopoints
        * spline interpolations between sensorpoints or addpoints
        * subsurface sensors

    Parameters
    ----------
    sensors : list of RVector3 objects | DataContainer with sensorPositions()
        Sensor positions. Must be sorted and unique in positive x direction.
        Depth need to be y-coordinate.
    paraDX : float [1]
        Relativ distance for refinement nodes between two electrodes (1=none),
        e.g., 0.5 means 1 additional node between two neighboring electrodes
        e.g., 0.33 means 2 additional equidistant nodes between two electrodes
    paraDepth : float, optional
        Maximum depth for parametric domain, 0 (default) means 0.4 * maximum
        sensor range.
    paraBoundary : float, optional
        Margin for parameter domain in absolute sensor distances. 2 (default).
    paraMaxCellSize: double, optional
        Maximum size for parametric size in m*m
    boundaryMaxCellSize: double, optional
        Maximum cells size in the boundary region in m*m
    boundary : float, optional
        Boundary width to be appended for domain prolongation in absolute
        para domain width.
        Values lover 0 force the boundary to be 4 times para domain width.

    Returns
    -------
    poly: :gimliapi:`GIMLI::Mesh`
        piecewise linear complex (PLC) containing nodes and edges
    """

    if hasattr(sensors, 'sensorPositions'):  # obviously a DataContainer type
        sensors = sensors.sensorPositions()
    elif type(sensors) == np.ndarray:
        sensors = [pg.RVector3(s) for s in sensors]


    eSpacing = kwargs.pop('eSpacing', sensors[0].distance(sensors[1]))

    iz = 1
    xmin, ymin, zmin = sensors[0][0], sensors[0][1], sensors[0][2]
    xmax, ymax, zmax = xmin, ymin, zmin
    for e in sensors:
        xmin = min(xmin, e[0])
        xmax = max(xmax, e[0])
        ymin = min(ymin, e[1])
        ymax = max(ymax, e[1])
        zmin = min(zmin, e[2])
        zmax = max(zmax, e[2])

    if abs(ymin) < 1e-8 and abs(ymax) < 1e-8:
        iz = 2

    paraBound = eSpacing * paraBoundary

    if paraDepth == 0:
        paraDepth = 0.4 * (xmax - xmin)

    poly = pg.Mesh(2)
    # define para domain without surface
    n1 = poly.createNode([xmin - paraBoundary, sensors[0][iz]])
    n2 = poly.createNode([xmin - paraBoundary, sensors[0][iz] - paraDepth])
    n3 = poly.createNode([xmax + paraBoundary, sensors[-1][iz] - paraDepth])
    n4 = poly.createNode([xmax + paraBoundary, sensors[-1][iz]])

    if boundary < 0:
        boundary = 4

    bound = abs(xmax - xmin) * boundary
    if bound > paraBound:
        # define world without surface
        n11 = poly.createNode(n1.pos() - [bound, 0.])
        n12 = poly.createNode(n11.pos() - [0., bound + paraDepth])
        n14 = poly.createNode(n4.pos() + [bound, 0.])
        n13 = poly.createNode(n14.pos() - [0., bound + paraDepth])

        poly.createEdge(n1, n11, pg.MARKER_BOUND_HOMOGEN_NEUMANN)
        poly.createEdge(n11, n12, pg.MARKER_BOUND_MIXED)
        poly.createEdge(n12, n13, pg.MARKER_BOUND_MIXED)
        poly.createEdge(n13, n14, pg.MARKER_BOUND_MIXED)
        poly.createEdge(n14, n4, pg.MARKER_BOUND_HOMOGEN_NEUMANN)
        poly.addRegionMarker(n12.pos() + [1e-3, 1e-3], 1, boundaryMaxCellSize)

    poly.createEdge(n1, n2, 1)
    poly.createEdge(n2, n3, 1)
    poly.createEdge(n3, n4, 1)
    poly.addRegionMarker(n2.pos() + [1e-3, 1e-3], 2, paraMaxCellSize)

    # define surface
    nSurface = []
    nSurface.append(n1)
    for i, e in enumerate(sensors):
        if iz == 2:
            e.rotateX(-pi/2)
        if paraDX >= 0.5:
            nSurface.append(poly.createNode(e, pg.MARKER_NODE_SENSOR))
            if (i < len(sensors) - 1):
                e1 = sensors[i + 1]
                if iz == 2:
                    e1.rotateX(-pi/2)
                nSurface.append(poly.createNode((e + e1) * 0.5))
            # print("Surface add ", e, el, nSurface[-2].pos(),
            #        nSurface[-1].pos())
        elif paraDX < 0.5:
            if (i > 0):
                e1 = sensors[i - 1]
                if iz == 2:
                    e1.rotateX(-pi/2)
                nSurface.append(
                    poly.createNode(e - (e - e1) * paraDX))
            nSurface.append(poly.createNode(e, pg.MARKER_NODE_SENSOR))
            if (i < len(sensors) - 1):
                e1 = sensors[i + 1]
                if iz == 2:
                    e1.rotateX(-pi/2)
                nSurface.append(
                    poly.createNode(e + (e1 - e) * paraDX))
            # print("Surface add ", nSurface[-3].pos(), nSurface[-2].pos(),
            #        nSurface[-1].pos())
    nSurface.append(n4)

    for i in range(len(nSurface) - 1, 0, -1):
        poly.createEdge(nSurface[i], nSurface[i - 1],
                        pg.MARKER_BOUND_HOMOGEN_NEUMANN)

#     for n in poly.nodes():
#        print(n.pos())
#    sys.exit()
    return poly


def createParaMesh(*args, **kwargs):
    """
    create parameter mesh from list of sensor positions

    Parameters
    ----------
    sensors : list of RVector3 objects
        Sensor positions. Must be sorted and unique in positive x direction.
        Depth need to be y-coordinate.
    paraDX : float
        Relativ distance for refinement nodes between two electrodes (1=none),
        e.g., 0.5 means 1 additional node between two neighboring electrodes
        e.g., 0.33 means 2 additional equidistant nodes between two electrodes
    paraDepth : float, optional
        Maximum depth for parametric domain, 0 (default) means 0.4 * maximum
        sensor range.
    paraBoundary : float, optional
        Margin for parameter domain in absolute sensor distances. 2 (default).
    paraMaxCellSize: double, optional
        Maximum size for parametric size in m*m
    boundaryMaxCellSize: double, optional
        Maximum cells size in the boundary region in m*m
    boundary : float, optional
        Boundary width to be appended for domain prolongation in absolute
        para domain width.
        Values lover 0 force the boundary to be 4 times para domain width.

    Returns
    -------
    poly: :gimliapi:`GIMLI::Mesh`

    """
    plc = createParaMeshPLC(*args, **kwargs)
    kwargs.pop('paraMaxCellSize', 0)
    kwargs.pop('boundaryMaxCellSize', 0)
    mesh = createMesh(plc, **kwargs)
    return mesh


def createParaMesh2dGrid(*args, **kwargs):
    """
        API change here .. use createParaMesh2DGrid instead
    """
    print("createParaMesh2dGrid: API change: pls use createParaMesh2DGrid")
    return createParaMesh2DGrid(*args, **kwargs)


def createParaMesh2DGrid(sensors, paraDX=1, paraDZ=1, paraDepth=0, nLayers=11,
                         boundary=-1, paraBoundary=2, verbose=False, *args,
                         **kwargs):
    """
    Create a grid style mesh for an inversion parameter mesh.

    Return parameter grid for a given list of sensor positions.

    Parameters
    ----------
    sensors : list of RVector3 objects or data container with sensorPositions
        Sensor positions. Must be sorted in positive x direction
    paraDX : float, optional
        Horizontal distance between sensors, relative regarding sensor
        distance. Value must be greater than 0 otherwise 1 is assumed.
    paraDZ : float, optional
        Vertical distance to the first depth layer, relative regarding sensor
        distance. Value must be greater than 0 otherwise 1 is assumed.
    paraDepth : float, optional
        Maximum depth for parametric domain, 0 (default) means 0.4 * maximum
        sensor range.
    nLayers : int, optional [11]
        Number of depth layers.
    boundary : int, optional [-1]
        Boundary width to be appended for domain prolongation in absolute
        para domain width.
        Values lower than 0 force the boundary to be 4 times para domain width.
    paraBoundary : int, optional [2]
        Offset to the parameter domain boundary in absolute sensor spacing.
    verbose : boolean, optional
        Be verbose.

    Returns
    -------
    mesh: :gimliapi:`GIMLI::Mesh`

    Examples
    --------
    >>> import pygimli as pg
    >>> import matplotlib.pyplot as plt
    >>>
    >>> from pygimli.meshtools import createParaMesh2DGrid
    >>> mesh = createParaMesh2DGrid(sensors=pg.RVector(range(10)),
    ...                             boundary=1, paraDX=1,
    ...                             paraDZ=1, paraDepth=5)
    >>> ax, _ = pg.show(mesh, mesh.cellMarkers(), alpha=0.3, tri=True)
    >>> ax, _ = pg.show(mesh, axes=ax)
    >>> plt.show()
    """

    mesh = pg.Mesh(2)

    # maybe separate x y z and sort
    if isinstance(sensors, np.ndarray) or isinstance(sensors, pg.RVector):
        sensors = [pg.RVector3(s, 0) for s in sensors]

    sensorX = pg.x(sensors)

    eSpacing = abs(sensorX[1] - sensorX[0])

    xmin = min(sensorX) - paraBoundary * eSpacing
    xmax = max(sensorX) + paraBoundary * eSpacing

    if paraDX == 0:
        paraDX = 1.
    if paraDZ == 0:
        paraDZ = 1.

    dx = eSpacing * paraDX
    dz = eSpacing * paraDZ

    if paraDepth == 0:
        paraDepth = 0.4 * (xmax - xmin)

    x = pg.utils.grange(xmin, xmax, dx=dx)

    y = -pg.increasingRange(dz, paraDepth, nLayers)

    mesh.createGrid(x, y)

    list(map(lambda cell: cell.setMarker(2), mesh.cells()))

    paraXLimits = [xmin, xmax]
#    paraYLimits = [min(y), max(y)]  # not used

    if boundary < 0:
        boundary = abs((paraXLimits[1] - paraXLimits[0]) * 4.0)

    mesh = pg.meshtools.appendTriangleBoundary(mesh,
                                               xbound=boundary,
                                               ybound=boundary,
                                               marker=1, *args, **kwargs)

    return mesh

if __name__ == "__main__":
    pass
