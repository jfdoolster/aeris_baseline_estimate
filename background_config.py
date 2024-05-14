class Baseline_Config:
    rawdata_colname: str
    timestamp_colname:str
    window_size:int
    segment_period:int
    gradient_filter_std_threshold:float
    outlier_filter_std_threshold: float
    polynomial_degree: int
    hard_outlier_threshold: float

    def __init__(self, rawdata_colname:str, timestamp_colname='Timestamp') -> None:
        self.set_columns(rawdata_colname=rawdata_colname, timestamp_colname=timestamp_colname)
        self.set_attrs()

    def set_columns(self, rawdata_colname:str, timestamp_colname='Timestamp'):
        self.rawdata_colname   =  rawdata_colname
        self.timestamp_colname =  rawdata_colname

    def set_attrs(self, window_size:int=3, segment_period:int= 120,
        gradient_filter_std_threshold = 0.2, outlier_filter_std_threshold= 1.0,
        polynomial_degree= 3, hard_outlier_threshold= 5000.0):

        self.window_size= window_size
        self.segment_period= segment_period
        self.gradient_filter_std_threshold = gradient_filter_std_threshold
        self.outlier_filter_std_threshold= outlier_filter_std_threshold
        self.polynomial_degree= polynomial_degree
        self.hard_outlier_threshold= hard_outlier_threshold


    def from_dict(self, d:dict):
        members = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        for dval in members:
            setattr(self, dval, d[dval])
        return self
