import numpy as np
def median(df, location):
    return df[location].median()


def firstQuartile(df, location):
    result = df[location].quantile([0.25]).fillna(0)
    return int(result)


def thirdQuartile(df, location):
    result = df[location].quantile([0.75]).fillna(0)
    return int(result)

def getLowerBound(df, location):
    Q1 = df[location].quantile(0.25)
    Q3 = df[location].quantile(0.75)
    IQR = Q3 - Q1
    return Q1 - (1.5 * IQR)


def getUpperBound(df, location):
    Q1 = df[location].quantile(0.25)
    Q3 = df[location].quantile(0.75)
    IQR = Q3 - Q1
    return Q3 + (1.5 * IQR)
