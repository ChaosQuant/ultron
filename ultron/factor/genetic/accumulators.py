# -*- coding: utf-8 -*-

from ... utilities.singleton import Singleton
from ultron.sentry.Analysis.SecurityValueHolders import SecurityLatestValueHolder
from ultron.sentry.Analysis.SecurityValueHolders import SecurityCurrentValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityDiffValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecuritySignValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityExpValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityLogValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecuritySqrtValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityAbsValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityNormInvValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityCeilValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityFloorValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityRoundValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecuritySigmoidValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityTanhValueHolder
from ultron.sentry.Analysis.CrossSectionValueHolders import CSRankedSecurityValueHolder
from ultron.sentry.Analysis.CrossSectionValueHolders import CSZScoreSecurityValueHolder
from ultron.sentry.Analysis.CrossSectionValueHolders import CSPercentileSecurityValueHolder


from ultron.sentry.Analysis.CrossSectionValueHolders import CSResidueSecurityValueHolder
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

import six,pdb

@six.add_metaclass(Singleton)
class Accumulators(object):
    def __init__(self):
        self._accumulators_pool = {
                1:SecurityCurrentValueHolder,2:SecurityDiffValueHolder,
                3:SecuritySignValueHolder,4:SecurityExpValueHolder,
                5:SecurityLogValueHolder,6:SecuritySqrtValueHolder,
                7:SecurityAbsValueHolder,8:SecurityNormInvValueHolder,
                9:SecurityCeilValueHolder,10:SecurityFloorValueHolder,
                11:SecurityRoundValueHolder,12:SecurityRoundValueHolder,
                13:CSRankedSecurityValueHolder,
                14:CSZScoreSecurityValueHolder,15:CSPercentileSecurityValueHolder,
                16:SecuritySigmoidValueHolder,17:SecurityTanhValueHolder
        }
        
        self._mutated_pool = {
                1:SecurityCurrentValueHolder,2:SecurityDiffValueHolder,
                3:SecuritySignValueHolder,4:SecurityExpValueHolder,
                5:SecurityLogValueHolder,6:SecuritySqrtValueHolder,
                7:SecurityAbsValueHolder,8:SecurityNormInvValueHolder,
                9:SecurityCeilValueHolder,10:SecurityFloorValueHolder,
                11:SecurityRoundValueHolder,12:SecurityRoundValueHolder,
                13:CSRankedSecurityValueHolder,
                14:CSZScoreSecurityValueHolder,15:CSPercentileSecurityValueHolder,
                16:SecuritySigmoidValueHolder,17:SecurityTanhValueHolder
        }
        self._cross_pool = {
                1:CSResidueSecurityValueHolder,2:SecurityAddedValueHolder,
                3:SecuritySubbedValueHolder,4:SecurityMultipliedValueHolder,
                5:SecurityDividedValueHolder,6:SecurityLtOperatorValueHolder,
                7:SecurityLeOperatorValueHolder,8:SecurityGtOperatorValueHolder,
                9:SecurityGeOperatorValueHolder,10:SecurityEqOperatorValueHolder,
                11:SecurityNeOperatorValueHolder,12:SecurityAndOperatorValueHolder,
                13:SecurityOrOperatorValueHolder
        }
        
    def transform(self, expression, is_formula=False):
        var_group  = expression.split('c_')
        formula = ''
        is_acc = False
        for i in range(len(var_group)):
            if i == 0:
                formula = '\'' + var_group[i] + '\''
            elif int(var_group[i]) > 1:
                is_acc = True
                formula = self._accumulators_pool[int(var_group[i])].__name__ + '(' + formula + ')'
        if not is_acc : formula = self._accumulators_pool[1].__name__ + '(' + formula + ')'
        return eval(formula) if is_formula else formula
    
    def dependency(self, expression_sets):
        result = {}
        expression_list = list(expression_sets)
        for expression in expression_list:
            result[expression] = ','.join(eval(expression)._dependency)
        return result
            
        
    def calc_new_factor(self, mutated_cross_columns, factor_data):
        new_factors = None
        for columns in mutated_cross_columns:
            sub_data = eval(columns).transform(factor_data, name=str(columns),
                                                category_field='code', dropna=False)
            sub_data = sub_data.reset_index().set_index('trade_date','code')
            if new_factors is None:
                new_factors = sub_data.copy()
            else:
                new_factors[str(columns)] = sub_data[str(columns)].values
        return new_factors.reset_index()[mutated_cross_columns]
            
            
    def fetch_accumulators_pool(self):
        return self._accumulators_pool
    
    def fetch_mutated_pool(self):
        return self._mutated_pool
    
    def fetch_cross_pool(self):
        return self._cross_pool
    
    def get_accumulators_pool(self, index):
        return self._accumulators_pool[index]
    
accumulators_pool = Accumulators().fetch_accumulators_pool()
mutated_pool = Accumulators().fetch_mutated_pool()
cross_pool = Accumulators().fetch_cross_pool()
transform = Accumulators().transform
dependency = Accumulators().dependency
calc_new_factor = Accumulators().calc_new_factor