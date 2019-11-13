#!/usr/bin/env python3
# =============================================================================
# Date:     February, 2019
# Author:   Marcelo Villa P.
# Purpose:  Groups every 8-day MOD14A2 product into monthly fire sum rasters.
#           All the pixels that are identified as fires with nominal or high
#           confidence are summed and all the pixels that represent a non-fire
#           pixel are assigned a value of 0. The rest of the pixels are
#           assigned a value of 255 and represent pixels where one cannot be
#           sure if a fire occurred or not.
# Notes:    Here is the description of each pixel value in the original MOD14A2
#           product:
#           0   not processed
#           1   not processed
#           2   not processed
#           3   non-fire water pixel
#           4   cloud
#           5   non-fire land pixel
#           6   unknown
#           7   fire (low confidence)
#           8   fire (nominal confidence)
#           9   fire (high confidence)
# =============================================================================
import glob
import os
import re

import gdal
import numpy as np

from code.functions import array_to_tif, doy_to_month


def pixel_classification(arr):
    """
    Reclassifies the original MOD14A2 product into three different values:
    Non-fire pixels (pixel-value: 5) -> 0
    Fire pixels (pixel-value: 8 & 9) -> 1
    Other pixels                     -> NaN

    The reason for other pixel values to be assigned a NaN value is that one
    cannot be sure if a fire occurred in the pixel or not, whereas with non-
    fire pixels one can be sure a fire did not occur. This is useful in a
    scenario where one wants to distinguish between certain and uncertain
    pixels (e.g. when one needs presence and absence data).

    :param arr: numpy array
    :return:    numpy array
    """
    con1 = (arr == 8) | (arr == 9)  # fire pixel
    con2 = (arr == 5)               # non-fire pixel
    return np.where(con1, 1, np.where(con2, 0, np.nan))


def sum_fire_pixels(arr):
    """
    Sums fire pixels (pixel-value: 1) in a 3D numpy array. NaN values (i.e.
    every original pixel value different than 5, 8 or 9) remain as NaN values.
    Non-fire pixels (pixel-value: 0) remain as 0 except when summed with a fire
    pixel or with a NaN pixel, in which case it turns into a NaN value.

    :param arr: 3D numpy array
    :return:    2D numpy array
    """
    arr = np.where((arr == 1).any(0), np.nansum(arr, 0), np.sum(arr, 0))
    arr[np.isnan(arr)] = 255
    return arr.astype(np.int)


if __name__ == '__main__':
    # change directory to the MOD14A2 folder and get all files
    os.chdir('../../data/tif/MODIS/MOD14A2')

    if not os.path.exists('preprocessed'):
        os.makedirs('preprocessed')

    # get unique years
    regex = re.compile('[0-9]{7}')
    years = set([re.search(regex, fn).group(0)[:4] for fn in os.listdir('./original')])
    years = sorted(list(years))

    # read first file and get geotransform and spatial reference data
    fn = glob.glob('original/*.tif')[0]
    ds = gdal.Open(fn, 0)
    sr = ds.GetProjection()
    gt = ds.GetGeoTransform()
    del ds

    for year in years:
        # group file names by month
        groups = {}
        for fn in glob.glob(f'original/*{year}*.tif'):
            doy = re.search(regex, fn).group(0)[4:]
            month = doy_to_month(year, doy)
            groups.setdefault(month, []).append(fn)

        for month in groups.keys():
            mo_array = []  # store the 8-day arrays
            for fn in groups[month]:
                ds = gdal.Open(fn, 0)
                array = ds.ReadAsArray()
                mo_array.append(array)
                del ds

            # compute and save monthly array
            mo_array = np.stack(mo_array)  # list of arrays to 3D array
            mo_array = pixel_classification(mo_array)
            mo_array = sum_fire_pixels(mo_array)
            fn = f'preprocessed/MOD14A2_{year}{month}.tif'
            array_to_tif(mo_array, fn, sr, gt, gdal.GDT_UInt16, 255)
