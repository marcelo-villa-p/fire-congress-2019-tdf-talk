#!/usr/bin/env python3
# =============================================================================
# Date:     November, 2019
# Author:   Marcelo Villa P.
# Purpose:  Creates a random sample with land cover and forest proximity
#           information for the same amount of fire and non-fire pixels.
# =============================================================================
import os

import numpy as np
import pandas as pd
from imblearn.under_sampling import RandomUnderSampler

from code.functions import create_data_array, get_nodata_value
from code.variables import landcovers

if __name__ == '__main__':
    # change directory
    os.chdir('../../data/tif/MODIS')

    # define product paths
    fire_path = 'MOD14A2/prepared'
    lc_path = 'MCD12Q1/prepared'
    dtnf_path = 'derived/DTNF'

    # define year and date ranges
    year = '2009'
    years = pd.date_range('2002', '2016', freq='AS').year.astype('str')
    months = pd.date_range('2002', '2017', freq='MS', closed='left')

    # create DataArrays
    fire_data = create_data_array(fire_path, months)
    lc_data = create_data_array(lc_path, years)
    dtnf_data = create_data_array(dtnf_path, years)

    # create empty DataFrame
    cols = ['year', 'is_fire_pixel', 'lc_code', 'forest_distance']
    df = pd.DataFrame(columns=cols)

    for year in years:
        # extract fire values for the given year
        fire_arr = fire_data.loc[year].values
        fire_nd = get_nodata_value(fire_path)
        fire_mask = (fire_arr == fire_nd)
        fire_arr = np.ma.array(fire_arr, mask=fire_mask).sum(axis=0)
        fire_arr = np.ma.where(fire_arr > 0, 1, fire_arr).filled(fire_nd)

        # extract land cover and dtnf values for the given year
        lc_arr = lc_data.loc[year].values
        dtnf_arr = dtnf_data.loc[year].values

        # create masks
        fire_mask = (fire_arr != fire_nd)
        lc_nd = get_nodata_value(lc_path)
        lc_mask = (lc_arr != lc_nd) & (lc_arr != 0)
        dtnf_nd = 32767
        dtnf_mask = (dtnf_arr != dtnf_nd)
        mask = fire_mask & lc_mask & dtnf_mask

        # create empty year DataFrame
        year_df = pd.DataFrame(columns=cols)

        # populate DataFrame
        year_df['is_fire_pixel'] = fire_arr[mask]
        year_df['lc_code'] = lc_arr[mask]
        year_df['forest_distance'] = dtnf_arr[mask]
        year_df['year'] = int(year)

        # append to original df
        df = pd.concat([df, year_df], ignore_index=True)

    # divide DataFrame in X and y
    y_col = 'is_fire_pixel'
    cols.remove(y_col)
    X = df[cols].values
    y = df[y_col].values

    # undersample original data
    rus = RandomUnderSampler(random_state=42)
    X, y = rus.fit_sample(X, y)
    us_df = pd.DataFrame(np.column_stack((y, X)), columns=[y_col] + cols)
    us_df[cols] = X

    # sample data
    n = round(len(us_df) * 0.75)
    sampled_df = us_df.sample(n=25000, random_state=42)

    # create a column with landcover names
    sampled_df['lc_name'] = sampled_df['lc_code'].map(landcovers)

    # save DataFrame
    fn = '../../csv/landcover_and_forest_proximity_per_pixel.csv'
    sampled_df.to_csv(fn, index=False)
