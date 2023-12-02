Minimal working example of baseline correction routine used for NMT UAV-mounted Aires MIRA Pico.

Developed and tested with python 3.11

### usage:

```bash
python main.py -f /path/to/csv

python main.py -f data/merge.csv
```

### output:

pandas dataframe with
* original data timestamp ('Timestamp')
* seconds into dataset ('seconds')
* original data ('CH4' or 'C2H6')
* n-point smoothed data ('smoothed_data')
* segmented and labeled smoothed data ('segment_data' and 'segment_label')
* gradient of smoothed data ('segment_gradient')
* boolean mask from gradient filter ('gradient_mask')
* boolean mask from outlier (mean) filter ('outlier_mask'); final mask for baseline data
* estimated baseline ('CH4_baseline' or 'C2H6_baseline')
* baseline-adjusted data ('CH4_adjusted' or 'C2H6_adjusted')

### dependencies:

python >3.9 with numpy, pandas, and matplotlib

currently requires csv files with **datetime string** ('Timestamp') and floating point ('CH4' or 'C2H6') data columns

### customization:

Individual datasets may require custom filter settings to improve baseline estimate.
Filter settings are definined in [./main.py](main.py) inside the `dset_info` dictionary.

Timestamp and data column names can also be specified in `dset_info` for specific csv files.


### contact:

jonathan.dooley@student.nmt.edu