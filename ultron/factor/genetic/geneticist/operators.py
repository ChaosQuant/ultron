# -*- coding: utf-8 -*-

import numpy as np
from .... utilities.singleton import Singleton
from ultron.sentry.Analysis.SecurityValueHolders import SecurityLatestValueHolder
from ultron.sentry.Analysis.SecurityValueHolders import SecurityCurrentValueHolder

##横截面变异
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityAverageValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityDiffValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecuritySignValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityExpValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityLogValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecuritySqrtValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityAbsValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityAcosValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityAcoshValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityAsinValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityAsinhValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityNormInvValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityCeilValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityFloorValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityRoundValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecuritySigmoidValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityTanhValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecuritySimpleReturnValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityLogReturnValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecuritySigmoidValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityTanhValueHolder

##横截面交叉
from ultron.sentry.Analysis.SecurityValueHolders import SecurityAddedValueHolder
from ultron.sentry.Analysis.SecurityValueHolders import SecuritySubbedValueHolder
from ultron.sentry.Analysis.SecurityValueHolders import SecurityMultipliedValueHolder
from ultron.sentry.Analysis.SecurityValueHolders import SecurityDividedValueHolder
from ultron.sentry.Analysis.SecurityValueHolders import SecurityLtOperatorValueHolder
from ultron.sentry.Analysis.SecurityValueHolders import SecurityLeOperatorValueHolder
from ultron.sentry.Analysis.SecurityValueHolders import SecurityGtOperatorValueHolder
from ultron.sentry.Analysis.SecurityValueHolders import SecurityGeOperatorValueHolder
from ultron.sentry.Analysis.SecurityValueHolders import SecurityEqOperatorValueHolder
from ultron.sentry.Analysis.SecurityValueHolders import SecurityNeOperatorValueHolder
from ultron.sentry.Analysis.SecurityValueHolders import SecurityAndOperatorValueHolder
from ultron.sentry.Analysis.SecurityValueHolders import SecurityOrOperatorValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityMinimumValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityMaximumValueHolder

from ultron.sentry.Analysis.CrossSectionValueHolders import CSAverageSecurityValueHolder
from ultron.sentry.Analysis.CrossSectionValueHolders import CSAverageAdjustedSecurityValueHolder
from ultron.sentry.Analysis.CrossSectionValueHolders import CSResidueSecurityValueHolder

from ultron.sentry.Analysis.CrossSectionValueHolders import CSRankedSecurityValueHolder
from ultron.sentry.Analysis.CrossSectionValueHolders import CSPercentileSecurityValueHolder
from ultron.sentry.Analysis.CrossSectionValueHolders import CSZScoreSecurityValueHolder

## 横截面变异
#from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityPowValueHolder # 指定默认参数

## 时间序列变异
#from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityMACDValueHolder #双默认参数

from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityXAverageValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingAverage
from ultron.sentry.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingDecay
from ultron.sentry.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingMax
from ultron.sentry.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingArgMax
from ultron.sentry.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingMin
from ultron.sentry.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingArgMin
from ultron.sentry.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingRank
from ultron.sentry.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingQuantile
from ultron.sentry.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingAllTrue
from ultron.sentry.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingAnyTrue
from ultron.sentry.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingSum
from ultron.sentry.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingVariance
from ultron.sentry.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingStandardDeviation
from ultron.sentry.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingCountedPositive
from ultron.sentry.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingPositiveAverage
from ultron.sentry.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingPositiveDifferenceAverage
from ultron.sentry.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingNegativeDifferenceAverage
from ultron.sentry.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingRSI
from ultron.sentry.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingLogReturn

from ultron.sentry.Analysis.SecurityValueHolders import SecurityDeltaValueHolder
from ultron.sentry.Analysis.SecurityValueHolders import SecurityShiftedValueHolder


## 时间序列交叉
from ultron.sentry.Analysis.TechnicalAnalysis.StatefulTechnicalAnalysers import SecurityMovingCorrelation


import six,pdb
from enum import Enum, unique

@unique
class FunctionType(Enum):
    cross_section = 1
    time_series = 2

class Function(object):
    def __init__(self, function, arity, ftype, default_value=0):
        self.function = function
        self.arity = arity
        self.name = function.__name__
        self.ftype = ftype
        self.default_value = default_value

