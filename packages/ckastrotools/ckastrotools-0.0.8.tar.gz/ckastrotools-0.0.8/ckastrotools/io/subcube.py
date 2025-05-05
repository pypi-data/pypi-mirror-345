"""Module to work on subcubes."""
from typing import Optional
import astropy.units as u
from spectral_cube import SpectralCube


def extractCutout(cube: SpectralCube,
                  glon: float, glat: float,
                  width: float,
                  v_min: Optional[float] = None, v_max: Optional[float] = None) -> SpectralCube:
    """
    Extract a square cutout from a larger cube.

    Parameters
    ----------
    cube:
        The original SpectralCube to extract from.
    glon:
        Galactic longitude of the center.
    glat:
        Galactic latitude of the center.
    width:
        Width in degrees.
    v_min:
        Minimum velocity in km/s (default = -49.5 km/s).
    v_max:
        Maxiumum velocity in km/s (default = 150 km/s).

    Returns
    -------
    subcube: spectral_cube.SpectralCube
        Returns the extracted subcube.
    """
    glon_min = glon - width / 2
    glon_max = glon + width / 2
    glat_min = glat - width / 2
    glat_max = glat + width / 2

    if v_min is None:
        v_min = -49.5  # [km/s]
    if v_max is None:
        v_max = 150  # [km/s]

    return cube.subcube(xlo=glon_min * u.deg, xhi=glon_max * u.deg,
                        ylo=glat_min * u.deg, yhi=glat_max * u.deg,
                        zlo=v_min * u.km / u.s, zhi=v_max * u.km / u.s)
