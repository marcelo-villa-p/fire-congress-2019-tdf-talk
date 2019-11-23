#!/usr/bin/env python3
# =============================================================================
# Date:     February, 2019
# Author:   Marcelo Villa P.
# Purpose:  Contains functions shared across multiple scripts in the project.
# =============================================================================
import datetime
import glob
import os

import gdal
import numpy as np
import seaborn as sns
import xarray as xr


def array_to_tif(arr, fn, sr, geotransform, gdtype, nd_val=None):
    """
    Writes a 2D NumPy array to a GeoTIFF file in disk.
    :param arr:             2D NumPy array
    :param fn:              output GeoTIFF's file name
    :param sr:              output GeoTIFF's spatial reference
    :param geotransform:    output GeoTIFF's geotransform
    :param gdtype:          GDAL data type
    :param nd_val:          output GeoTIFF's NoData value
    :return:                None
    """

    # get driver and create output TIFF
    driver = gdal.GetDriverByName('GTiff')
    out_tif = driver.Create(fn, arr.shape[1], arr.shape[0], 1, gdtype)

    # set projection and geotransform
    out_tif.SetProjection(sr)
    out_tif.SetGeoTransform(geotransform)

    # set NoData value and write array
    band = out_tif.GetRasterBand(1)
    if nd_val:
        band.SetNoDataValue(nd_val)
    band.WriteArray(arr)

    # flush to disk
    band.FlushCache()
    del out_tif, band


def beautify_ax(ax, edge_color, face_color):
    """
    Beautifies an ax object by adjusting axis and ticks and changing colors.
    :param ax:
    :return:
    """
    # set ticks only on the left and the bottom
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')

    # change ticks length and width
    ax.xaxis.set_tick_params(direction='in', length=3, width=0.5,)
    ax.yaxis.set_tick_params(direction='in', length=3, width=0.5)

    # change axis spines width and color
    ax.spines['left'].set_linewidth(0.5)
    ax.spines['bottom'].set_linewidth(0.5)
    ax.spines['left'].set_color(edge_color)
    ax.spines['bottom'].set_color(edge_color)

    # set patch face color
    ax.patch.set_facecolor(face_color)

    # change ticks and labels color
    ax.tick_params(axis='both', colors=edge_color, which='both')


def beautify_box(ax, edge_color, face_color):
    """
    Beautifies boxplot boxes by changing their edge and face colors.
    :param ax:  matplotlib.axes._subplots.AxesSubplot object
    :return:    None
    """
    for j, box in enumerate(ax.artists):
        box.set_edgecolor(edge_color)
        box.set_facecolor(face_color)
        for n in range(6 * j, 6 * (j + 1)):
            ax.lines[n].set_color(edge_color)


def create_data_array(folder, date_range, offset=None):
    """
    Creates a xarray DataArray from all the GeoTIFF files found in the folder
    parameter. The result DataArray has three dimensions:
        * t: time
        * y: latitude
        * x: longitude

    :param folder:      path to the folder with the GeoTIFF files
    :param date_range:  pandas.core.indexes.datetimes.DatetimeIndex object,
                        which can be created using the pd.date_range function
    :param offset:      number of files to skip at the beginning
    :return:            xarray.core.dataarray.DataArray object
    """
    # read each individual array, store them and stack them
    data = []
    for fn in glob.glob(os.path.join(folder, '*.tif'))[offset:]:
        ds = gdal.Open(fn, 0)
        arr = ds.ReadAsArray()
        data.append(arr)
        del ds, arr
    data = np.stack(data)

    return xr.DataArray(data, coords={'t': date_range}, dims=('t', 'y', 'x'))


def doy_to_month(year, doy):
    """
    Converts a three-digit string with the day of the year to a two-digit
    string representing the month. Takes into account leap years.
    :param year: four-digit year
    :param doy:  three-digit day of the year
    :return:     two-digit string month
    """
    dt = datetime.datetime.strptime(f'{year} {doy}', '%Y %j')
    return dt.strftime('%m')


def get_nodata_value(folder):
    """
    Gets the NoData value from the first GeoTIFF file found on the folder
    parameter.
    :param folder: path to the folder with the GeoTIFF files
    :return:       NoData value
    """
    fn = glob.glob(os.path.join(folder, '*.tif'))[0]
    ds = gdal.Open(fn, 0)
    nd = ds.GetRasterBand(1).GetNoDataValue()
    del ds

    return nd


def init_sns():
    """
    Initializes seaborn environment by setting the plots' context and style.
    :return:
    """
    sns.set_context('paper')
    sns.set_style('white')
