"""Module to extract spectra from a FITS data cube."""
import numpy as np
import matplotlib.pyplot as plt

from spectral_cube import SpectralCube

from ..io.subcube import extractCutout


def extractSpectrumAroundCenter(cube, glon, glat, pixel_width=3, plot=False):
    width = (pixel_width - 0.9) * np.abs(
        cube.header["CDELT1"]
    )  # [deg] 2.1pixels around center = 3x3 pixel
    cutout = extractCutout(cube, glon, glat, width)  # extract central 9 pixels

    img = np.array(cutout.max(axis=0))
    if plot:
        plt.imshow(img)

    spectrum = cutout.mean(axis=(1, 2))  # get spectrum over central 9 pixels (~1 beam)
    if plot:
        plt.figure(figsize=(10, 2))
        plt.plot(spectrum)
    return spectrum


def extractSpectrumInAperture(source, input_filename, line, output_folder, radius=120, plot=False):
    radius_in_deg = radius / 3600.0
    global cutout
    cube = SpectralCube.read(input_filename)
    cutout = extractCutout(cube, source["gal_long"], source["gal_lat"], width=2.1 * radius_in_deg)

    n_velocity = cutout.header["NAXIS3"]  # vlsr
    width = cutout.header["NAXIS1"]  # glon
    height = cutout.header["NAXIS2"]  # glat

    # # Create a grid of x and y coordinates
    x = np.arange(-width / 2, width / 2, dtype="int").reshape((width, 1))
    y = np.arange(-height / 2, height / 2, dtype="int").reshape((1, height))

    # Compute the distance from the center for the x and y dimensions
    distance = np.sqrt(x ** 2 + y ** 2)

    # Create a 2D mask where the distance is greater than the requested radius
    mask_2d = distance > (radius_in_deg / np.abs(cube.header["CDELT1"]))

    # Extend this 2D mask across the entire depth to make it a 3D mask
    mask_3d = np.repeat(mask_2d[:, :, np.newaxis], n_velocity, axis=2).T
    # mask the cutout
    cutout = cutout.with_mask(~mask_3d)
    if plot:
        # check if the mask was applied correctly
        plt.imshow(np.array(cutout.mean(axis=0)))

    cutout.allow_huge_operations = True

    spectrum = cutout.mean(axis=(1, 2))
    if plot:
        # plot the resulting spectrum
        plt.figure(figsize=(10, 2))
        plt.plot(spectrum)

    spectrum.write(
        f'{output_folder}/{source["higal_name"]}_{line}_{radius:0.0f}arcsec_spectrum.fits',
        overwrite=True,
    )
