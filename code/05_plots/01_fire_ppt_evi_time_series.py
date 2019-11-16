#!/usr/bin/env python3
# =============================================================================
# Date:     November, 2019
# Author:   Marcelo Villa P.
# Purpose:
# =============================================================================
from calendar import month_abbr
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from code.functions import beautify_ax, beautify_box, init_sns
from code.variables import face_color, edge_color

if __name__ == '__main__':
    # change directory
    os.chdir('../../data/csv')

    # read grouped fire pixels, ppt and evi data
    cols = ['fire_pixels', 'ppt', 'evi']
    df = pd.read_csv('groupby_area.csv', usecols=cols+['date'],
                     index_col='date', parse_dates=True)

    # initialize seaborn environment
    init_sns()

    fig, axs = plt.subplots(ncols=2, nrows=3, sharex='col', sharey='row')
    for i, col in enumerate(cols):
        # draw time series on the left (first) column
        sns.lineplot(df.index, df[col], ax=axs[i][0], color=edge_color,
                     linewidth=0.5)

        # get list of month initials
        months = list(map(lambda x: month_abbr[x][0], df.index.month.unique()))

        # draw boxplot on the right (second) column
        flierprops = dict(marker='o', markerfacecolor=edge_color, markersize=0.5)
        sns.boxplot(df.index.month, df[col], ax=axs[i][1], linewidth=0.5,
                    width=0.4, flierprops=flierprops)

        # set tick labels and beautify box
        axs[i][1].set_xticklabels(months)
        beautify_box(axs[i][1], edge_color, face_color)

    # beautify axes and hide x axis label
    for ax in axs.flat:
        beautify_ax(ax, edge_color, face_color)
        ax.xaxis.label.set_visible(False)

    labels = ['Fire pixels', 'Precipitation\n(mm/month)',
              'Enhanced Vegetation\nIndex']
    for i, label in enumerate(labels):
        axs[i][0].set_ylabel(label, labelpad=10, color=edge_color)

    # hide y axis in the second column
    for i in range(3):
        axs[i][1].yaxis.label.set_visible(False)

    # draw precipitation threshold lines and adjust y axis ticks
    for i in range(2):
        axs[1][i].axhline(100, xmin=0.045, xmax=0.955, linewidth=0.5,
                          color='r', linestyle=':')
        axs[1][i].set_yticks([0, 100, 200, 300])

    # adjust plot layout and save figure
    sns.despine(offset={'left': 5, 'bottom': 10}, trim=True)
    plt.subplots_adjust(wspace=0.4, hspace=1)
    plt.tight_layout()
    fn = '../../figures/graph/fire_ppt_evi_time_series.eps'
    plt.savefig(fn, format='eps', dpi=1200, facecolor=face_color)
