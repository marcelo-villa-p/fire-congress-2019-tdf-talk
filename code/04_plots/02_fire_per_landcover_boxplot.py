#!/usr/bin/env python3
# =============================================================================
# Date:     November, 2019
# Author:   Marcelo Villa P.
# Purpose:  Creates a boxplot showing fire pixels proportion for each landcover
#           category.
# =============================================================================
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from code.functions import beautify_ax, beautify_box, init_sns
from code.variables import edge_color, face_color, landcovers

if __name__ == '__main__':
    # change directory
    os.chdir('../../data/csv')

    # read fire pixels proportion per landcover data
    df = pd.read_csv('fire_pixels_proportion_per_landcover.csv')

    # initialize seaborn environment
    init_sns()

    # create empty figure and add a boxplot
    f, ax = plt.subplots(1, 1)
    flierprops = dict(marker='o', markerfacecolor=edge_color, markersize=0.5)
    sns.boxplot(x="variable", y="value", data=pd.melt(df), ax=ax,
                flierprops=flierprops, linewidth=0.5, width=0.3)

    # set x tick labels, y label and hide x axis label
    ax.set_xticklabels(landcovers.values())
    ax.set_ylabel('Fire pixels proportion', labelpad=20, color=edge_color)
    ax.xaxis.label.set_visible(False)

    # beautify figure
    beautify_ax(ax, edge_color, face_color)
    beautify_box(ax, edge_color, face_color)

    # adjust plot layout and save figure
    sns.despine(offset={'left': 5, 'bottom': 10}, trim=True)
    plt.subplots_adjust(wspace=0.4, hspace=1)
    plt.tight_layout()
    fn = '../../figures/graph/fire_per_landcover_boxplot.eps'
    plt.savefig(fn, format='eps', dpi=1200, facecolor=face_color)
