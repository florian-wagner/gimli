#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""    
    For the manager look at BERT https://gitlab.com/resistivity-net/bert
    
"""

import pygimli as pg
import numpy as np

def resistivityArchie(rFluid, porosity, a=1.0, m=2.0, S=1.0, n=2.0,
                      mesh=None, meshI=None, fill=None):
    r"""
    Return resistivity of rock for the petrophysical model from Archies law.
    
    .. math:: 
        \rho = a\rho_{\text{fl}}\phi^{-m}\S^{-n}
        
    * :math:`\rho` - the electrical resistivity of the fluid saturated rock in :math:`\Omega\text{m}`
    * :math:`\rho_{\text{fl}}` - rFluid: electrical resistivity of the fluid in :math:`\Omega\text{m}`
    * :math:`\phi` - porosity 0.0 --1.0
    * :math:`S`    - fluid saturation 0.0 --1.0
    * :math:`a` - Tortuosity factor. (common 1)
    * :math:`m` - Cementation exponent of the rock (usually in the range 1.3 -- 2.5 for sandstones)
    * :math:`n` - is the saturation exponent (usually close to 2)
     
    If mesh is not None the resulting values are calculated for each cell of 
    the mesh. 
    All parameter can be scalar, array of length mesh.cellCount() 
    or callable(pg.cell). If rFluid is non-steady n-step distribution 
    than rFluid can be a matrix of size(n, mesh.cellCount())
    If meshI is not None the result is interpolated to meshI.cellCenters() 
    and prolonged (if fill ==1).
    
    Note
    ----
    We experience some unstable nonlinear behavior.
    Until this is clarified all results are rounded to the precision 1e-6.
     
    Examples
    --------
    
    WRITEME
     
     
    """
    phi = porosity
    if type(porosity) is list:
        phi = np.array(porosity)
    
    if mesh == None:
        return rFluid * a * phi**(-m) * S**(-n)
    
    rB = None
    
    if type(rFluid) == float:
        rB = pg.RMatrix(1, mesh.cellCount())
        rB[0] = pg.solver.parseArgToArray(rFluid, mesh.cellCount(), mesh)
        
    elif rFluid.ndim == 1:
        rB = pg.RMatrix(1, len(rFluid))
        rB[0] = pg.solver.parseArgToArray(rFluid, mesh.cellCount(), mesh)
        
    elif rFluid.ndim == 2:
        rB = pg.RMatrix(len(rFluid), len(rFluid[0]))
        for i in range(len(rFluid)):
            rB[i] = rFluid[i]
     
    phi = pg.solver.parseArgToArray(phi, mesh.cellCount(), mesh)
    a = pg.solver.parseArgToArray(a, mesh.cellCount(), mesh)
    m = pg.solver.parseArgToArray(m, mesh.cellCount(), mesh)
    S = pg.solver.parseArgToArray(S, mesh.cellCount(), mesh)
    n = pg.solver.parseArgToArray(n, mesh.cellCount(), mesh)
    
    r = pg.RMatrix(len(rB), len(rB[0]))
    for i in range(len(r)):
        r[i] = rB[i] * a * phi**(-m) * S**(-n)
        
    r.round(1e-6)
    #print('rc:', min(np.array(r).flatten()), max(np.array(r).flatten()), np.mean(np.array(r).flatten()))        
    if meshI == None:
        if len(r) == 1:
            return r[0].copy()
        return r
    
    rI = pg.RMatrix(len(r), meshI.cellCount())
    if meshI:
        pg.interpolate(mesh, r, meshI.cellCenters(), rI) 
        
    #print('rd0:', min(np.array(rI).flatten()), max(np.array(rI).flatten()), np.mean(np.array(rI).flatten()))        
    
    if fill:
        for i in range(len(rI)):
            # slope == True produce unstable behavior .. check!!!!!!
            
            rI[i] = pg.solver.fillEmptyToCellArray(meshI, rI[i], slope=False)
        
    #print('rd1:', min(np.array(rI).flatten()), max(np.array(rI).flatten()), np.mean(np.array(rI).flatten()))        
    rI.round(1e-6)
    
    #print('rd2:', min(np.array(rI).flatten()), max(np.array(rI).flatten()), np.mean(np.array(rI).flatten()))        
    #print(rI)
    if len(rI) == 1:
        return rI[0]
    return rI

def transFwdArchiePhi(rFluid=20, n=2): 
    r""" Transformation for 
    
    .. math:: 
        \rho & = a\rho_{\text{fl}}\phi^{-m}\S_w^{-n} \\
        \rho & = \rho_{\text{fl}}\phi^(-n) = \left(\phi/\rho_{\text{fl}}^{-1/n}\right)^{-n}

    See also :py:mod:`pygimli.physics.petro.resistivityArchie`
    
    Return
    ------
    trans : :gimliapi:`GIMLI::RTransPower`
        Transformation function
    
    Examples
    --------
    >>> from pygimli.physics.petro import *
    >>> phi = 0.3
    >>> tFAPhi = transFwdArchiePhi(rFluid=20)
    >>> r1 = tFAPhi.trans(phi)
    >>> r2 = resistivityArchie(rFluid=20.0, porosity=phi, 
    ...                        a=1.0, m=2.0, S=1.0, n=2.0)
    >>> print(r1-r2 < 1e-12)
    True
    >>> phi = [0.3]
    >>> tFAPhi = transFwdArchiePhi(rFluid=20)
    >>> r1 = tFAPhi.trans(phi)
    >>> r2 = resistivityArchie(rFluid=20.0, porosity=phi, 
    ...                        a=1.0, m=2.0, S=1.0, n=2.0)
    >>> print((r1-r2 < 1e-12)[0])
    True
    """
    return pg.RTransPower(-n, rFluid**(1./n))

def transInvArchiePhi(rFluid=20, n=2):  # phi(rho)
    """ Inverse Wyllie transformation function porosity(slowness)
    # rFluid/rho = phi^n  ==> phi = (rFluid/rho)^(1/n) = (rho/rFluid)^(-1/n)
    See
    ---
    :py:mod:`pygimli.physics.petro.transFwdArchiePhi`
    """
    
    return pg.RTransPower(-1/n, rFluid)

def transFwdArchieS(rFluid=20, phi=0.4, n=2, m=2):  # rho(S)
    """ inverse Wyllie transformation function slowness(saturation) """
    # rho = rFluid * phi^(-n) S^(-m)
    return pg.RTransPower(-m, (rFluid*phi**(-n))**(1/m))

def transInvArchieS(rFluid=20, phi=0.4, n=2, m=2):  # S(rho)
    """ inverse Wyllie transformation function slowness(saturation) """
    # rFluid/rho = phi^n S^m => S=(rFluid/rho/phi^n)^(1/m)=(rho/rFluid/phi^-n)^(-1/m)
    return pg.RTransPower(-1/m, rFluid*phi**(-n))

def test_Archie():
    dx = 0.01
    phivec = np.arange(dx, 0.5, dx)
    swvec = np.arange(dx, 1, dx)

    phi0 = 0.4  # 40% porosity
    rhow = 20  # 20 Ohmm tap water
    tIAPhi = transInvArchiePhi()
    tIAS = transInvArchieS(phi=phi0)
    tFAPhi = transFwdArchiePhi()
    tFAS = transFwdArchieS(phi=phi0)
    fig, ax = plt.subplots()
    # direct function
    ax.semilogy(phivec, Archie(rhof=rhow, phi=phivec), 'b-')
    ax.semilogy(swvec, Archie(rhof=rhow, phi=phi0, Sw=swvec), 'r-')
    # forward transformation
    ax.semilogy(phivec, tFAPhi.trans(phivec), 'bx')
    ax.semilogy(swvec, tFAS.trans(swvec), 'rx')
    # inverse transformation
    ax.semilogy(phivec, tIAPhi.invTrans(phivec), 'b+')
    ax.semilogy(swvec, tIAS.invTrans(swvec), 'r+')

if __name__ == "__main__":
    pass

