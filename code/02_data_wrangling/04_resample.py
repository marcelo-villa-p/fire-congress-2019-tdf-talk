#!/usr/bin/env python3
# =============================================================================
# Date:     November, 2019
# Author:   Marcelo Villa P.
# Purpose:  Resamples all cells of GeoTIFF files to a specified size using
#           GDAL Warp and a specified resampling algorithm.
# Notes:    Documentation about both GDAL Warp command line utility and its
#           Python bindings (i.e. gdal.Warp) can be found on:
#               * https://gdal.org/programs/gdalwarp.html
#               * https://gdal.org/python/osgeo.gdal-module.html#Warp
# =============================================================================
import glob
import os

import gdal


def get_resolution(fn):
    """
    Gets the x and y resolution of a GeoTiff and returns them as a tuple.
    :param fn: GeoTIFF filename
    :return:   tuple with x and y resolutions
    """
    ds = gdal.Open(fn, 0)
    gt = ds.GetGeoTransform()

    return gt[1], -gt[-1]


if __name__ == '__main__':
    # change directory
    os.chdir('../../data/tif')

    # define a sample to get properties from
    target_sample = glob.glob('MODIS/MOD14A2/original/*.tif')[0]
    x_res, y_res = get_resolution(target_sample)

    # define products to be resampled
    products = [
        {'parent': 'MODIS', 'prod': 'MCD12Q1', 'dir': 'preprocessed',
         'algo': 'mode'},
        {'parent': 'TRMM', 'prod': '3B43', 'dir': 'preprocessed',
         'algo': 'cubic'}
    ]

    for prod in products:
        base = os.path.join(prod['parent'], prod['prod'])
        path = os.path.join(base, prod['dir'], '*.tif')
        filenames = glob.glob(path)

        # create output directory if it does not exist
        out_path = os.path.join(base, 'resampled')
        if not os.path.exists(out_path):
            os.makedirs(out_path)

        for fn in filenames:
            base_name = os.path.basename(fn)
            dst_fn = os.path.join(out_path, base_name)
            if not os.path.exists(dst_fn):
                kwargs = {
                    'format': 'GTiff',
                    'xRes': x_res,
                    'yRes': y_res,
                    'resampleAlg': prod['algo']
                }
                ds = gdal.Warp(dst_fn, fn, **kwargs)
                del ds
