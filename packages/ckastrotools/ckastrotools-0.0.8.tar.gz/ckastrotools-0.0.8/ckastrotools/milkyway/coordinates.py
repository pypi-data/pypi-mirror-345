"""Module for coordinate operations in the Milky Way."""

import numpy as np

def _residual_brand(R_gal, vlsr, glon, glat=0., R_0=8.34, t_0=240.):
    '''
    Calculate residual for Brand & Blitz (1993) rotation curve, using parameters from
    Reid 2014.

    @param r: Galactocentric radius [kpc]
    @type r: float
    @param vlsr: Line of sight velocity with respect to local standard of rest [km s^-1]
    @type vlsr: float
    @param glon: Galactic longitude [deg]
    @type glon: float
    @param glat: (optional; default glat=0) Galactic latitude [deg]
    @type glat: float
    @param R_0: (optional; default R_0=8.34) Distance to Galactic center [kpc]
    @type R_0: float
    @param t_0: (optional; default Theta_0=248.) Circular rotation velocity at orbit of
                the sun [km s^-1]
    @type t_0: float
    @return: Residual between the actual vlsr and the expected from the rotation curve
    @rtype: float

    '''
    a1 = 1.00767
    a2 = 0.0394
    a3 = 0.00712
    a = vlsr
    c = np.sin(glon * np.pi / 180.) * np.cos(glat * np.pi / 180.) * t_0 * (
                a1 * (R_gal / R_0) ** (a2 - 1) + a3 * (R_0 / R_gal) - 1)
    return c - a


def getRgalFromVlsr(vlsr, glon, glat=0., R_0=8.34, t_0=240., precision=0.001):
    '''
    Calculate Galactocentric radius from line of sight velocity and Galactic longitude.

    @param vlsr: Line of sight velocity with respect to local standard of rest [km s^-1]
    @type vlsr: float
    @param glon: Galactic longitude [deg]
    @type glon: float
    @param glat: (optional; default glat=0) Galactic latitude [deg]
    @type glat: float
    @param R_0: (optional; default R_0=8.34) Distance to Galactic center [kpc]
    @type R_0: float
    @param t_0: (optional; default Theta_0=248.) Circular rotation velocity at orbit of
                the sun [km s^-1]
    @type t_0: float
    @param precission: (optional; default prec=0.001) Precission of the result [km s^-1]
    @type precission: float
    @return: Galactocentric radius [kpc]
    @rtype: float

    '''
    # make it 2D and column vector (i.e. transpose) if array is given
    if hasattr(vlsr, '__len__'):
        # solution for input arrays
        if type(vlsr) != np.array:
            vlsr = np.array(vlsr)
        vlsr = vlsr[np.newaxis].T
    if hasattr(glon, '__len__'):
        # solution for input arrays
        if type(glon) != np.array:
            glon = np.array(glon)
        glon = glon[np.newaxis].T

    distances = np.arange(0.1, 30. + precision, precision)
    residuals = _residual_brand(distances, vlsr, glon, glat=glat, t_0=t_0, R_0=R_0)
    min_index = np.argmin(np.abs(residuals), axis=len(residuals.shape) - 1)
    R_gal_min = distances[min_index]
    print(distances)

    try:
        # solution for input arrays
        # assume no solution is found if in the extreme values
        is_invalid = (min_index == 0) + (min_index == len(distances) - 1)
        R_gal_min[is_invalid] = np.nan
    except TypeError:
        # solution for single float input
        if min_index in (0, len(distances)):
            R_gal_min = np.nan

    return np.round(R_gal_min, int(np.abs(np.log10(precision))))


def getVlsrFromRgal(R_gal, glon, glat=0., R_0=8.34, t_0=240, precision=0.001):
    '''
    Calculate line of sight velocity from Galactocentric radius.

    @param R_gal: Galactocentric radius [kpc]
    @type R_gal: float
    @param glon: Galactic longitude [deg]
    @type glon: float
    @param glat: (optional; default glat=0) Galactic latitude [deg]
    @type glat: float
    @param R_0: (optional; default R_0=8.34) Distance to Galactic center [kpc]
    @type R_0: float
    @param t_0: (optional; default Theta_0=248.) Circular rotation velocity at orbit of
                the sun [km s^-1]
    @type t_0: float
    @param precission: (optional; default prec=0.001) Precission of the result [km s^-1]
    @type precission: float
    @return: Line of sight velocity with respect to local standard of rest [km s^-1]
    @rtype: float

    '''
    # make it 2D and column vector (i.e. transpose) if array is given
    if hasattr(R_gal, '__len__'):
        # solution for input arrays
        if type(R_gal) != np.array:
            R_gal = np.array(R_gal)
        R_gal = R_gal[np.newaxis].T
    if hasattr(glon, '__len__'):
        # solution for input arrays
        if type(glon) != np.array:
            glon = np.array(glon)
        glon = glon[np.newaxis].T

    vlsrs = np.arange(-200., 200. + precision, precision)
    residuals = _residual_brand(R_gal, vlsrs, glon, glat=glat, t_0=t_0, R_0=R_0)
    min_index = np.argmin(np.abs(residuals), axis=len(residuals.shape) - 1)
    vlsr_min = vlsrs[min_index]

    try:
        # solution for input arrays
        # assume no solution is found if in the extreme values
        is_invalid = (min_index == 0) + (min_index == len(vlsrs) - 1)
        vlsr_min[is_invalid] = np.nan
    except TypeError:
        # solution for single float input
        if vlsr_min in (-200., 200.):
            vlsr_min = np.nan

    return np.round(vlsr_min, int(np.abs(np.log10(precision))))
