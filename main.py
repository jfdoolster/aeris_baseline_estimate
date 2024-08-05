
if __name__=="__main__":

    import argparse
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from background_plotter import background_estimate_plotter
    from background_calc import background_estimate
    from background_config import Background_Config

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', required=True, type=str,
        help='path to csv datafile with Timestamp and CH4 (or C2H6) labelled data columns')
    args = parser.parse_args()
    argdict = vars(args)

    rawdata_path = argdict['file']

    # read data
    df0 = pd.read_csv(rawdata_path, parse_dates=['Timestamp'])
    if 'Seconds' not in df0.columns:
        df0.insert(1, 'Seconds', (df0['Timestamp']-df0['Timestamp'].min())/np.timedelta64(1, 's'))

    aeris_mask = (df0['CH4'].notna() & df0['C2H6'].notna()) 
    if 'Sts' in df0.columns:
        aeris_mask &= (df0['Sts'] > 0)


    # set configuration class for CH4 and C2H6
    ch4_class = Background_Config(rawdata_colname="CH4")

    c2h6_class = Background_Config(rawdata_colname="C2H6")
    c2h6_class.polynomial_degree = 4

    # read and process METHANE data only
    ch4_dset_info = ch4_class.__dict__
    seconds = np.array(df0.loc[aeris_mask,'Seconds'])
    rawdata = np.array(df0.loc[aeris_mask, ch4_dset_info['rawdata_colname']])
    df_ch4 = background_estimate(seconds, rawdata, ch4_dset_info)
    df_ch4.index = df0.loc[aeris_mask,:].index
    df_ch4.loc[aeris_mask,'Timestamp'] = df0.loc[aeris_mask,'Timestamp']
    background_estimate_plotter(df_ch4, ch4_dset_info)

    # read and process ETHANE data only
    c2h6_dset_info = c2h6_class.__dict__
    seconds = np.array(df0.loc[aeris_mask,'Seconds'])
    rawdata = np.array(df0.loc[aeris_mask, c2h6_dset_info['rawdata_colname']])
    df_c2h6 = background_estimate(seconds, rawdata, c2h6_dset_info)
    df_c2h6.index = df0.loc[aeris_mask,:].index
    df_c2h6.loc[aeris_mask,'Timestamp'] = df0.loc[aeris_mask,'Timestamp']
    background_estimate_plotter(df_c2h6, c2h6_dset_info)

    pd.set_option('display.precision', 2)
    print(df_ch4)
    print(df_c2h6)

    plt.show()
