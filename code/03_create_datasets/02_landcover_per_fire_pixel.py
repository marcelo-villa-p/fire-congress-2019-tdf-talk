#!/usr/bin/env python3
# =============================================================================
# Date:     November, 2019
# Author:   Marcelo Villa P.
# Purpose:  Creates a csv file with yearly landcover information for every fire
#           pixel identified during each year.
# =============================================================================
import os

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
    cols = ['year', 'code']
    df = pd.DataFrame(columns=cols)

    for year in years:
        # filter data arrays by year
        fire_arr = fire_data.loc[year].values
        lc_arr = lc_data.loc[year].values

        # get all fire pixels for the whole year
        mask = ((fire_arr != 0) & (fire_arr != fire_nd)).any(axis=0)

        # get landcover values for fire pixels, excluding Non-Flammable and
        # NoData values
        values = lc_arr[mask]
        mask2 = (values != 0) & (values != lc_nd)

        # create empty DataFrame to store the year's results
        year_df = pd.DataFrame(columns=cols)
        year_df['code'] = values[mask2]
        year_df['year'] = year

        # append year's DataFrame to original DataFrame
        df = df.append(year_df, ignore_index=True)

    # assign landcover names
    df['name'] = df['code'].map(landcovers)

    # save DataFrame to csv
    df.to_csv('../../csv/landcover_per_fire_pixel.csv', index=False)
