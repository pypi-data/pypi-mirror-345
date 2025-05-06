import datetime
import pandas as pd
import numpy as np
from .ml import autoreg_fill
def tryfloat(x, nanflag:float = None, nanvalue=np.nan):
    if nanflag and np.abs(float(x) - nanflag) < 1E-8:
        return nanvalue
    try:
        return float(x)
    except:
        return nanvalue


def moving_avg(x:np.ndarray, w:int) -> np.ndarray:
    if w % 2 != 1:
        raise ValueError(f'moving_avg w % 2 == 1, given {w}')
    data = np.convolve(x, np.ones(w), 'same') / w
    hw = int((w-1)/2)
    data[:hw] = data[hw]
    data[-hw:] = data[-(hw+1)]
    return data


def outlier_filter_single_point(data, thres=3.0):
    xm = np.nanmedian(data)
    xstd = np.nanstd(data)
    N = len(data)
    for i in range(N):
        if not np.isnan(data[i]):
            if i == 0 or np.isnan(data[i - 1]):
                xb = data[i] - xm
            else:
                xb = data[i] - data[i - 1]
            if i == (N - 1) or np.isnan(data[i + 1]):
                xf = data[i] - xm
            else:
                xf = data[i] - data[i + 1]
            if xb * xf > 0 and xb > thres * xstd and xf > thres * xstd:
                data[i] = np.nan
    return data


def outlier_filer_sigma(data, thres):
    d = data - moving_avg(data, 9)
    I = np.abs(d - d.mean()) > thres * d.std()
    data[I] = np.nan
    return data

class ExcelDataProcessor(object):
    def __init__(self, fn, sheetname):
        self.df = pd.read_excel(fn, sheetname)

    def try_convert_float(self, key, nanflag=None):
        if key in self.df.keys():
            self.df[key] = self.df[key].map(lambda x: tryfloat(x, nanflag))
        else:
            raise ValueError(f'ExcelDataProcessor: unexpected key {key}')

    def try_convert_datetime(self, key, format):
        if key in self.df.keys():
            self.df[key] = self.df[key].map(lambda x: datetime.datetime.strptime(x, format))
        else:
            raise ValueError(f'ExcelDataProcessor: unexpected key {key}')

    def try_convert_str(self, key):
        if key in self.df.keys():
            self.df[key] = self.df[key].astype(str)
        else:
            raise ValueError(f'ExcelDataProcessor: unexpected key {key}')

    def left_merge_by_key(self, df, key):
        self.df = pd.merge(left=self.df, right=df, how='left', on=key)

    def outlier_filter(self, key, thres=3.0):
        if key in self.df.keys():
            # plt.plot(self.df[key].to_numpy())
            # plt.plot(outlier_filer_sigma(self.df[key].interpolate().to_numpy(), thres))
            # plt.title(key)
            # plt.show()
            self.df[key] = pd.Series(outlier_filer_sigma(self.df[key].interpolate().to_numpy(), thres))
        else:
            raise ValueError(f'ExcelDataProcessor: unexpected key {key}')

    def autoreg_fill(self, key, rank):
        if key in self.df.keys():
            self.df[key] = pd.Series(autoreg_fill(self.df[key].to_numpy(), rank))
        else:
            raise ValueError(f'ExcelDataProcessor: unexpected key {key}')


