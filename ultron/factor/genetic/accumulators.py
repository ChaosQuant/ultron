# -*- coding: utf-8 -*-

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
#from PyFin.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityAverageValueHolder
from ultron.sentry.Analysis.CrossSectionValueHolders import CSRankedSecurityValueHolder
from ultron.sentry.Analysis.CrossSectionValueHolders import CSZScoreSecurityValueHolder
from ultron.sentry.Analysis.CrossSectionValueHolders import CSPercentileSecurityValueHolder

##使用pyfin构造算子
accumulators_pool = {
                1:SecurityLatestValueHolder,2:SecurityDiffValueHolder,
                3:SecuritySignValueHolder,4:SecurityExpValueHolder,
                5:SecurityLogValueHolder,6:SecuritySqrtValueHolder,
                7:SecurityAbsValueHolder,8:SecurityNormInvValueHolder,
                9:SecurityCeilValueHolder,10:SecurityFloorValueHolder,
                11:SecurityRoundValueHolder,12:SecurityRoundValueHolder,
                #13:SecurityAverageValueHolder,
                13:CSRankedSecurityValueHolder,
                14:CSZScoreSecurityValueHolder,15:CSPercentileSecurityValueHolder
        }