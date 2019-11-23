#!/usr/bin/env python3
# =============================================================================
# Date:     November, 2019
# Author:   Marcelo Villa P.
# Purpose:  Plots fire pixel probability as a function of both land cover and
#           distance to the nearest forest pixel.
# =============================================================================
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from code.functions import beautify_ax, init_sns
from code.variables import edge_color, face_color, landcovers

if __name__ == '__main__':
    # change directory
    os.chdir('../../data/csv')

    # read landcover and distance per pixel data
    df = pd.read_csv('landcover_and_forest_proximity_per_pixel.csv')
    df = df[df['lc_name'] != 'Forest']

    # init seaborn environment
    init_sns()

    # define line options and subplot titles
    line_kws = dict(color=edge_color, linewidth=0.75)
    titles = sorted(list(landcovers.values())[1:])

    # create logistic regression plot for forest distance and landcover type
    g = sns.lmplot(x="forest_distance", y="is_fire_pixel", col="lc_name",
                   hue="lc_name", data=df, scatter=False, logistic=True,
                   line_kws=line_kws, col_order=titles)

    for i, ax in enumerate(g.axes.flatten()):
        # set x label and subplot title
        ax.set_xlabel('Distance to nearest forest (pixels)', labelpad=10,
                      color=edge_color)
        ax.set_title(titles[i], color=edge_color)

        # beautify ax and change y lim
        beautify_ax(ax, edge_color, face_color)
        ax.set_ylim([0, 1])

    # change y label in first subplot
    g.axes[0][0].set_ylabel('Fire pixel probability', labelpad=10,
                            color=edge_color)

    # adjust plot and save figure
    sns.despine(offset={'left': 5, 'bottom': 10}, trim=True)
    plt.subplots_adjust(wspace=0.2)
    plt.tight_layout()
    fn = '../../figures/graph/distance_by_landcover_reg.pdf'
    plt.savefig(fn, format='pdf', dpi=1200, facecolor=face_color)
