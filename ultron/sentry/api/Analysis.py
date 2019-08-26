# -*- coding: utf-8 -*-


import functools

from ultron.sentry.Analysis.TechnicalAnalysis import SecurityMovingAverage
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityMovingDecay
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityMovingMax
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityMovingArgMax
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityMovingMin
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityMovingArgMin
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityMovingRank
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityMaximumValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityMinimumValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityMovingQuantile
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityMovingAllTrue
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityMovingAnyTrue
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityMovingSum
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityMovingVariance
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityMovingStandardDeviation
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityMovingCountedPositive
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityMovingPositiveAverage
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityMovingRSI
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityMovingCorrelation
from ultron.sentry.Analysis.TechnicalAnalysis import SecuritySignValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityAverageValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityXAverageValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityMACDValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis import SecuritySqrtValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityDiffValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis import SecuritySimpleReturnValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityLogReturnValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityExpValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityLogValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityPowValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityAbsValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityAcosValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityAcoshValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityAsinValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityAsinhValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityNormInvValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityCeilValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityFloorValueHolder
from ultron.sentry.Analysis.TechnicalAnalysis import SecurityRoundValueHolder
from ultron.sentry.Analysis.SecurityValueHolders import SecurityShiftedValueHolder
from ultron.sentry.Analysis.SecurityValueHolders import SecurityDeltaValueHolder
from ultron.sentry.Analysis.SecurityValueHolders import SecurityCurrentValueHolder
from ultron.sentry.Analysis.SecurityValueHolders import SecurityLatestValueHolder
from ultron.sentry.Analysis.SecurityValueHolders import SecurityIIFValueHolder

from ultron.sentry.Analysis.CrossSectionValueHolders import CSRankedSecurityValueHolder
from ultron.sentry.Analysis.CrossSectionValueHolders import CSTopNSecurityValueHolder
from ultron.sentry.Analysis.CrossSectionValueHolders import CSBottomNSecurityValueHolder
from ultron.sentry.Analysis.CrossSectionValueHolders import CSTopNPercentileSecurityValueHolder
from ultron.sentry.Analysis.CrossSectionValueHolders import CSBottomNPercentileSecurityValueHolder
from ultron.sentry.Analysis.CrossSectionValueHolders import CSAverageSecurityValueHolder
from ultron.sentry.Analysis.CrossSectionValueHolders import CSAverageAdjustedSecurityValueHolder
from ultron.sentry.Analysis.CrossSectionValueHolders import CSZScoreSecurityValueHolder
from ultron.sentry.Analysis.CrossSectionValueHolders import CSFillNASecurityValueHolder
from ultron.sentry.Analysis.CrossSectionValueHolders import CSPercentileSecurityValueHolder
from ultron.sentry.Analysis.CrossSectionValueHolders import CSResidueSecurityValueHolder


def CSRank(x, groups=None):
    return CSRankedSecurityValueHolder(x, groups)


def CSTopN(x, n, groups=None):
    return CSTopNSecurityValueHolder(x, n, groups)


def CSTopNQuantile(x, n, groups=None):
    return CSTopNPercentileSecurityValueHolder(x, n, groups)


def CSBottomN(x, n, groups=None):
    return CSBottomNSecurityValueHolder(x, n, groups)


def CSBottomNQuantile(x, n, groups=None):
    return CSBottomNPercentileSecurityValueHolder(x, n, groups)


def CSMean(x, groups=None):
    return CSAverageSecurityValueHolder(x, groups)


def CSMeanAdjusted(x, groups=None):
    return CSAverageAdjustedSecurityValueHolder(x, groups)


def CSQuantiles(x, groups=None):
    return CSPercentileSecurityValueHolder(x, groups)


def CSZScore(x, groups=None):
    return CSZScoreSecurityValueHolder(x, groups)


def CSFillNA(x, groups=None):
    return CSFillNASecurityValueHolder(x, groups)


def CSRes(left, right):
    return CSResidueSecurityValueHolder(left, right)