@six.add_metaclass(Singleton)
class Operators(object):
    def __init__(self):
       
        # 时间序列默认周期列表
        self._ts_period = [2, 4, 6, 8 ,10]
        
        self._init_cs()
        self._init_ts()
        
        self._cs_mutation_function_list = [Function(f, 1, FunctionType.cross_section) for f in self._cross_section_mutation_list]
        self._cs_crossover_function_list = [Function(f, 2, FunctionType.cross_section) for f in self._cross_section_crossover_list]
        #时间序列默认为5天
        self._ts_mutation_function_list = [Function(f, 1, FunctionType.time_series, self._ts_period[np.random.randint(0, len(self._ts_period))]
                                                   ) for f in self._time_series_mutation_list]
        self._ts_crossover_function_list = [Function(f, 2, FunctionType.time_series, self._ts_period[np.random.randint(0, len(self._ts_period))]
                                                    ) for f in self._time_series_crossover_list]
        
        self._mutation_sets = self._cs_mutation_function_list + self._ts_mutation_function_list
        self._crossover_sets = self._cs_crossover_function_list + self._ts_crossover_function_list
        
    
    def _init_cs(self):
        self._cross_section_mutation_list = [SecurityAverageValueHolder,SecurityDiffValueHolder,
                                             SecurityTanhValueHolder,SecuritySignValueHolder,
                                             SecurityExpValueHolder, SecurityLogValueHolder,SecuritySqrtValueHolder,
                                             SecurityAbsValueHolder,SecurityAcosValueHolder,
                                             SecurityAsinValueHolder,SecurityAsinhValueHolder,
                               SecurityAcoshValueHolder,SecurityNormInvValueHolder,
                               SecurityCeilValueHolder,SecurityFloorValueHolder,
                               SecurityRoundValueHolder,SecuritySimpleReturnValueHolder,
                               SecurityLogReturnValueHolder,SecuritySigmoidValueHolder,
                               CSRankedSecurityValueHolder,CSZScoreSecurityValueHolder,
                               CSPercentileSecurityValueHolder,CSAverageSecurityValueHolder,
                               CSAverageAdjustedSecurityValueHolder]
        
        self._cross_section_crossover_list = [CSResidueSecurityValueHolder,SecurityAddedValueHolder,
                                          SecuritySubbedValueHolder,SecurityMultipliedValueHolder,
                                          SecurityDividedValueHolder,SecurityLtOperatorValueHolder,
                                          SecurityLeOperatorValueHolder,SecurityGtOperatorValueHolder,
                                          SecurityGeOperatorValueHolder,SecurityEqOperatorValueHolder,
                                          SecurityNeOperatorValueHolder,SecurityAndOperatorValueHolder,
                                          SecurityOrOperatorValueHolder,SecurityMinimumValueHolder,
                                          SecurityMaximumValueHolder]
        
    def _init_ts(self):
        self._time_series_mutation_list = [
            SecurityXAverageValueHolder,SecurityMovingAverage,
            SecurityMovingDecay,SecurityMovingMax,
            SecurityMovingArgMax,SecurityMovingMin,
            SecurityMovingArgMin,SecurityMovingRank,
            SecurityMovingQuantile,SecurityMovingAllTrue,
            SecurityMovingAnyTrue,SecurityMovingSum,
            SecurityMovingVariance,SecurityMovingStandardDeviation,
            SecurityMovingCountedPositive,SecurityMovingPositiveAverage,
            SecurityMovingPositiveDifferenceAverage,SecurityMovingNegativeDifferenceAverage,
            SecurityMovingRSI,SecurityMovingLogReturn,SecurityDeltaValueHolder,
            SecurityShiftedValueHolder
        ]
        
        self._time_series_crossover_list = [
            SecurityMovingCorrelation
        ]
        
        
    def custom_transformer(self, formula_sets):
        operators_sets =  self._mutation_sets + self._crossover_sets
        return [operator for operator in operators_sets if operator.name in formula_sets]
        
    def calc_factor(self, expression, total_data, indexs, key, name='transformed'):
        return eval(expression).transform(total_data.set_index(indexs), 
                                         category_field=key, name=name,
                                          dropna=False)
        
    def fetch_mutation_sets(self):
        return self._mutation_sets
    
    def fetch_crossover_sets(self):
        return self._crossover_sets
    
mutation_sets = Operators().fetch_mutation_sets()
crossover_sets = Operators().fetch_crossover_sets()
operators_sets = mutation_sets + crossover_sets
calc_factor = Operators().calc_factor
custom_transformer = Operators().custom_transformer
