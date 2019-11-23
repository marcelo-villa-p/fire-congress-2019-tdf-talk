#!/usr/bin/env python3
# =============================================================================
# Date:     November, 2019
# Author:   Marcelo Villa P.
# Purpose:  Groups fire pixels, precipitation and Enhanced Vegetation Index
#           (EVI) data for each month. Previous 3 months average values for
#           precipitation and EVI are also calculated.
# =============================================================================
import os

import numpy as np
import pandas as pd

from code.functions import create_data_array, get_nodata_value
from code.variables import evi_scaling_factor


def get_data_statistic(data, nd, start=0, end=None, statistic='mean'):
    """
    Gets a specific statistic from a (sliced) xarray DataArray.
    :param data:        xarray.core.dataarray.DataArray object
    :param nd:          NoData value
    :param start:       start in the first dimension
    :param end:         end in the first dimension
    :param statistic:   statistic to be computed. Possible values are:
                            * 'mean'
                            * 'sum'
    :return:            single float
    """
    arr = data.loc[start:end].values
    arr = np.ma.array(arr, mask=(arr == nd))

    if statistic == 'mean':
        return arr.mean()
    elif statistic == 'sum':
        return arr.sum()
    else:
        raise NotImplementedError()


if __name__ == '__main__':
    # change directory
    os.chdir('../../data/tif')

    # create empty DataFrame
    columns = ['fire_pixels', 'evi', 'evi_prev', 'ppt', 'ppt_prev']
    df = pd.DataFrame(columns=columns)

    # define date range
    date_range_off = pd.date_range('2001-10-01', '2016-12-31', freq='MS')
    date_range = date_range_off[3:]

    # define products and their properties
    products = [
        {'path': 'MODIS/MOD14A2/prepared', 'col': 'fire_pixels', 'stat': 'sum',
         'compute_prev': False, 'date_range': date_range},
        {'path': 'MODIS/MOD13A3/prepared', 'col': 'evi', 'stat': 'mean',
         'compute_prev': True, 'date_range': date_range_off},
        {'path': 'TRMM/3B43/prepared', 'col': 'ppt', 'stat': 'mean',
         'compute_prev': True, 'date_range': date_range_off},
    ]

    for prod in products:
        data = create_data_array(prod['path'], prod['date_range'])
        nd = get_nodata_value(prod['path'])
        for i, month in enumerate(date_range):
            # calculate stat for current month
            stat = get_data_statistic(data, nd, month, month, prod['stat'])
            df.loc[i, prod['col']] = stat

            # compute previous 3 month period
            if prod['compute_prev']:
                start = month - pd.DateOffset(months=3)
                end = month - pd.DateOffset(months=1)
                stat = get_data_statistic(data, nd, start, end, prod['stat'])
                df.loc[i, f'{prod["col"]}_prev'] = stat

    # set index as date and change data types
    df.index = date_range
    df['fire_pixels'] = df['fire_pixels'].astype('int')
    df[df.columns[1:]] = df[df.columns[1:]].astype('float')

    # rescale EVI values using a defined scaling factor
    df['evi'] = df['evi'] * evi_scaling_factor
    df['evi_prev'] = df['evi_prev'] * evi_scaling_factor

    # save DataFrame to csv
    df.to_csv('../csv/groupby_area.csv', index=True, index_label='date')
