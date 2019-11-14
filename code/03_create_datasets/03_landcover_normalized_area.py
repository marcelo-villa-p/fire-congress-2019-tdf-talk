#!/usr/bin/env python3
# =============================================================================
# Date:     November, 2019
# Author:   Marcelo Villa P.
# Purpose:  Creates a csv file with yearly landcover information for every fire
#           pixel identified during each year.
# =============================================================================
import os

import numpy as np
import pandas as pd

from code.functions import create_data_array, get_nodata_value
from code.variables import landcovers

if __name__ == '__main__':
    # change directory
    os.chdir('../../data/tif/MODIS/MCD12Q1/prepared')

    # create landcover DataArray
    years = pd.date_range('2002', '2016', freq='AS').year.astype('str')
    data = create_data_array('.', years)
    nd = get_nodata_value('.')

    # create empty DataFrame
    cols = ['year', 'code', 'pixels', 'proportion']
    df = pd.DataFrame(columns=cols)

    for i, year in enumerate(years):
        # filter DataArray by year and get pixel count by landcover
        arr = data.loc[year].values
        mask = (arr != 0) & (arr != nd)
        values, counts = np.unique(arr[mask], return_counts=True)

        # create year's DataFrame
        year_df = pd.DataFrame(columns=cols)
        year_df['code'] = values
        year_df['pixels'] = counts
        year_df['proportion'] = year_df['pixels'] / counts.sum()
        year_df['year'] = year

        # append year's
        df = df.append(year_df, ignore_index=True)

    # assign landcover names
    df['name'] = df['code'].map(landcovers)

    # save DataFrame to csv
    df.to_csv('../../../../csv/landcover_normalized_area.csv', index=False)
