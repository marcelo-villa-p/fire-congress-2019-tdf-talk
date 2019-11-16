#!/usr/bin/env python3
# =============================================================================
# Date:     November, 2019
# Author:   Marcelo Villa P.
# Purpose:
# =============================================================================
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from code.functions import beautify_ax, create_data_array, get_nodata_value, \
                           init_sns
from code.variables import edge_color, face_color, hue_one


if __name__ == '__main__':
    # change directory
    os.chdir('../../data/tif/MODIS')
    fire_path = 'MOD14A2/prepared'
    dtnf_path = 'derived/DTNF'

    # create fire array and get NoData value
    date_range = pd.date_range('2002', '2017', freq='MS', closed='left')
    fire_data = create_data_array(fire_path, date_range)
    fire_nd = get_nodata_value(fire_path)
    fire_mask = (fire_data != fire_nd) & (fire_data != 0)

    # create fire pixels mask grouped by year
    grouped_fire_mask = fire_mask.groupby(fire_data.t.dt.year).any(dim='t').values

    # create DataArray for forest proximity and fire
    years = date_range.year.unique().astype('str')
    arr = create_data_array(dtnf_path, years).values
    nd = 32767
    mask = (arr != nd)

    # get distance values for fire pixels and create bins for the histogram
    values = arr[grouped_fire_mask & mask]
    bins = np.arange(values.min(), values.max()) - 0.5  # one pixel bins

    # initialize seaborn environment and create plot
    init_sns()
    f, ax = plt.subplots(1, 1)

    # create histogram and set first bin (forest pixels) to red
    sns.distplot(values, ax=ax, color=hue_one, bins=bins)
    ax.patches[0].set_color('r')
    ax.patches[0].set_alpha(0.75)

    # set x label and beautify ax
    label = 'Distance to nearest forest (pixels)'
    ax.set_xlabel(label, labelpad=10, color=edge_color)
    beautify_ax(ax, edge_color, face_color)

    # adjust plot layout and save figure
    sns.despine(offset={'left': 5, 'bottom': 10}, trim=True)
    plt.subplots_adjust(wspace=0.4, hspace=1)
    plt.tight_layout()
    fn = '../../../figures/graph/distance_to_nearest_forest_hist.pdf'
    plt.savefig(fn, format='pdf', dpi=1200, facecolor=face_color)
