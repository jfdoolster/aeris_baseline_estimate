import numpy as np

def moving_average(arr: np.ndarray, n=3):
    ret = np.cumsum(arr, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    nan_arr = np.empty((n-1,))
    nan_arr[:] = np.nan
    return np.hstack((nan_arr, np.array(ret[n-1:]/n)))

def gradient_filter(arr: np.ndarray, std_cutoff=0.2):
    ret = np.gradient(arr)
    avg, std = np.nanmean(ret), np.nanstd(ret)
    cutoff = std_cutoff * std
    mask = (ret > (avg-cutoff)) & (ret < (avg+cutoff))
    return mask

def segmenting_filter(arr:np.ndarray):
    split_arr, split_num = [arr], 1
    return split_arr, split_num


if __name__=="__main__":

    xdata=np.linspace(0,100,75)

    smoothed=moving_average(xdata)
    print(len(smoothed))
    grad_mask = gradient_filter(smoothed)
    print(len(grad_mask))

    #mask bad values first! (then split)

    segments, num_segs = segmenting_filter(smoothed)
    for segment in segments:
        print(segment)






