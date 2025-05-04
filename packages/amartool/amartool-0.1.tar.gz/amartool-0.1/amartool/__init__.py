
def mean(data):
    """ 
     محاسبه میانگین داده ها

    """
    return sum(data)/ len(data)


def dara_range(data):
    """
    محاسبه بازه داده ها 
    """
    return max(data)- min(data)


import numpy as np
import math


def median(data):
    """
    محاسبه میانه داده ها
    """ 
    return np.median(data)

def variance(data):
    """
    محاسبه واریانس داده ها
    """
    return np.var(data)

def standard_deviation(data):
    """
    محاسبه انحراف معیار داده ها
    """
    return math.sqrt(variance(data))

from scipy import stats

def kurtosis(data):
    """
    محاسبه کشیدگی داده ها
    """
    return stats.kurtosis(data)


def skewness(data):
    """
    محاسبه چولگی داده ها
    """
    return stats.skew(data)



