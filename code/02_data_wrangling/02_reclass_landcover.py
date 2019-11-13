#!/usr/bin/env python3
# =============================================================================
# Date:     February, 2019
# Author:   Marcelo Villa P.
# Purpose:  Reclassifies the MCD12Q1 Land Cover products to group the different
#           classes into more general ones.
# Notes:    Here is the class of each pixel value in the original MCD12Q1 -
#           Land Cover Type 2 (UMD classification scheme) product:
#           0   Water bodies
#           1   Evergreen Needleleaf Forests
#           2   Evergreen Broadleaf Forests
#           3   Deciduous Needleleaf Forests
#           4   Deciduous Broadleaf Forests
#           5   Mixed Forests
#           6   Closed Shrublands
#           7   Open Shrublands
#           8   Woody Savannas
#           9   Savannas
#           10  Grasslands
#           11  Permanent Wetlands
#           12  Croplands
#           13  Urban and Built-up Lands
#           14  Cropland/Natural Vegetation Mosaics
#           15  Non-Vegetated Lands
#           255 Unclassified
#
#           More information about this product can be found at:
#           https://lpdaac.usgs.gov/sites/default/files/public/
#           product_documentation/mcd12_user_guide_v6.pdf
# =============================================================================
import glob
import os
import re

import gdal
import numpy as np

from code.functions import array_to_tif


def reclass(arr):
    """
    Reclassifies original Land Cover Type raster to new grouped classes. This
    classes are:

    0   Non-flammable
    1   Forest
    2   Savannas
    3   Grasslands
    4   Croplands
    255 Unclassified

    Here is the mapping of the original values to the new values:
    0   ->  0   ||   4   ->  1   ||   8   ->  2   ||   12  ->  4
    1   ->  1   ||   5   ->  1   ||   9   ->  2   ||   13  ->  0
    2   ->  1   ||   6   ->  3   ||   10  ->  3   ||   14  ->  4
    3   ->  1   ||   7   ->  3   ||   11  ->  0   ||   15  ->  0

    :param arr:   2D numpy array
    :return:      2D numpy array
    """

    # get size or input array
    y, x = arr.shape

    # create a Boolean aoi_mask for each of the new values (i.e. 0 - 5)
    con1 = np.in1d(arr, [0, 11, 13, 15]).reshape((y, x))  # val 0
    con2 = np.in1d(arr, [1, 2, 3, 4, 5]).reshape((y, x))  # val 1
    con3 = (arr == 8) | (arr == 9)                        # val 2
    con4 = (arr == 6) | (arr == 7) | (arr == 10)          # val 3
    con5 = (arr == 12) | (arr == 14)                      # val 4

    # group conditions and apply the corresponding values
    cons = [con2, con3, con4, con5]
    reclassed_arr = np.where(con1, 0, arr)
    for i, con in enumerate(cons, 1):
        reclassed_arr = np.where(con, i, reclassed_arr)

    return reclassed_arr


if __name__ == '__main__':
    # change directory to the MCD12Q1 folder and get all files
    os.chdir('../../data/tif/MODIS/MCD12Q1')

    if not os.path.exists('preprocessed'):
        os.makedirs('preprocessed')

    filenames = glob.glob('original/*')

    for fn in filenames:
        # read raster and get projection, geotransform and data
        ds = gdal.Open(fn, 0)
        sr = ds.GetProjection()
        gt = ds.GetGeoTransform()
        arr = ds.ReadAsArray()
        nd_val = ds.GetRasterBand(1).GetNoDataValue()
        del ds

        # reclass array
        reclassed_arr = reclass(arr)

        # define new name and create reclassed GeoTIFF
        regex = re.compile('[0-9]{7}')
        date = re.search(regex, fn).group(0)
        year = date[:4]
        new_fn = f'preprocessed/MCD12Q1_{year}.tif'
        array_to_tif(reclassed_arr, new_fn, sr, gt, gdal.GDT_UInt16, nd_val)
