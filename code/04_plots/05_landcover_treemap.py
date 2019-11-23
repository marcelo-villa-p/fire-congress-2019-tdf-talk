#!/usr/bin/env python3
# =============================================================================
# Date:     April, 2019
# Author:   Marcelo Villa P.
# Purpose:  Creates a treemap showing the mean area of each landcover for all
#           the years.
# =============================================================================
import os

import matplotlib.pyplot as plt
import pandas as pd
import squarify

from code.variables import edge_color, face_color

if __name__ == '__main__':
    # change directory
    os.chdir('../../data/csv')

    # read data and get mean area per landcover
    df = pd.read_csv('landcover_normalized_area.csv')
    areas = df.groupby(['name'])['pixels'].mean()

    # define options for boxes and texts
    bar_kwargs = dict(edgecolor=edge_color, linewidth=0.5)
    text_kwargs = dict(color=edge_color, fontweight='normal')

    # create treemap
    ax = squarify.plot(sizes=areas.values, label=areas.index, color=face_color,
                       bar_kwargs=bar_kwargs, text_kwargs=text_kwargs, pad=True)
    plt.axis('off')

    # save figure
    fn = '../../figures/graph/landcover_treemap.eps'
    plt.savefig(fn, format='eps', dpi=1200, facecolor=face_color)
