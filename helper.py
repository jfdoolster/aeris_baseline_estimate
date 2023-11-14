import numpy as np

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

def new_dict_keyval(d: dict, key: str, val: any) -> dict:
    if key not in d:
        d[key] = val
    return d

def dataset_template(d: dict) -> dict:
    new_dict_keyval(d,'window_size', 3)
    new_dict_keyval(d,'segment_period', 120)
    new_dict_keyval(d,'gradient_filter_std_threshold', 0.2)
    new_dict_keyval(d,'outlier_filter_std_threshold', 1.0)
    new_dict_keyval(d,'polynomial_degree', 3)
    return d
