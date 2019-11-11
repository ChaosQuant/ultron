import os,time, pdb
import datetime as dt
import sqlalchemy
import numpy as np
import pandas as pd
import statsmodels.api as sm
from . long_short import LongShortWeighted
from . only_side import OnlySideWeighted
from . high_frequency import HighFrequencyWeighted
from . basic_indicators import IC_Weighted

class Weighted(object):
    @classmethod
    def create_weighted(cls, method='longshort'):
        if method == 'longshort':
            return LongShortWeighted()
        elif method == 'onlyside':
            return OnlySideWeighted()
        elif method == 'high_frequency':
            return HighFrequencyWeighted()
        elif method == 'ic':
            return IC_Weighted('ic')
        elif method == 'ir':
            return IC_Weighted('ir')
        else:
            return None