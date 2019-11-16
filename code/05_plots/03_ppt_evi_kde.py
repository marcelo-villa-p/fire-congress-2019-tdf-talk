#!/usr/bin/env python3
# =============================================================================
# Date:     November, 2019
# Author:   Marcelo Villa P.
# Purpose:
# =============================================================================
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from code.functions import beautify_ax, create_data_array, get_nodata_value, \
                           init_sns
from code.variables import edge_color, evi_scaling_factor, face_color, \
                           hue_one, hue_two

if __name__ == '__main__':
    # change directory and define product paths
    os.chdir('../../data/tif')
    fire_path = 'MODIS/MOD14A2/prepared'
    paths = ['TRMM/3B43/prepared', 'MODIS/MOD13A3/prepared']

    # create fire array and get NoData value
    date_range = pd.date_range('2002', '2017', freq='MS', closed='left')
    fire_arr = create_data_array(fire_path, date_range).values
    fire_nd = get_nodata_value(fire_path)
    fire_mask = (fire_arr != fire_nd) & (fire_arr != 0)

    # initialize seaborn environment and create figure and axes
    init_sns()
    fig, axs = plt.subplots(ncols=2, nrows=1)
    hue_colors = [hue_one, hue_two]
    labels = ['Precipitation (mm/month)', 'Enhanced Vegetation Index']

    for i, path in enumerate(paths):
        arr = create_data_array(path, date_range, offset=3).values
        nd = get_nodata_value(path)
        mask = (arr != nd)

        # get all values (excluding NoData) and masked values (for fire-pixels)
        all_values = arr[mask]
        masked_values = arr[mask & fire_mask]

        for j, values in enumerate([all_values, masked_values]):
            # rescale values for EVI
            if path == 'MODIS/MOD13A3/prepared':
                values = values * evi_scaling_factor

            # plot kernel density estimate
            sns.kdeplot(values, shade=True, ax=axs[i], color=hue_colors[j],
                        linewidth=0.5)

        # set x label and beautify ax
        axs[i].set_xlabel(labels[i], labelpad=10, color=edge_color)
        beautify_ax(axs[i], edge_color, face_color)

    # adjust y axis limits on the second column
    axs[1].set_ylim([0, 5])

    # adjust plot layout and save figure
    sns.despine(offset={'left': 5, 'bottom': 10}, trim=True)
    plt.subplots_adjust(wspace=0.4, hspace=1)
    plt.tight_layout()
    fn = '../../figures/graph/ppt_evi_kde.pdf'
    plt.savefig(fn, format='pdf', dpi=1200, facecolor=face_color)