def SIGN(x='x'):
    return SecuritySignValueHolder(x)


def AVG(x='x'):
    return SecurityAverageValueHolder(x)


def EMA(window, x='x'):
    return SecurityXAverageValueHolder(window, x)


def MACD(short, long, x='x'):
    return SecurityMACDValueHolder(short, long, x)


def RSI(window, x='x'):
    return SecurityMovingRSI(window, x)


def MCORR(window, x='x', y='y'):
    return SecurityMovingCorrelation(window, x, y)


def MA(window, x='x'):
    return SecurityMovingAverage(window, x)


def MADecay(window, x='x'):
    return SecurityMovingDecay(window, x)


def MMAX(window, x='x'):
    return SecurityMovingMax(window, x)


def MARGMAX(window, x='x'):
    return SecurityMovingArgMax(window, x)


def MMIN(window, x='x'):
    return SecurityMovingMin(window, x)


def MARGMIN(window, x='x'):
    return SecurityMovingArgMin(window, x)


def MRANK(window, x='x'):
    return SecurityMovingRank(window, x)


def MAXIMUM(x='x', y='y'):
    return SecurityMaximumValueHolder(x, y)


def MINIMUM(x='x', y='y'):
    return SecurityMinimumValueHolder(x, y)


def MQUANTILE(window, x='x'):
    return SecurityMovingQuantile(window, x)


def MALLTRUE(window, x='x'):
    return SecurityMovingAllTrue(window, x)


def MANYTRUE(window, x='x'):
    return SecurityMovingAnyTrue(window, x)


def MSUM(window, x='x'):
    return SecurityMovingSum(window, x)


def MVARIANCE(window, x='x'):
    return SecurityMovingVariance(window, x)


def MSTD(window, x='x'):
    return SecurityMovingStandardDeviation(window, x)


def MNPOSITIVE(window, x='x'):
    return SecurityMovingCountedPositive(window, x)


def MAPOSITIVE(window, x='x'):
    return SecurityMovingPositiveAverage(window, x)


def CURRENT(x='x'):
    return SecurityCurrentValueHolder(x)


def LAST(x='x'):
    return SecurityLatestValueHolder(x)


def SQRT(x='x'):
    return SecuritySqrtValueHolder(x)


def DIFF(x='x'):
    return SecurityDiffValueHolder(x)


def RETURNSimple(x='x'):
    return SecuritySimpleReturnValueHolder(x)


def RETURNLog(x='x'):
    return SecurityLogReturnValueHolder(x)


def EXP(x):
    return SecurityExpValueHolder(x)


def LOG(x):
    return SecurityLogValueHolder(x)


def POW(x, n):
    return SecurityPowValueHolder(x, n)


def ABS(x):
    return SecurityAbsValueHolder(x)


def ACOS(x):
    return SecurityAcosValueHolder(x)


def ACOSH(x):
    return SecurityAcoshValueHolder(x)


def ASIN(x):
    return SecurityAsinValueHolder(x)


def ASINH(x):
    return SecurityAsinhValueHolder(x)


def NORMINV(x):
    return SecurityNormInvValueHolder(x)


def CEIL(x):
    return SecurityCeilValueHolder(x)


def FLOOR(x):
    return SecurityFloorValueHolder(x)


def ROUND(x):
    return SecurityRoundValueHolder(x)


def SHIFT(x, n):
    return SecurityShiftedValueHolder(n, x)


def DELTA(x, n):
    return SecurityDeltaValueHolder(n, x)


def IIF(flag, left, right):
    return SecurityIIFValueHolder(flag, left, right)


def INDUSTRY(name, level=1):
    name = name.lower()
    if name == 'sw':
        if level in (1, 2, 3):
            return LAST(name + str(level))
        else:
            raise ValueError('{0} is not recognized level for {1}'.format(level, name))
    else:
        raise ValueError('currently only `sw` industry is supported. {1} is not a recognized industry type')


HIGH = functools.partial(LAST, 'highestPrice')
LOW = functools.partial(LAST, 'lowestPrice')
OPEN = functools.partial(LAST, 'openPrice')
CLOSE = functools.partial(LAST, 'closePrice')



