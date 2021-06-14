# 来源：Online Diversity Assessment in Evolutionary Multiobjective Optimization: A Geometrical Perspective. DOI: 10.1109/TEVC.2014.2353672

import random
import numpy as np

from . import moead


def triangle_S(a, b, c):
    v1 = np.array(b)-np.array(a)
    v2 = np.array(c)-np.array(a)
    v3 = np.array(c)-np.array(b)
    l1 = (np.sum(v1**2))**0.5
    l2 = (np.sum(v2**2))**0.5
    l3 = (np.sum(v3**2))**0.5
    p = 0.5*(l1+l2+l3)
    S2 = p*(p-l1)*(p-l2)*(p-l3)
    if S2 < 0:
        return 0
    else:
        return S2**0.5


def cal_mrdl(P, C, x, y):
    assert(len(P) == len(C))
    if len(P) == 0:
        return 0
    else:
        if True in map(y.equal, C):
            return float('inf')
        if True in map(x.equal, P):
            return 0
        max = 0
        for i in range(len(P)):
            numerator = triangle_S(x.get_objective(), P[i].get_objective(), C[i].get_objective())
            denominator = triangle_S(y.get_objective(), P[i].get_objective(), C[i].get_objective())
            if denominator == 0:
                return float('inf')
            else:
                r = numerator/denominator
            if r > max:
                max = r
        return max


def environmental_selection(P, C, weigh_vectors, Z, gamma, objective_num=3):
    assert(len(P) == len(C))
    D = list(range(len(P)))
    random.shuffle(D)
    newP, Pconv, Cconv = [], [], []
    for k in D:
        P_M = []
        tch_C = moead.cal_tchbycheff(C[k], weigh_vectors, k, Z, objective_num)
        for neighbour in weigh_vectors.B[k]:
            tch_neighbour_parent = moead.cal_tchbycheff(P[neighbour], weigh_vectors, neighbour, Z, objective_num)
            if tch_neighbour_parent > tch_C:
                P_M.append(P[neighbour])
        if len(P_M) == 0:
            newP.append(P[k])
        else:
            nearest_diff = float('inf')
            for plan in P_M:
                diff = C[k].cal_difference(plan)
                if diff < nearest_diff:
                    nearest_diff = diff
                    nearest_plan = plan
            if len(Pconv) == 0 and len(Cconv) == 0:
                newP.append(C[k])
                Pconv.append(nearest_plan)
                Cconv.append(C[k])
            else:
                mrdl_list = []
                for plan in P_M:
                    mrdl_list.append(cal_mrdl(Pconv, Cconv, plan, C[k]))
                if min(mrdl_list) > gamma:
                    newP.append(P[k])
                else:
                    newP.append(C[k])
                    Pconv.append(nearest_plan)
                    Cconv.append(C[k])
    return newP


if __name__ == '__main__':
    a = [1, 0]
    b = [0, 2]
    c = [0, 0]
    S = triangle_S(a, b, c)
    print(S)
