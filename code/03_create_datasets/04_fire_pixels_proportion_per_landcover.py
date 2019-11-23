#!/usr/bin/env python3
# =============================================================================
# Date:     November, 2019
# Author:   Marcelo Villa P.
# Purpose:  Creates a csv with monthly fire pixel proportions for each land
#           cover type.
# =============================================================================
import os

import numpy as np
import pandas as pd

from code.functions import create_data_array, get_nodata_value
from code.variables import landcovers

if __name__ == '__main__':
    # change directory
    os.chdir('../../data/tif/MODIS')

    # define folders for fire and landcover products
    fire_folder = 'MOD14A2/prepared'
    lc_folder = 'MCD12Q1/prepared'

    # define NoData values
    fire_nd = get_nodata_value(fire_folder)
    lc_nd = get_nodata_value(lc_folder)

    # define date ranges to create the data arrays
    months = pd.date_range('2002', '2017', freq='MS', closed='left')
    years = pd.date_range('2002', '2016', freq='AS').year.astype('str')

    # create data arrays
    fire_data = create_data_array(fire_folder, months)
    lc_data = create_data_array(lc_folder, years)

    # create empty DataFrame
    df = pd.DataFrame(columns=list(landcovers.values()))

    for i, month in enumerate(months):
        # filter DataArrays by month
        fire_arr = fire_data.loc[month].values
        lc_arr = lc_data.loc[str(month.year)].values

        # define masks
        fire_mask = (fire_arr != 0) & (fire_arr != fire_nd)

        # compute number of fire pixels for each type of landcover
        fire_pixels_per_cover = []
        for val in landcovers.keys():
            mask = (lc_arr == val)
            fire_pixels = fire_arr[fire_mask & mask].sum()
            fire_pixels_per_cover.append(fire_pixels)

        # compute total number of pixels for each type of landcover
        lc_mask = (lc_arr != 0) & (lc_arr != lc_nd)
        pixels_per_cover = np.unique(lc_arr[lc_mask], return_counts=True)[1]

        # compute proportions and store them in DataFrame
        proportions = fire_pixels_per_cover / pixels_per_cover
        df.loc[i] = proportions

    # save DataFrame to csv
    df.to_csv('../../csv/fire_pixels_proportion_per_landcover.csv', index=False)
