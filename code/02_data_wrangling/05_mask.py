#!/usr/bin/env python3
# =============================================================================
# Date:     November, 2019
# Author:   Marcelo Villa P.
# Purpose:  Masks a set of GeoTIFF files with an Area Of Interest (AOI) Shape-
#           file using GDAL Warp.
# Notes:    Documentation about both GDAL Warp command line utility and its
#           Python bindings (i.e. gdal.Warp) can be found on:
#               * https://gdal.org/programs/gdalwarp.html
#               * https://gdal.org/python/osgeo.gdal-module.html#Warp
# =============================================================================
import glob
import os

import gdal


if __name__ == '__main__':
    # change directory
    os.chdir('../../data/tif')

    # define mask (shapefile)
    mask = '../shp/aoi/TDF_biome_COL_4326.shp'

    # define products to be cropped and resampled
    products = [
        {'parent': 'MODIS', 'prod': 'MCD12Q1', 'dir': 'resampled',
         'algo': 'mode'},
        {'parent': 'MODIS', 'prod': 'MOD13A3', 'dir': 'original',
         'algo': 'bilinear'},
        {'parent': 'MODIS', 'prod': 'MOD14A2', 'dir': 'preprocessed',
         'algo': 'near'},
        {'parent': 'TRMM', 'prod': '3B43', 'dir': 'resampled',
         'algo': 'cubic'}
    ]

    for prod in products:
        base = os.path.join(prod['parent'], prod['prod'])
        path = os.path.join(base, prod['dir'], '*.tif')
        filenames = glob.glob(path)

        # create output directory if it does not exist
        out_path = os.path.join(base, 'prepared')
        if not os.path.exists(out_path):
            os.makedirs(out_path)

        for fn in filenames:
            base_name = os.path.basename(fn)
            dst_fn = os.path.join(out_path, base_name)
            if not os.path.exists(dst_fn):
                kwargs = {
                    'format': 'GTiff',
                    'resampleAlg': prod['algo'],
                    'cutlineDSName': mask,
                    'cropToCutline': True
                }
                ds = gdal.Warp(dst_fn, fn, **kwargs)
                del ds
