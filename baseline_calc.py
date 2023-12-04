import numpy as np
import pandas as pd
from polynomial import polynomial_regression
import baseline_utils as utils

def baseline_correction(xdata: np.ndarray, ydata: np.ndarray, d: dict):
    df = pd.DataFrame() # initialize output dataframe

    smoothed=moving_average(ydata, n=d['window_size'])
    #print(f"{d['rawdata_colname']} {d['window_size']}-point smoothed")

    # split smoothed data into segments with approximately equal periods
    segments, num_segs = segmenting_filter(smoothed, period=d['segment_period'])
    #print(f"split into {num_segs} segments with period ~{d['segment_period']} sec")

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
            d['rawdata_colname']: ydata,
            'smoothed_data': smoothed,
        }), df], axis=1)

    # polynomial regression on filtered data
    background_orig = df[df['outlier_mask']][d['rawdata_colname']]
    background_secs = df[df['outlier_mask']]['seconds']
    background_data = df[df['outlier_mask']]['segment_data']
    betas, background_yhat = polynomial_regression(np.array(background_secs), np.array(background_data),
                               power = d['polynomial_degree'])

    # use filtered polynomial coefs on original data
    x_lists = []
    for i in range(0, d['polynomial_degree']+1):
        x_lists.append(np.array(xdata)**i)
    x_mat = np.vstack(x_lists)
    x_mat = np.transpose(x_mat)
    yhat = np.matmul(x_mat, betas).flatten()

    yadj = ydata - yhat
    yerr = [y if df.loc[i,'outlier_mask'] else np.nan for i,y in enumerate(yadj)]

    df = pd.concat([df,
        pd.DataFrame.from_dict({
            f"{d['rawdata_colname']}_baseline": yhat,
            f"{d['rawdata_colname']}_baseline_error": yerr,
            f"{d['rawdata_colname']}_adjusted": yadj,
        })], axis=1)

    return df


def baseline_estimate_template(rawdata_colname: str | int, d=dict({})) -> dict:
    utils.new_dict_keyval(d,'rawdata_colname', rawdata_colname)
    utils.new_dict_keyval(d,'timestamp_colname', 'Timestamp')
    utils.new_dict_keyval(d,'window_size', 3)
    utils.new_dict_keyval(d,'segment_period', 120)
    utils.new_dict_keyval(d,'gradient_filter_std_threshold', 0.2)
    utils.new_dict_keyval(d,'outlier_filter_std_threshold', 1.0)
    utils.new_dict_keyval(d,'polynomial_degree', 3)
    utils.new_dict_keyval(d,'hard_outlier_threshold', 5000.0)
    return d

def moving_average(arr: np.ndarray, n=3):
    ret = np.cumsum(arr, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    nan_arr = np.empty((n-1,))
    nan_arr[:] = np.nan
    return np.hstack((nan_arr, np.array(ret[n-1:]/n)))

def gradient_filter(arr: np.ndarray, std_cutoff=1.0) -> (np.ndarray, np.ndarray):
    grad = np.gradient(arr)
    avg, std = np.nanmean(grad), np.nanstd(grad)
    cutoff = std_cutoff * std
    mask = (grad > (avg-cutoff)) & (grad < (avg+cutoff))
    return mask, grad

def segmenting_filter(arr: np.ndarray, dt=1, period = 120) -> (list, int):
    splits = (len(arr) * dt) / period
    n = int(round(splits))
    return list(segment_array(list(arr),n)), n

def segment_array(arr: list, n: int) -> list:
    k, m = divmod(len(arr), n)
    return list(np.array(arr[i*k+min(i, m):(i+1)*k+min(i+1, m)]) for i in range(n))

def dataset_template(d: dict) -> dict:
    # todo: remove function?
    utils.new_dict_keyval(d,'window_size', 3)
    utils.new_dict_keyval(d,'segment_period', 120)
    utils.new_dict_keyval(d,'gradient_filter_std_threshold', 0.2)
    utils.new_dict_keyval(d,'outlier_filter_std_threshold', 1.0)
    utils.new_dict_keyval(d,'polynomial_degree', 3)
    return d
