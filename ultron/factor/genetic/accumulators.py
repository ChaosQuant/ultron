# -*- coding: utf-8 -*-

from PyFin.Analysis.SecurityValueHolders import SecurityLatestValueHolder
from PyFin.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityDiffValueHolder
from PyFin.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecuritySignValueHolder
from PyFin.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityExpValueHolder
from PyFin.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityLogValueHolder
from PyFin.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecuritySqrtValueHolder
from PyFin.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityAbsValueHolder
from PyFin.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityNormInvValueHolder
from PyFin.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityCeilValueHolder
from PyFin.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityFloorValueHolder
from PyFin.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityRoundValueHolder
#from PyFin.Analysis.TechnicalAnalysis.StatelessTechnicalAnalysers import SecurityAverageValueHolder
from PyFin.Analysis.CrossSectionValueHolders import CSRankedSecurityValueHolder
from PyFin.Analysis.CrossSectionValueHolders import CSZScoreSecurityValueHolder
from PyFin.Analysis.CrossSectionValueHolders import CSPercentileSecurityValueHolder

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