

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
    new_dict_keyval(d, 'start_time', '00:00:00')
    new_dict_keyval(d, 'start_time', '23:59:59')
    return d

if __name__=="__main__":

    import numpy as np
    import pandas as pd

    from polynomial import polynomaial_regression
    from helper import moving_average, segmenting_filter, gradient_filter
    from custom_plots import set_custom_rcparams

    import matplotlib.pyplot as plt
    plt.rcParams['axes.grid'] = True


    df1 = pd.DataFrame() # initialize output dataframe

    rawdata_path = 'data/20230419-Hobbs/flight.csv'
    timestamp_colname = 'Timestamp'
    rawdata_colname = "CH4"

    df0 = pd.read_csv(rawdata_path, parse_dates=['Timestamp'])
    xdata = np.array(df0[timestamp_colname] - df0[timestamp_colname].min()) / np.timedelta64(1,'s')
    ydata = np.array(df0[rawdata_colname])
    dset_info = dataset_template({})

    #window_size = dset_info['window_size']
    #grad_filt_cutoff = dset_info['gradient_filter_std_threshold']
    #segment_period_sec = dset_info['segment_period']

    smoothed=moving_average(ydata, n=dset_info['window_size'])
    print(f"{rawdata_colname} {dset_info['window_size']}-point smoothed")

    # split smoothed data into segments with approximately equal periods
    segments, num_segs = segmenting_filter(smoothed, period=dset_info['segment_period'])
    print(f"split into {num_segs} segments with period ~{dset_info['segment_period']} sec")

    # loop through segmented (smoothed) data
    for i, segment in enumerate(segments):
        seg_label = np.array([i] * len(segment))

        seg_gmask, seg_gradient = gradient_filter(segment, std_cutoff=dset_info['gradient_filter_std_threshold'])

        # summary statistics for gradient-filtered segment
        # set cuttoff values for remaining outliers
        seg_gavg, seg_gstd = np.mean(segment[seg_gmask]), np.std(segment[seg_gmask])
        topcut = seg_gavg + (seg_gstd * dset_info['outlier_filter_std_threshold']),
        botcut = seg_gavg - (seg_gstd * dset_info['outlier_filter_std_threshold'])

        # final mask for background data
        seg_amask = seg_gmask & ((segment > botcut) & (segment < topcut))

        tmp = {
            'segment_data': segment,
            "segment_label": seg_label,
            "segment_gradient": seg_gradient,
            "gradient_mask": seg_gmask,
            "outlier_mask": seg_amask,
        }
        df1 = pd.concat([df1, pd.DataFrame.from_dict(tmp)], ignore_index=True)

    df1 = pd.concat([
        pd.DataFrame.from_dict({
            timestamp_colname: df0[timestamp_colname],
            'seconds': xdata,
            rawdata_colname: ydata,
            'smoothed_data': smoothed,
        }), df1], axis=1)

    betas, _ = polynomaial_regression(np.array(df1[df1['outlier_mask']]['seconds']),
                               np.array(df1[df1['outlier_mask']]['segment_data']),
                               power = dset_info['polynomial_degree'])

    x_lists = []
    for i in range(0, dset_info['polynomial_degree']+1):
        x_lists.append(np.array(xdata)**i)
    x_mat = np.vstack(x_lists)
    x_mat = np.transpose(x_mat)

    set_custom_rcparams()

    data_color = "C0"
    smooth_color = "C1"
    gradient_color="C2"
    removed_color="C3"
    fitted_color="C4"

    fig = plt.figure()
    fig.set_size_inches(12, 8)
    ax0 = fig.add_subplot(221)
    ax0.plot(df1['seconds'], df1[rawdata_colname], color=data_color)
    ax0.plot(df1['seconds'], df1['segment_data'], color=smooth_color)

    ax1 = fig.add_subplot(222, sharex=ax0)
    ax1.plot(df1['seconds'], df1['segment_gradient'], color=gradient_color)
    vertical_max = (dset_info['gradient_filter_std_threshold'] + 0.5 ) * np.std(df1['segment_gradient'])
    gradfilt = df1[df1['gradient_mask']]
    ax1.plot(gradfilt['seconds'], gradfilt['segment_gradient'], ls='None', marker='o', color=fitted_color)
    ax1.set_ylim(-vertical_max, vertical_max)

    ax2 = fig.add_subplot(223, sharex=ax0, sharey=ax0)
    ax2.plot(df1['seconds'], df1['segment_data'], color=smooth_color)
    #outliers = df1[df1['gradient_mask'] & df1['outlier_mask'] == False]
    #ax2.plot(outliers['seconds'], outliers['segment_data'], ls='None', marker='o', color=removed_color)
    outfilt = df1[df1['outlier_mask']]
    ax2.plot(outfilt['seconds'], outfilt['segment_data'], ls='None', marker='o', color=fitted_color)


    yhat = np.matmul(x_mat, betas)

    ax3 = fig.add_subplot(224, sharex=ax0, sharey=ax0)
    ax3.plot(df1['seconds'], df1[rawdata_colname], color=data_color)
    ax3.plot(df1['seconds'], yhat, color=fitted_color)


    for ax in [ax2, ax3]:
        ax.set_xlabel("seconds")

    for ax in [ax0, ax2, ax3]:
        if rawdata_colname in ['C2H6']:
            ax.set_ylabel(f"{rawdata_colname} (ppb)")
            continue
        ax.set_ylabel(f"{rawdata_colname} (ppm)")

    for ax in [ax1]:
        ax.set_ylabel(r"$\nabla$"+f"{rawdata_colname}")

    fig.tight_layout()
    plt.show()

