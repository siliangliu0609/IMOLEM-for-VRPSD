# 来源：https://blog.csdn.net/jiang425776024/article/details/84635353

import numpy as np
import random


class Weight_vector:
    # 对m维空间，目标方向个数H
    def __init__(self, H=13, m=3, T_size=20):
        self.H = H
        self.m = m
        self.W = self.__get_mean_vectors()
        self.T_size = T_size
        self.W_Bi_T = []  # 权重的T个邻居

    def __perm(self, sequence):
        # ！！！ 序列全排列，且无重复
        l = sequence
        if (len(l) <= 1):
            return [l]
        r = []
        for i in range(len(l)):
            if i != 0 and sequence[i - 1] == sequence[i]:
                continue
            else:
                s = l[:i] + l[i + 1:]
                p = self.__perm(s)
                for x in p:
                    r.append(l[i:i + 1] + x)
        return r

    def __get_mean_vectors(self):
        H = self.H
        m = self.m
        sequence = []
        for ii in range(H):
            sequence.append(0)
        for jj in range(m - 1):
            sequence.append(1)
        ws = []

        pe_seq = self.__perm(sequence)
        for sq in pe_seq:
            s = -1
            weight = []
            for i in range(len(sq)):
                if sq[i] == 1:
                    w = i - s
                    w = (w - 1) / H
                    s = i
                    weight.append(w)
            nw = H + m - 1 - s
            nw = (nw - 1) / H
            weight.append(nw)
            if weight not in ws:
                ws.append(weight)
        return np.array(ws)

    def cal_W_Bi_T(self):
        # 计算权重的T个邻居
        for bi in range(len(self.W)):
            Bi = self.W[bi]
            DIS = np.sum((self.W - Bi) ** 2, axis=1)
            B_T = np.argsort(DIS)
            # 第0个是自己（距离永远最小）
            B_T = B_T[1:self.T_size + 1]
            self.W_Bi_T.append(B_T)

    def pick_2_neighbor_of_W_i(self, i):
        pick = random.sample(range(self.T_size), 2)
        return self.W_Bi_T[i][pick[0]], self.W_Bi_T[i][pick[1]]


def initialize_Z(P):
    distance = []
    pay = []
    NV = []
    for plan in P:
        distance.append(plan.distance)
        pay.append(plan.pay)
        NV.append(len(plan.routes))
    Z = [min(distance), min(pay), min(NV)]
    return Z


def update_Z(Z, plan):
    if plan.distance < Z[0]:
        Z[0] = plan.distance
    if plan.pay < Z[1]:
        Z[1] = plan.pay
    if len(plan.routes) < Z[2]:
        Z[2] = len(plan.routes)


def Tchebycheff_dist(w0, f0, z0):
    # 计算切比雪夫距离
    return w0 * abs(f0 - z0)


def cal_tchbycheff(plan, weigh_vectors, idx, Z):
    # idx：X在种群中的位置
    # 计算X的切比雪夫距离（与理想点Z的）
    max = 0
    w = weigh_vectors.W[idx]
    F_X = [plan.distance, plan.pay, len(plan.routes)]
    for i in range(3):
        fi = Tchebycheff_dist(w[i], F_X[i], Z[i])
        if fi > max:
            max = fi
    return max
