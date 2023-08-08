import numpy as np
import pandas as pd
import scipy.constants as constants


def steps(df: pd.DataFrame) -> int:
    """
    Return an integer representing the number of steps taken during the session.
    """
    df = df.iloc[:, 1:4] * constants.g
    logic = np.ones(len(df))
    steps = np.zeros(len(df))

    # x-axis
    acc = df.iloc[:, 0]
    # y-axis
    # acc = df.iloc[:, 1]
    w = 10
    steps = 0

    n = range(0, len(df))
    logic = logic[n]

    # compute local variance
    var = np.convolve(acc[n], np.ones((w,))/w, mode='valid')
    pks = np.array([])

    pks = np.array([])
    for i in range(len(var)):
        if (var[i] > 0.1):
            pks = np.append(pks, var[i])

    if (len(pks) != 0):
        thresh = min(pks)
        D1 = thresh*2
        D2 = D1/2
        B = np.zeros(len(var))

        for i in range(len(var)):
            if (var[i] >= thresh):
                B[i] = D1
            else:
                B[i] = D2

        F = np.zeros(len(B))

        F[0] = 1

        for i in range(1, len(B)):
            if (B[i-1] > B[i]):
                F[i] = -1
            elif (B[i-1] < B[i]):
                F[i] = 1

        # count up the steps
        if (F[0] == 1 and logic[i] == 1):
            steps = 1

        for i in range(1, len(F)):
            if (F[i] == 1):
                steps = steps + 1
            elif (F[i] == -1 and F[i-1] == -1 and logic[i] == 1):
                steps = steps + 1

    return steps
