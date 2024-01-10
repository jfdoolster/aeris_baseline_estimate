import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import *

def baseline_correction_plotter(df: pd.DataFrame, d: dict) -> plt.Figure:
    plt.rcParams['axes.grid'] = True
    plt.rcParams['lines.linewidth'] = 1.5
    plt.rcParams['legend.loc'] = "upper left"
    plt.rc('font', size=12)
    plt.rc('axes', titlesize=16)
    plt.rc('axes', labelsize=14)
    plt.rc('xtick', labelsize=12)
    plt.rc('ytick', labelsize=12)
    plt.rc('legend', fontsize=10)
    plt.rc('figure', titlesize=16)

    data_color = "C0"
    smooth_color = "C1"
    gradient_color="C2"
    #removed_color="C3"
    fitted_color="C4"

    fig = plt.figure()
    fig.set_size_inches(12, 8)

    CVAR='\chi'
    rawdata_str = rf'${CVAR}$'
    smoothed_str = fr"$\widetilde {CVAR}$"+rf"$\,(n = {d['window_size']:d})$"
    gradfilt_str = rf"$\nabla {CVAR}<\pm{d['gradient_filter_std_threshold']:3.2f}\sigma$"
    meanfilt_str = rf"$\widetilde {CVAR}$"+rf"$< \pm {d['outlier_filter_std_threshold']:3.2f}\sigma$"
    baseline_str = rf"${CVAR}_{0}$"+f" deg({d['polynomial_degree']})"

    # plot rawdata and smoothed data
    ax0 = fig.add_subplot(221)
    ax0.plot(df['seconds'], df[d['rawdata_colname']], color=data_color, \
        label=rawdata_str)
    ax0.plot(df['seconds'], df['segment_data'], color=smooth_color, \
        label=smoothed_str)

    # plot gradient of rawdata and unfiltered samples
    ax1 = fig.add_subplot(222, sharex=ax0)
    ax1.plot(df['seconds'], df['segment_gradient'], color=gradient_color, label=fr"$\nabla {CVAR}$")
    #vertical_max = (d['gradient_filter_std_threshold'] * np.std(df['segment_gradient'])) * 2.00
    vertical_max = max(abs(df[df['gradient_mask']]['segment_gradient']).dropna())
    ax1.plot(df[df['gradient_mask']]['seconds'], df[df['gradient_mask']]['segment_gradient'], \
        ls='None', marker='o', color=fitted_color, label=gradfilt_str)

    ax1.set_ylim(-vertical_max*2.00, vertical_max*2.00)

    def y_fmt(x, y):
        #return f"${x/np.std(df['segment_gradient']):.1f}\,$"+"$\sigma$"
        return f"${(d['gradient_filter_std_threshold']*x/vertical_max):.1f}\,$"+"$\sigma$"

    ax1.yaxis.set_major_locator(MultipleLocator(vertical_max))
    ax1.yaxis.set_major_formatter(FuncFormatter(y_fmt))

    # plot gradient of rawdata and unfiltered samples
    ax2 = fig.add_subplot(223, sharex=ax0, sharey=ax0)
    ax2.plot(df['seconds'], df['segment_data'], color=smooth_color, \
        label=smoothed_str)
    outfilt = df[df['outlier_mask']]
    ax2.plot(outfilt['seconds'], outfilt['segment_data'], ls='None', marker='o', color=fitted_color, \
        label=meanfilt_str)


    ax3 = fig.add_subplot(224, sharex=ax0, sharey=ax0)
    ax3.plot(df['seconds'], df[d['rawdata_colname']], color=data_color, \
        label=rawdata_str)
    ax3.plot(df['seconds'], df[f"{d['rawdata_colname']}_baseline"], color=fitted_color,
        label=baseline_str, lw=3)

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

    for ax in [ax2]:
        std = outfilt['segment_data'].dropna().std()
        avg = df['segment_data'].dropna().mean()
        if d['rawdata_colname'] == 'CH4' and max(df[d['rawdata_colname']]) > 100:
            ax.set_ylim(top = 100.0)
        if d['rawdata_colname'] == 'C2H6' and max(df[d['rawdata_colname']]) > 500:
            ax.set_ylim(top = 500.0)
        #ax.set_ylim(bottom = min(df['segment_data'].dropna()))

    lbls = ['A', 'B', 'C', 'D']
    for i, ax in enumerate([ax0, ax1, ax2, ax3]):
        ax.text(0.90, 0.95, lbls[i], fontsize=20, transform=ax.transAxes, va='top')

    fig.tight_layout()
    return fig