#!/usr/bin/env python3
# =============================================================================
# Date:     November, 2019
# Author:   Marcelo Villa P.
# Purpose:  Creates yearly forest proximity rasters.
# =============================================================================
import glob
import os
import re

import gdal

from code.variables import landcovers


def create_proximity_raster(src, dst, values, units='PIXEL'):
    """
    Creates a proximity raster using gdal.ComputeProximity. NoData pixels in
    the src raster will be considered NoData pixels in the dst raster.
    :param src: source raster filename
    :param dst: dest raster filename
    :return:    None
    """
    # open src raster
    ds = gdal.Open(src, 0)
    gt = ds.GetGeoTransform()
    sr = ds.GetProjection()
    cols = ds.RasterXSize
    rows = ds.RasterYSize

    # create dst raster
    driver = gdal.GetDriverByName('GTiff')
    out_ds = driver.Create(dst, cols, rows, 1, gdal.GDT_Int16)
    out_ds.SetGeoTransform(gt)
    out_ds.SetProjection(sr)

    # define options for gdal.ComputeProximity and execute it
    options = [
        f'VALUES={",".join(map(str, values))}',
        f'DISTUNITS={units}',
        'USE_INPUT_NODATA=YES'
    ]
    gdal.ComputeProximity(ds.GetRasterBand(1), out_ds.GetRasterBand(1), options)

    del ds, out_ds


if __name__ == '__main__':
    # change directory
    os.chdir('../../data/tif/MODIS')

    # create output directory if it does not exist
    save_to = 'derived/DTNF'
    if not os.path.exists(save_to):
        os.makedirs(save_to)

    # get list of landcover GeoTIFF files and NoData value
    lc_path = 'MCD12Q1/prepared'
    filenames = glob.glob(os.path.join(lc_path, '*.tif'))
    forest_val = [k for k, v in landcovers.items() if v == 'Forest'][0]

    # define regex to get file's year
    regex = re.compile('[0-9]{4}')

    for fn in filenames:
        # get file's year and define output filename
        year = re.search(regex, fn).group(0)
        base_name = f'DTNF_{year}.tif'
        dst_fn = os.path.join(save_to, base_name)
        if not os.path.exists(dst_fn):
            create_proximity_raster(fn, dst_fn, [forest_val])
