# -*- coding: utf-8 -*-

import sys 
from xml.dom.minidom import parse
from pyproj import Proj, transform

import matplotlib.image as mpimg
from math import floor

def needOSGEO():
    try:
        from osgeo import gdal
        from osgeo.gdalconst import GA_ReadOnly
    except ImportError as e:
        print(e)
        import traceback
        traceback.print_exc(file=sys.stdout)
        sys.stderr.write("no modules osgeo\n")

gk2   = Proj( init="epsg:31466" ) # GK zone 2
gk3   = Proj( init="epsg:31467" ) # GK zone 3
gk4   = Proj( init="epsg:31468" ) # GK zone 3
wgs84 = Proj( init="epsg:4326" ) # pure ellipsoid for step-wise change

def handleWPTS( wpts ):
    """ 
        Handler for Waypoints in gpx xml-dom 
    """
    w = []

    for wpt in wpts:
        if wpt.hasAttribute('lat'):
            lat = float( wpt.getAttribute('lat') )
        else:
            continue
        if wpt.hasAttribute('lon'):
            lon = float( wpt.getAttribute('lon') )
        else:
            continue

        name = wpt.getElementsByTagName( 'name' )[0].childNodes[0].data
        time = wpt.getElementsByTagName( 'time' )[0].childNodes[0].data

        w.append( ( lon, lat, name, time)  )
    return w
#def findWPTS( ... )

def readGPX( filename ):
    """
    Extract GPS Waypoint from GPS Exchange Format (GPX).

    Currently only simple waypoint extraction is supported.
    """
    
    dom = parse( filename )
    wpts = dom.getElementsByTagName("wpt")

    return handleWPTS( wpts )
# def readGPX( ... )

def readSimpleLatLon(filename, verbose=False):
    """
        Read a list of the following formats. Try to convert the format automatically
        If you want to be sure, provide format without "d" to ensure floating point format:
            
        lon lat
        
        or
        
        marker lat lon
            
        return list:
            lon lat name time
    """
    
    def conv_(deg):
        """convert degree into floating vpoint."""
        ret = 0.0
        if 'd' in deg:
            # 10d???
            d = deg.split('d')
            ret = float(d[0])

            if "'" in d[1]:
                # 10d23'2323.44''
                m = d[1].split("'")
                if len(m) > 1:
                    ret += float(m[0]) / 60.
                    ret += float(m[1]) / 3600.
            else:
                # 10d23.2323
                ret += float( d[1] ) / 60.
        else:
            # 10.4432323
            ret = float( deg )

        return ret
    # def conv_(...):
    
    w = []
    
    with open( filename, 'r') as fi:
        content = fi.readlines( )
    fi.close()
    
    for line in content:
        if line[0] == '#': continue
        
        vals = line.split()
        
        if len( vals ) == 2:
            #lon lat
            w.append((conv_(vals[1]), conv_(vals[0]), '', 'time'))
        if len( vals ) == 3:
            # marker lat lon
            w.append((conv_(vals[2]), conv_(vals[1]), vals[0], 'time'))
                    
        if verbose:
            print(w[-1])
        
    
    return w

def GK2toUTM( R, H=None, zone=32 ):
    """ transform Gauss-Krueger zone 2 into UTM """
    """ note the double transformation (1-ellipsoid,2-projection) """
    """ default zone is 32 """

    utm = Proj( proj='utm', zone=zone, ellps='WGS84' ) # UTM 

    if H is None: # two-column matrix
        lon, lat = transform( gk2, wgs84, R[0], R[1] )
    else:
        lon, lat = transform( gk2, wgs84, R, H )
    
    return utm( lon, lat )

def GK3toUTM( R, H=None, zone=33 ):
    """ transform Gauss-Krueger zone 3 into UTM """
    """ note the double transformation (1-ellipsoid,2-projection) """
    """ default zone is 33 """

    utm = Proj( proj='utm', zone=zone, ellps='WGS84' ) # UTM 

    if H is None: # two-column matrix
        lon, lat = transform( gk3, wgs84, R[0], R[1] )
    else:
        lon, lat = transform( gk3, wgs84, R, H )
    
    return utm( lon, lat )

def GK4toUTM( R, H=None, zone=33 ):
    """ transform Gauss-Krueger zone 3 into UTM """
    """ note the double transformation (1-ellipsoid,2-projection) """
    """ default zone is 33 """

    utm = Proj( proj='utm', zone=zone, ellps='WGS84' ) # UTM 

    if H is None: # two-column matrix
        lon, lat = transform( gk4, wgs84, R[0], R[1] )
    else:
        lon, lat = transform( gk4, wgs84, R, H )
    
    return utm( lon, lat )

def GKtoUTM(R, H=None):
    """ transforms any Gauss-Krueger to UTM """
    """ autodetect GK zone from offset """
    if H is None: rr = R[0][0]
    else: rr = R[0]
    if floor( rr*1e-6 ) == 2.:
        return GK2toUTM( R, H )
    elif floor( rr*1e-6 ) == 3.:
        return GK3toUTM( R, H )
    elif floor( rr*1e-6 ) == 4.:
        return GK4toUTM( R, H )
    else:
        print("cannot detect valid GK zone")
    
def convddmm(num):
    dd = np.floor( num / 100. )
    r1 = num - dd * 100.
    return dd + r1 / 60.

def readGeoRefTIF( file_name ):
    """ 
        Read geo-referenced TIFF file and return image and bbox
        plt.imshow( im, ext = bbox.ravel() ), bbox might need transform.
    """
    dataset = gdal.Open(file_name, GA_ReadOnly)
    geotr = dataset.GetGeoTransform()
    projection = dataset.GetProjection()
    
    im = np.flipud( mpimg.imread(file_name))  
    
    tifx, tify, dx = geotr[0], geotr[3], geotr[1]
    
    bbox = [[tifx, tifx + im.shape[1] * dx],
            [tify - im.shape[0] * dx, tify]]
    
    return im, bbox, projection
 
def getBKGaddress(xlim, ylim, imsize=1000,
                  zone=32, service='dop40', uuid='', fmt='jpeg'):
    """
        Generate address for rendering web service image from BKG.
        Assumes UTM in any zone.
    """
    url='http://sg.geodatenzentrum.de/wms_' + service
    stdarg='REQUEST=GetMap&SERVICE=WMS&VERSION=1.1.0&LAYERS=0&STYLES=default&FORMAT='+fmt
    srsstr='SRS=EPSG:' + str( 25800 + zone ) # 
    
    boxstr='BBOX='+ '%d' % xlim[0] + ',' + '%d' % ylim[0] + ',' + '%d' % xlim[1] + ',' + '%d' % ylim[1]
    ysize = imsize * (ylim[1]-ylim[0]) / (xlim[1]-xlim[0])
    sizestr = 'WIDTH=' + str(imsize) + '&HEIGHT=' + '%d' % ysize
    addr = url + '__' + uuid + '?' + stdarg + '&' + srsstr + '&' + boxstr +'&' + sizestr
    
    return addr

