import numpy as np
import pandas as pd

from polynomial import polynomial_regression
from helper import moving_average, segmenting_filter, gradient_filter, dataset_template


def baseline_correction(xdata: np.ndarray, ydata: np.ndarray, d: dict):
    df = pd.DataFrame() # initialize output dataframe

    smoothed=moving_average(ydata, n=d['window_size'])
    print(f"{d['rawdata_colname']} {d['window_size']}-point smoothed")

    # split smoothed data into segments with approximately equal periods
    segments, num_segs = segmenting_filter(smoothed, period=d['segment_period'])
    print(f"split into {num_segs} segments with period ~{d['segment_period']} sec")

    # loop through segmented (smoothed) data
    for i, segment in enumerate(segments):
        seg_label = np.array([i] * len(segment))

        seg_gmask, seg_gradient = gradient_filter(segment, std_cutoff=d['gradient_filter_std_threshold'])

        # summary statistics for gradient-filtered segment
        # set cuttoff values for remaining outliers
        seg_gavg, seg_gstd = np.mean(segment[seg_gmask]), np.std(segment[seg_gmask])
        topcut = seg_gavg + (seg_gstd * d['outlier_filter_std_threshold']),
        botcut = seg_gavg - (seg_gstd * d['outlier_filter_std_threshold'])

        # final mask for background data
        seg_amask = seg_gmask & ((segment > botcut) & (segment < topcut))

        tmp = {
            'segment_data': segment,
            "segment_label": seg_label,
            "segment_gradient": seg_gradient,
            "gradient_mask": seg_gmask,
            "outlier_mask": seg_amask,
        }
        df = pd.concat([df, pd.DataFrame.from_dict(tmp)], ignore_index=True)

    df = pd.concat([
        pd.DataFrame.from_dict({
            'seconds': xdata,
            d['rawdata_colname']: ydata,
            'smoothed_data': smoothed,
        }), df], axis=1)

    # polynomial regression on filtered data
    background_secs = df[df['outlier_mask']]['seconds']
    background_data = df[df['outlier_mask']]['segment_data']
    betas, _ = polynomial_regression(np.array(background_secs), np.array(background_data),
                               power = d['polynomial_degree'])

    # use filtered polynomial coefs on original data
    x_lists = []
    for i in range(0, d['polynomial_degree']+1):
        x_lists.append(np.array(xdata)**i)
    x_mat = np.vstack(x_lists)
    x_mat = np.transpose(x_mat)
    yhat = np.matmul(x_mat, betas).flatten()

    df = pd.concat([df,
        pd.DataFrame.from_dict({
            f"{d['rawdata_colname']}_baseline": yhat,
        })], axis=1)

    return df

if __name__=="__main__":

    import argparse
    import matplotlib.pyplot as plt
    from custom_plots import baseline_correction_plotter

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', required=True, type=str,
        help='path to csv datafile with Timestamp and CH4 (or C2H6) labelled data columns')
    args = parser.parse_args()
    argdict = vars(args)

    rawdata_path = argdict['file']

    dset_info = dataset_template({
        'timestamp_colname': 'Timestamp',     # datatime column name
        'rawdata_colname': 'CH4',             # data column name
        'window_size': 3,                     # smoothing window size
        'segment_period': 120,                # approx period for segments in sec
        'gradient_filter_std_threshold': 0.2, # gradient filter std cuttoff
        'outlier_filter_std_threshold': 1.0,  # outlier (mean) filter std cuttoff
        'polynomial_degree': 3,               # polynomial fit order
    })

    df0 = pd.read_csv(rawdata_path, parse_dates=['Timestamp'])
    seconds = np.array(df0[dset_info['timestamp_colname']] -
                     df0[dset_info['timestamp_colname']].min()) / np.timedelta64(1,'s')

    # read and process METHANE data only
    dset_info['rawdata_colname'] = 'CH4'
    rawdata = np.array(df0[dset_info['rawdata_colname']])
    df1 = baseline_correction(seconds, rawdata, dset_info)
    df1 = pd.concat([df0[dset_info['timestamp_colname']], df1], axis=1)
    print(df1)
    baseline_correction_plotter(df1, dset_info)

    # read and process ETHANE data only
    dset_info['rawdata_colname'] = 'C2H6'
    dset_info['polynomial_degree'] = 4
    rawdata = np.array(df0[dset_info['rawdata_colname']])
    df2 = baseline_correction(seconds, rawdata, dset_info)
    df2 = pd.concat([df0[dset_info['timestamp_colname']], df2], axis=1)
    print(df2)
    baseline_correction_plotter(df2, dset_info)

    plt.show()

