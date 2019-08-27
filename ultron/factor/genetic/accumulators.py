# -*- coding: utf-8 -*-

from ... utilities.singleton import Singleton
from ultron.sentry.Analysis.SecurityValueHolders import SecurityLatestValueHolder
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
import six

@six.add_metaclass(Singleton)
class Accumulators(object):
    def __init__(self):
        self._accumulators_pool = {
                1:SecurityLatestValueHolder,2:SecurityDiffValueHolder,
                3:SecuritySignValueHolder,4:SecurityExpValueHolder,
                5:SecurityLogValueHolder,6:SecuritySqrtValueHolder,
                7:SecurityAbsValueHolder,8:SecurityNormInvValueHolder,
                9:SecurityCeilValueHolder,10:SecurityFloorValueHolder,
                11:SecurityRoundValueHolder,12:SecurityRoundValueHolder,
                13:CSRankedSecurityValueHolder,
                14:CSZScoreSecurityValueHolder,15:CSPercentileSecurityValueHolder,
                16:SecuritySigmoidValueHolder,17:SecurityTanhValueHolder
        }
        
    def transform(self, expression, is_formula=False):
        var_group  = expression.split('c_')
        formula = ''
        for i in range(len(var_group)):
            if i == 0:
                formula = '\'' + var_group[i] + '\''
            else:
                formula = self._accumulators_pool[int(var_group[i])].__name__ + '(' + formula + ')'
        return eval(formula) if is_formula else formula
    
    def fetch_accumulators_pool(self):
        return self._accumulators_pool
    
    def get_accumulators_pool(self, index):
        return self._accumulators_pool[index]
    
accumulators_pool = Accumulators().fetch_accumulators_pool()
transform = Accumulators().transform