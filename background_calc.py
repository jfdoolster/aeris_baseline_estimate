import pandas as pd
import numpy as np
from polynomial import polynomial_regression
from background_config import Baseline_Config

def baseline_estimate(xdata: np.ndarray, ydata: np.ndarray, b: Baseline_Config):
    # initialize output dataframe
    df = pd.DataFrame()

    smoothed = moving_average(ydata, b.window_size)

    # split smoothed data into segments with approximately equal periods
    segments, num_segs = segmenting_filter(smoothed, period=b.segment_period)

    # loop through segmented (smoothed) data
    for i, segment in enumerate(segments):
        seg_label = np.array([i] * len(segment))

        seg_gmask, seg_gradient = gradient_filter(segment, std_cutoff=b.gradient_filter_std_threshold)

        # summary statistics for gradient-filtered segment
        # set cuttoff values for remaining outliers
        seg_gavg, seg_gstd = np.mean(segment[seg_gmask]), np.std(segment[seg_gmask])
        topcut = seg_gavg + (seg_gstd * b.outlier_filter_std_threshold),
        botcut = seg_gavg - (seg_gstd * b.outlier_filter_std_threshold)

        # final mask for background data
        seg_amask = (seg_gmask & (segment > botcut)) & \
            ((segment < topcut) & (segment < d['hard_outlier_threshold']))

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
            b.rawdata_colname: ydata,
            'smoothed_data': smoothed,
        }), df], axis=1)

    # polynomial regression on filtered data
    background_orig = df[df['outlier_mask']][b.rawdata_colname]
    background_secs = df[df['outlier_mask']]['seconds']
    background_data = df[df['outlier_mask']]['segment_data']
    betas, background_yhat = polynomial_regression(np.array(background_secs), np.array(background_data),
                               power = b.polynomial_degree)

    # use filtered polynomial coefs on original data
    x_lists = []
    for i in range(0, b.polynomial_degree+1):
        x_lists.append(np.array(xdata)**i)
    x_mat = np.vstack(x_lists)
    x_mat = np.transpose(x_mat)
    yhat = np.matmul(x_mat, betas).flatten()

    yadj = ydata - yhat
    yerr = [y if df.loc[i,'outlier_mask'] else np.nan for i,y in enumerate(yadj)]

    df = pd.concat([df,
        pd.DataFrame.from_dict({
            f"{b.rawdata_colname}_baseline": yhat,
            f"{b.rawdata_colname}_baseline_error": yerr,
            f"{b.rawdata_colname}_adjusted": yadj,
        })], axis=1)

    return df

def moving_average(arr: np.ndarray, n=3):
    ret = np.cumsum(arr, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    nan_arr = np.empty((n-1,))
    nan_arr[:] = np.nan
    return np.hstack((nan_arr, np.array(ret[n-1:]/n)))

def gradient_filter(arr: np.ndarray, std_cutoff=1.0) -> tuple[np.ndarray, np.ndarray]:
    grad = np.gradient(arr)
    avg, std = np.nanmean(grad), np.nanstd(grad)
    cutoff = std_cutoff * std
    mask = (grad > (avg-cutoff)) & (grad < (avg+cutoff))
    return mask, grad

def segmenting_filter(arr: np.ndarray, dt=1, period = 120) -> tuple[list, int]:
    splits = (len(arr) * dt) / period
    n = int(round(splits))
    return list(segment_array(list(arr),n)), n

def segment_array(arr: list, n: int) -> list:
    k, m = divmod(len(arr), n)
    return list(np.array(arr[i*k+min(i, m):(i+1)*k+min(i+1, m)]) for i in range(n))

