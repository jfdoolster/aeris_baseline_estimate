import pandas as pd
import numpy as np
import matplotlib.pyplot as plt




def baseline_correction_plotter(df: pd.DataFrame, d: dict) -> plt.Figure:
    set_custom_rcparams()

    data_color = "C0"
    smooth_color = "C1"
    gradient_color="C2"
    #removed_color="C3"
    fitted_color="C4"

    fig = plt.figure()
    fig.set_size_inches(12, 8)

    # plot rawdata and smoothed data
    ax0 = fig.add_subplot(221)
    ax0.plot(df['seconds'], df[d['rawdata_colname']], color=data_color, \
        label=r'$\chi$')
    ax0.plot(df['seconds'], df['segment_data'], color=smooth_color, \
        label=r"$\tilde{\chi}$"+rf"$(n = {d['window_size']:d})$")

    # plot gradient of rawdata and unfiltered samples
    ax1 = fig.add_subplot(222, sharex=ax0)
    ax1.plot(df['seconds'], df['segment_gradient'], color=gradient_color, label=r"$\nabla\chi$")
    vertical_max = (d['gradient_filter_std_threshold'] + 0.5 ) * np.std(df['segment_gradient'])
    ax1.plot(df[df['gradient_mask']]['seconds'], df[df['gradient_mask']]['segment_gradient'], \
        ls='None', marker='o', color=fitted_color, label=rf"$\nabla\chi < \pm {d['gradient_filter_std_threshold']} \sigma$")
    ax1.set_ylim(-vertical_max, vertical_max)

    # plot gradient of rawdata and unfiltered samples
    ax2 = fig.add_subplot(223, sharex=ax0, sharey=ax0)
    ax2.plot(df['seconds'], df['segment_data'], color=smooth_color, \
        label=r"$\tilde{\chi}$"+rf"$(n = {d['window_size']:d})$")
    outfilt = df[df['outlier_mask']]
    ax2.plot(outfilt['seconds'], outfilt['segment_data'], ls='None', marker='o', color=fitted_color, \
        label=r"$\tilde{\chi}$"+rf"$< \pm {d['window_size']:d}\sigma$")


    ax3 = fig.add_subplot(224, sharex=ax0, sharey=ax0)
    ax3.plot(df['seconds'], df[d['rawdata_colname']], color=data_color, \
        label=r'$\chi$')
    ax3.plot(df['seconds'], df[f"{d['rawdata_colname']}_baseline"], color=fitted_color,
        label=r'$\chi_{0}$')

    for ax in [ax2, ax3]:
        ax.set_xlabel("seconds")

    for ax in [ax0, ax2, ax3]:
        ax.legend()
        if d['rawdata_colname'] in ['C2H6']:
            ax.set_ylabel(f"{d['rawdata_colname']} (ppb)")
            continue
        ax.set_ylabel(f"{d['rawdata_colname']} (ppm)")

    for ax in [ax1]:
        ax.legend()
        ax.set_ylabel(r"$\nabla$"+f"{d['rawdata_colname']}")

    fig.tight_layout()
    return fig

def set_custom_rcparams(grid=True):
    plt.rcParams['axes.grid'] = grid
    plt.rcParams['lines.linewidth'] = 1.5
    plt.rcParams['legend.loc'] = "upper left"
    plt.rc('font', size=12)
    plt.rc('axes', titlesize=16)
    plt.rc('axes', labelsize=14)
    plt.rc('xtick', labelsize=12)
    plt.rc('ytick', labelsize=12)
    plt.rc('legend', fontsize=10)
    plt.rc('figure', titlesize=16)
