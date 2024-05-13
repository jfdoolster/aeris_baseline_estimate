class Baseline_Config:
    rawdata_colname: str
    timestamp_colname:str               = 'Timestamp'
    window_size:int                     = 3
    segment_period:int                  = 120
    gradient_filter_std_threshold:float = 0.2
    outlier_filter_std_threshold: float = 1.0
    polynomial_degree: int              = 3
    hard_outlier_threshold: float       = 5000.0

    def __init__(self, rawdata_colname:str) -> None:
        self.rawdata_colname =  rawdata_colname

    def from_dict(self, d:dict):
        self.rawdata_colname                = d['rawdata_colname']
        self.timestamp_colname              = d['timestamp_colname']
        self.window_size                    = d['window_size']
        self.segment_period                 = d['segment_period']
        self.gradient_filter_std_threshold  = d['gradient_filter_std_threshold']
        self.outlier_filter_std_threshold   = d['outlier_filter_std_threshold']
        self.polynomial_degree              = d['polynomial_degree']
        self.hard_outlier_threshold         = d['hard_outlier_threshold']

    def to_dict(self):
        return dict({
            'rawdata_colname'               : self.rawdata_colname,
            'timestamp_colname'             : self.timestamp_colname,
            'window_size'                   : self.window_size,
            'segment_period'                : self.segment_period,
            'gradient_filter_std_threshold' : self.gradient_filter_std_threshold,
            'outlier_filter_std_threshold'  : self.outlier_filter_std_threshold,
            'polynomial_degree'             : self.polynomial_degree,
            'hard_outlier_threshold'        : self.hard_outlier_threshold,
        })
