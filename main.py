
if __name__=="__main__":

    import argparse
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from baseline_plotter import baseline_correction_plotter
    from baseline_calc import baseline_estimate_template, baseline_correction

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', required=True, type=str,
        help='path to csv datafile with Timestamp and CH4 (or C2H6) labelled data columns')
    args = parser.parse_args()
    argdict = vars(args)

    rawdata_path = argdict['file']

    ch4_dset_info  = baseline_estimate_template(rawdata_colname="CH4")
    c2h6_dset_info = baseline_estimate_template(rawdata_colname="C2H6", d={'polynomial_degree': 4})

    df0 = pd.read_csv(rawdata_path, parse_dates=['Timestamp'])
    aeris_mask = (df0['CH4'].notna() & df0['C2H6'].notna()) & (df0['Sts'] > 0)

    # read and process METHANE data only
    seconds = np.array(df0.loc[aeris_mask,'Seconds'])
    rawdata = np.array(df0.loc[aeris_mask, ch4_dset_info['rawdata_colname']])
    df_ch4 = baseline_correction(seconds, rawdata, ch4_dset_info)
    df_ch4.index = df0.loc[aeris_mask,:].index
    df_ch4.loc[aeris_mask,'Timestamp'] = df0.loc[aeris_mask,'Timestamp']
    baseline_correction_plotter(df_ch4, ch4_dset_info)

    # read and process ETHANE data only
    seconds = np.array(df0.loc[aeris_mask,'Seconds'])
    rawdata = np.array(df0.loc[aeris_mask, c2h6_dset_info['rawdata_colname']])
    df_c2h6 = baseline_correction(seconds, rawdata, c2h6_dset_info)
    df_c2h6.index = df0.loc[aeris_mask,:].index
    df_c2h6.loc[aeris_mask,'Timestamp'] = df0.loc[aeris_mask,'Timestamp']
    baseline_correction_plotter(df_c2h6, c2h6_dset_info)

    pd.set_option('display.precision', 2)
    print(df_ch4)
    print(df_c2h6)

    plt.show()
