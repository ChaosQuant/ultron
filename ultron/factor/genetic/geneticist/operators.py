# -*- coding: utf-8 -*-

from .... utilities.singleton import Singleton
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

class Function(object):
    def __init__(self, function, arity):
        self.function = function
        self.arity = arity
        self.name = function.__name__

@six.add_metaclass(Singleton)
class Operators(object):
    def __init__(self):
        self._cross_section_mutation_list = [SecurityDiffValueHolder,
                               SecuritySignValueHolder,SecurityExpValueHolder,
                               SecurityLogValueHolder,SecuritySqrtValueHolder,
                               SecurityAbsValueHolder,SecurityNormInvValueHolder,
                               SecurityCeilValueHolder,SecurityFloorValueHolder,
                               SecurityRoundValueHolder,SecurityRoundValueHolder,
                               CSRankedSecurityValueHolder,CSZScoreSecurityValueHolder,
                               CSPercentileSecurityValueHolder,SecuritySigmoidValueHolder,
                               SecurityTanhValueHolder]
        
        self._cross_section_crossover_list = [CSResidueSecurityValueHolder,SecurityAddedValueHolder,
                                          SecuritySubbedValueHolder,SecurityMultipliedValueHolder,
                                          SecurityDividedValueHolder,SecurityLtOperatorValueHolder,
                                          SecurityLeOperatorValueHolder,SecurityGtOperatorValueHolder,
                                          SecurityGeOperatorValueHolder,SecurityEqOperatorValueHolder,
                                          SecurityNeOperatorValueHolder,SecurityAndOperatorValueHolder,
                                          SecurityOrOperatorValueHolder]
        
        self._mutation_list = self._cross_section_mutation_list
        self._crossover_list = self._cross_section_crossover_list
        
        self._mutation_sets = [Function(f, 1) for f in self._mutation_list]
        self._crossover_sets = [Function(f, 2) for f in self._crossover_list]
      
    def calc_factor(self, expression, total_data, indexs, key):
        return eval(expression).transform(total_data.set_index(indexs), 
                                         category_field=key, dropna=False)
        
    def fetch_mutation_sets(self):
        return self._mutation_sets
    
    def fetch_crossover_sets(self):
        return self._crossover_sets
    
mutation_sets = Operators().fetch_mutation_sets()
crossover_sets = Operators().fetch_crossover_sets()
operators_sets = mutation_sets + crossover_sets
calc_factor = Operators().calc_factor