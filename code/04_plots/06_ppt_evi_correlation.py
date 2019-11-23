#!/usr/bin/env python3
# =============================================================================
# Date:     November, 2019
# Author:   Marcelo Villa P.
# Purpose:  Creates four scatter plots (including a regression line) showing
#           the correlation between both precipitation and enhanced vegetation
#           index (and their previous three month period measures) and the
#           quantity of fire pixels.
# =============================================================================
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from code.functions import beautify_ax, init_sns
from code.variables import edge_color, face_color

if __name__ == '__main__':
    # change directory
    os.chdir('../../data/csv')

    # read grouped fire pixel count, ppt and evi data
    df = pd.read_csv('groupby_area.csv')
    cols = [['ppt', 'evi'], ['ppt_prev', 'evi_prev']]
    labels = [
        ['Precipitation (mm/hr)', 'Enhanced Vegetation Index'],
        ['Precipitation (mm/hr) (prev. 3 months)',
         'Enhanced Vegetation Index (prev. 3 months)']
    ]

    # initialize seaborn environment and create figure
    init_sns()
    f, axs = plt.subplots(ncols=2, nrows=2, sharey='all', sharex='col')

    # define options for scatter and line
    scatter_kws = dict(marker='+', s=0.5)
    line_kws = dict(linewidth=0.75, color='r')

    for i, group in enumerate(cols):
        for j, col in enumerate(group):
            # create scatterplot with regression line using a lowess model
            sns.regplot(col, 'fire_pixels', df, ax=axs[i][j], color=edge_color,
                        scatter_kws=scatter_kws, line_kws=line_kws, lowess=True)

            # beautify and set x label
            beautify_ax(axs[i][j], edge_color, face_color)
            axs[i][j].set_xlabel(labels[i][j], labelpad=10, color=edge_color)

            # set x label on the first column and hide it on the second
            if j == 0:
                axs[i][j].set_ylabel('Fire pixels', labelpad=10, color=edge_color)
            else:
                axs[i][j].yaxis.label.set_visible(False)

            # set y lim
            axs[i][j].set_ylim([-100, 2000])

            # calculate correlation and write it on the plot
            corr = df['fire_pixels'].corr(df[col])
            text = rf'$r = {round(corr, 2)}$'
            axs[i][j].text(x=0.8, y=0.8, s=text, transform=axs[i][j].transAxes,
                           horizontalalignment='center', color=edge_color,
                           fontsize=8)

    for i in range(2):
        axs[i][0].set_xlim([0, 300])
        axs[i][0].set_xticks([0, 100, 200, 300])
        axs[i][1].set_xlim([0.30, 0.55])

    # adjust plot layout and save figure
    sns.despine(offset={'left': 5, 'bottom': 10}, trim=True)
    plt.subplots_adjust(wspace=0.4, hspace=1)
    plt.tight_layout()
    fn = '../../figures/graph/ppt_evi_correlation.eps'
    plt.savefig(fn, format='eps', dpi=1200, facecolor=face_color)
