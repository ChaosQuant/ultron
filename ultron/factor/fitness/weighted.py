import os,time, pdb
import datetime as dt
import sqlalchemy
import numpy as np
import pandas as pd
import statsmodels.api as sm
from . long_short import LongShortWeighted
from . only_long import OnlyLongWeighted

class Weighted(object):
    @classmethod
    def create_weighted(cls, method='longshort'):
        if method == 'longshort':
            return LongShortWeighted
        else:
            return OnlyLongWeighted