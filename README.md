Minimal working example of background correction routine used for NMT UAV-mounted Aires MIRA Pico.

Developed and tested with python 3.11

### Usage:

```bash
python main.py -f /path/to/csv

python main.py -f data/level0.csv
```

### Output:

pandas dataframe with
* original data timestamp ('Timestamp')
* seconds into dataset ('seconds')
* original data ('CH4' or 'C2H6')
* n-point smoothed data ('smoothed_data')
* segmented and labeled smoothed data ('segment_data' and 'segment_label')
* gradient of smoothed data ('segment_gradient')
* boolean mask from gradient filter ('gradient_mask')
* boolean mask from outlier (mean) filter ('outlier_mask'); final mask for background data
* estimated background ('CH4_background' or 'C2H6_background')
* background-adjusted data ('CH4_adjusted' or 'C2H6_adjusted')

### Dependencies:

Python >3.9 with numpy, pandas, and matplotlib

Script requires csv files with **datetime string** ('Timestamp') and floating point ('CH4' or 'C2H6') data columns

### Customization:

Individual datasets may require custom filter settings to improve background estimate.
Initial filter settings defined in [./main.py](main.py) inside the `dset_info` dictionary.

Timestamp and data column names can also be specified in `dset_info` for specific csv files.


### Contact:

jonathan.dooley@student.nmt.edu