"""Module to get the position of the Galactic bar of the Milky Way."""
import numpy as np
from astropy.coordinates import Galactocentric
from astropy import units as u
from typing import Optional

def getGalacticBar(length:Optional[float]=6., angle:Optional[float]=-50) -> Galactocentric:
    """
    Get the position of the Galactic bar of the Milky Way.

    Parameters
    ----------
    length:float
        Length of the bar in kpc.
    angle:float
        Angle of the bar in degrees.

    Returns
    -------
    bar:astropy.coordinates.Galactocentric
        The position of the bar.
    """
    x = np.linspace(-length/2., length/2., int(length*10)) * np.cos(np.radians(angle)) * u.kpc
    y = np.linspace(-length/2., length/2., int(length*10)) * np.sin(np.radians(angle)) * u.kpc
    return Galactocentric(x=x, y=y, z=np.zeros(len(x)) * u.kpc,
                          galcen_distance=8.3*u.kpc, z_sun=27*u.pc)


