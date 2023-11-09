import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def baseline_correction_plotter(df: pd.DataFrame, d: dict):
    set_custom_rcparams()

    data_color = "C0"
    smooth_color = "C1"
    gradient_color="C2"
    removed_color="C3"
    fitted_color="C4"

    fig = plt.figure()
    fig.set_size_inches(12, 8)

    # plot rawdata and smoothed data
    ax0 = fig.add_subplot(221)
    ax0.plot(df['seconds'], df[d['rawdata_colname']], color=data_color)
    ax0.plot(df['seconds'], df['segment_data'], color=smooth_color)

    # plot gradient of rawdata and unfiltered samples
    ax1 = fig.add_subplot(222, sharex=ax0)
    ax1.plot(df['seconds'], df['segment_gradient'], color=gradient_color)
    vertical_max = (d['gradient_filter_std_threshold'] + 0.5 ) * np.std(df['segment_gradient'])
    ax1.plot(df[df['gradient_mask']]['seconds'], df[df['gradient_mask']]['segment_gradient'], ls='None', marker='o', color=fitted_color)
    ax1.set_ylim(-vertical_max, vertical_max)

    # plot gradient of rawdata and unfiltered samples
    ax2 = fig.add_subplot(223, sharex=ax0, sharey=ax0)
    ax2.plot(df['seconds'], df['segment_data'], color=smooth_color)
    outfilt = df[df['outlier_mask']]
    ax2.plot(outfilt['seconds'], outfilt['segment_data'], ls='None', marker='o', color=fitted_color)


    ax3 = fig.add_subplot(224, sharex=ax0, sharey=ax0)
    ax3.plot(df['seconds'], df[d['rawdata_colname']], color=data_color)
    ax3.plot(df['seconds'], df[f"{d['rawdata_colname']}_baseline"], color=fitted_color)

    for ax in [ax2, ax3]:
        ax.set_xlabel("seconds")

    for ax in [ax0, ax2, ax3]:
        if d['rawdata_colname'] in ['C2H6']:
            ax.set_ylabel(f"{d['rawdata_colname']} (ppb)")
            continue
        ax.set_ylabel(f"{d['rawdata_colname']} (ppm)")

    for ax in [ax1]:
        ax.set_ylabel(r"$\nabla$"+f"{d['rawdata_colname']}")

    fig.tight_layout()

def set_custom_rcparams(grid=True):
    """
    custom rcparams
    """
    plt.rcParams['axes.grid'] = grid
    plt.rcParams['lines.linewidth'] = 1.5
    plt.rcParams['legend.loc'] = "upper left"
    # Set the default text font size
    plt.rc('font', size=12)
    # Set the axes title font size
    plt.rc('axes', titlesize=16)
    # Set the axes labels font size
    plt.rc('axes', labelsize=14)
    # Set the font size for x tick labels
    plt.rc('xtick', labelsize=12)
    # Set the font size for y tick labels
    plt.rc('ytick', labelsize=12)
    # Set the legend font size
    plt.rc('legend', fontsize=10)
    # Set the font size of the figure title
    plt.rc('figure', titlesize=16)
