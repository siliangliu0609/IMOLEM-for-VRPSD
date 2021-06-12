# 来源：Diversity preservation with hybrid recombination for evolutionary multiobjective optimization. DOI: 10.1109/CEC.2014.6900617

import numpy as np


def triangle_S_vector(a, b):
    #a = np.array(a)
    #b = np.array(b)
    al = np.linalg.norm(a)
    bl = np.linalg.norm(b)
    cos = a.dot(b)/(al*bl)
    sin = np.sqrt(1-cos**2)
    S = al*bl*sin/2
    return S


def triangle_S_point(a, b, c):
    v1 = np.array(b)-np.array(a)
    v2 = np.array(c)-np.array(a)
    S = triangle_S_vector(v1, v2)
    return S


def cal_mrdl(P, C, x, y):
    assert(len(P) == len(C))
    if len(P) == 0:
        return 0
    else:
        max = 0
        for i in range(len(P)):
            r = triangle_S_point(x, P[i], C[i])/triangle_S_point(y, P[i], C[i])
            if r > max:
                max = r
        return max


if __name__ == '__main__':
    a = [1, 0]
    b = [0, 2]
    c = [0, 0]
    S = triangle_S_point(a, b, c)
    print(S)
