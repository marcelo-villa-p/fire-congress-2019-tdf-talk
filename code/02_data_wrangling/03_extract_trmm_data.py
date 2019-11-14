#!/usr/bin/env python3
# =============================================================================
# Date:     March, 2019
# Author:   Marcelo Villa P.
# Purpose:  Takes TRMM monthly precipitation rate data (mm/hr) and creates a
#           monthly precipitation accumulation product by multiplying the ppt
#           rate by 24 (hours in a day) and then by the number of days in the
#           respective month.
# Notes:    The original data consists of compressed gz hdf files. This script
#           decompresses the data, saves an hdf copy to the disk and the
#           resulting products are stored as GeoTIFFs. Furthermore, original
#           data is not properly georeferenced and lacks projection. Therefore,
#           the data is transposed and then flipped. It finally is given a
#           proper geotransform and projection (WGS 84). The bounding box
#           imported from the constants module has to coincide with the
#           bounding box specified when submitting the PPS request. If no
#           bounding box was specified, change the line 99 to:
#           gt = (-180, 0.25, 0, 50, 0, -0.25)
# =============================================================================
import glob
import gzip
import os
import re
import shutil
from calendar import monthrange

import gdal
import numpy as np
import osr

from code.functions import array_to_tif
from code.variables import bbox


def compute_accumulation(arr, date):
    """
    Computes precipitation accumulation (mm) based on precipitation rate
    (mm/hr) data. It multiplies this rate by the number of hours in a day and
    then by the number of days in a given month.

    :param arr:     2D numpy array
    :param date:    a string formatted as 'YYYYMM' (e.g. '201704')
    :return:        2D numpy array
    """
    days = monthrange(int(date[:4]), int(date[4:]))[1]
    hours = 24

    return arr * hours * days


def unzip_file(src, dst):
    """
    Unzips a .gz file. Based on: https://stackoverflow.com/a/44712152/7144368
    :param src:
    :param dst:
    :return:
    """
    with gzip.open(src, 'rb') as gz:
        with open(dst, 'wb') as f:
            shutil.copyfileobj(gz, f)


if __name__ == '__main__':
    # change directory to the root of data and define folders
    os.chdir('../../data')
    gz_folder = 'hdf/TRMM/3B43/original'
    hdf_folder = 'hdf/TRMM/3B43/extracted'
    tif_folder = 'tif/TRMM/3B43/preprocessed'

    # create tif_folder and hdf_folder if they do not exist
    if not os.path.exists(tif_folder):
        os.makedirs(tif_folder)
    if not os.path.exists(hdf_folder):
        os.makedirs(hdf_folder)

    # get all zipped files
    zipped_files = glob.glob(os.path.join(gz_folder, '*.gz'))
    for zipped_file in zipped_files:

        # unzip file with a new, shorter name
        regex = re.compile('[0-9]{8}')
        date = re.search(regex, zipped_file).group(0)[:-2]
        hdf_fn = f'3B43_{date}.hdf'
        hdf_path = os.path.join(hdf_folder, hdf_fn)
        if not os.path.exists(hdf_path):
            unzip_file(zipped_file, hdf_path)

        # read precipitation data from hdf file
        hdf_ds = gdal.Open(hdf_path)
        ds = gdal.Open(hdf_ds.GetSubDatasets()[0][0])
        arr = ds.ReadAsArray()

        # rotate data 90 degrees to the left
        arr = np.flip(arr.T, axis=0)

        # create projection and geotransform
        sr = osr.SpatialReference()
        sr.ImportFromEPSG(4326)
        gt = (bbox[0], 0.25, 0, bbox[3], 0, -0.25)

        # compute precipitation accumulation and save as GeoTIFF
        arr = compute_accumulation(arr, date)
        tif_fn = f'3B43_{date}.tif'
        tif_path = os.path.join(tif_folder, tif_fn)
        if not os.path.exists(tif_path):
            array_to_tif(arr, tif_path, sr.ExportToWkt(), gt, gdal.GDT_Float32,
                         -9999)

        del hdf_ds
