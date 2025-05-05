"""Compare two datasets."""
from copy import copy

import numpy as np
from matplotlib import pylab as plt
from spectral_cube import SpectralCube


def headers_are_same(header1, header2, exclude=None):
    """
    Compare two FITS headers.

    Parameters
    ----------
    header1: astropy.io.fits.Header
        The first FITS header.
    header2: astropy.io.fits.Header
        The second FITS header.
    exclude: list of str, optional
        List of header keywords to exclude from the comparison. Default is None, which means no keywords are excluded.

    Returns
    -------
    bool
        True if the headers are the same, False otherwise.

    """
    if exclude is None:
        exclude = []

    error_count = 0
    for k in header1.keys():
        if k not in exclude:
            if k not in header2:
                error_count += 1
            else:
                if header1[k] != header2[k]:
                    error_count += 1
                    print(f"found difference [{k}]")
                    print(f"  old: {header1[k]}")
                    print(f"  new: {header2[k]}")

    if error_count == 0:
        print("Headers are the same.")
        return True
    else:
        print("Headers are not the same (see above).")
        return False


def data_is_same(data1, data2, replace_nans=None):
    """
    Compare two data cubes.

    Parameters
    ----------
    data1: numpy.ndarray
        The first data cube.
    data2: numpy.ndarray
        The second data cube.
    replace_nans: float, optional
        Value to replace NaNs with before comparison. Default is None, which means no replacement is done.

    Returns
    -------
    bool
        True if the data cubes are the same, False otherwise.

    """
    if replace_nans is not None:
        data1_test = copy(data1)
        data1_test[np.isnan(data1_test)] = replace_nans

        data2_test = copy(data2)
        data2_test[np.isnan(data2_test)] = replace_nans

        residual = data1_test - data2_test
    else:
        residual = data1 - data2

    if np.min(residual) == np.max(residual) == 0:
        print("Data is the same")
        return True
    else:
        print("Data is not the same.")
        return False


def fits_cubes_are_same(filename1, filename2):
    """
    Compoare two FITS files.

    Parameters
    ----------
    filename1: str
        The first FITS file.
    filename2: str
        The second FITS file.

    Returns
    -------
    bool
        True if the files are the same, False otherwise.
    """
    cube1 = SpectralCube.read(filename1)
    header1 = cube1.hdu.header
    data1 = cube1.hdu.data

    cube2 = SpectralCube.read(filename2)
    header2 = cube2.hdu.header
    data2 = cube2.hdu.data

    headers_same = headers_are_same(header1, header2, exclude=["HISTORY"])
    data_same = data_is_same(data1, data2)

    if headers_same and data_same:
        print("-> Files represent identical astronomical data.")
        return True
    else:
        print("-> Files are not the same.")
        return False
