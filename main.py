import numpy as np
from polynomial import slope_intercept

def moving_average(arr: np.ndarray, n=3):
    ret = np.cumsum(arr, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    nan_arr = np.empty((n-1,))
    nan_arr[:] = np.nan
    return np.hstack((nan_arr, np.array(ret[n-1:]/n)))

def gradient_filter(arr: np.ndarray, std_cutoff=1.0) -> (np.ndarray, np.ndarray):
    ret = np.gradient(arr)
    avg, std = np.nanmean(ret), np.nanstd(ret)
    cutoff = std_cutoff * std
    mask = (ret > (avg-cutoff)) & (ret < (avg+cutoff))
    return mask, ret

def segmenting_filter(arr: np.ndarray, dt=1, segment_period_sec = 120) -> (list, int):
    splits = (len(arr) * dt) / segment_period_sec
    n = int(round(splits))
    return list(segment_array(list(arr),n)), n

def segment_array(arr: list, n: int) -> list:
    k, m = divmod(len(arr), n)
    return list(np.array(arr[i*k+min(i, m):(i+1)*k+min(i+1, m)]) for i in range(n))


if __name__=="__main__":

    import pandas as pd
    import matplotlib.pyplot as plt

    df0 = pd.read_csv("data/flight.csv", parse_dates=['Timestamp'])
    xdata = np.array(df0['Timestamp'] - df0['Timestamp'].min())/np.timedelta64(1,'s')
    ydata = np.array(df0['CH4'])

    smoothed=moving_average(ydata, n=3)

    df1 = pd.DataFrame()

    grad_filt_cutoff = 0.2
    avg_filt_cutoff = 1.0
    segments, num_segs = segmenting_filter(smoothed, segment_period_sec=120)
    for i, segment in enumerate(segments):
        seg_label = np.array([i] * len(segment))
        seg_gmask,seg_gradient = gradient_filter(segment, std_cutoff=grad_filt_cutoff)
        seg_gavg, seg_gstd = np.mean(segment[seg_gmask]), np.std(segment[seg_gmask])
        topcut, botcut = seg_gavg+(seg_gstd*avg_filt_cutoff), seg_gavg-(seg_gstd*avg_filt_cutoff)
        seg_amask = seg_gmask & ((segment > botcut) & (segment < topcut))

        tmp = {
            "segment_data": segment,
            "segment_label": seg_label,
            "segment_gradient": seg_gradient,
            "gradient_mask": seg_gmask,
            "outlier_mask": seg_amask,
        }
        df1 = pd.concat([df1, pd.DataFrame.from_dict(tmp)], ignore_index=True)

    df1 = pd.concat([
        pd.DataFrame.from_dict({
            'timestamp': df0['Timestamp'],
            'seconds': xdata,
            'original_data': ydata,
            'smoothed_data': smoothed,
        }), df1], axis=1)

    fig = plt.figure()
    ax0 = fig.add_subplot(221)
    ax0.plot(df1['seconds'], df1['original_data'])
    ax0.plot(df1['seconds'], df1['segment_data'])

    ax1 = fig.add_subplot(222)
    ax1.plot(df1['seconds'], df1['segment_gradient'])
    gradfilt = df1[df1['gradient_mask'] == False]
    ax1.plot(gradfilt['seconds'], gradfilt['segment_gradient'], ls='None', marker='o')

    ax2 = fig.add_subplot(223)
    ax2.plot(df1['seconds'], df1['segment_data'])
    outfilt = df1[df1['outlier_mask']]
    ax2.plot(outfilt['seconds'], outfilt['segment_data'], ls='None', marker='o')

    degree = 2
    betas, _ = slope_intercept(np.array(outfilt['seconds']),
                               np.array(outfilt['segment_data']),
                               power = degree)

    x_lists = []
    for i in range(0,degree+1):
        x_lists.append(np.array(df1['seconds'])**i)
    x_mat = np.vstack(x_lists)
    x_mat = np.transpose(x_mat)

    yhat = np.matmul(x_mat, betas)

    ax3 = fig.add_subplot(224)
    ax3.plot(df1['seconds'], df1['original_data'])
    ax3.plot(df1['seconds'], yhat)

    plt.show()


    #print(len(xdata))
    #print(len(ydata))
    #print(len(smoothed))
    #print(len(gradmask_col))
    #print(len(segment_col))








