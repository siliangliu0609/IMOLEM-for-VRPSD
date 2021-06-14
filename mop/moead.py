# 来源：https://blog.csdn.net/jiang425776024/article/details/84635353

import numpy as np
import random


class Weight_vector:
    # 对m维空间，目标方向个数H
    def __init__(self, H=13, m=3, T_size=20):
        self.H = H
        self.m = m
        self.W = self.get_mean_vectors()
        self.T_size = T_size
        self.B = []  # 权重的T个邻居

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

    def get_mean_vectors(self):
        H = self.H
        m = self.m
        sequence = []
        for _ in range(H):
            sequence.append(0)
        for _ in range(m - 1):
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

    def cal_B(self):
        # 计算权重的T个邻居
        for bi in range(len(self.W)):
            Bi = self.W[bi]
            DIS = np.sum((self.W - Bi) ** 2, axis=1)
            B_T = np.argsort(DIS)
            # 第0个是自己（距离永远最小）
            B_T = B_T[1:self.T_size + 1]
            self.B.append(B_T)

    def pick_x_neighbor_of_i(self, i, x):
        neighbor = self.B[i].tolist()
        return random.sample(neighbor, x)


def initialize_Z(P, objective_num=3):
    objectives = []
    for _ in range(objective_num):
        objectives.append([])
    for plan in P:
        for ob_i in range(objective_num):
            objectives[ob_i].append(plan.get_objective()[ob_i])
    Z = []
    for ob_i in range(objective_num):
        Z.append(min(objectives[ob_i]))
    return Z


def update_Z(Z, plan, objective_num=3):
    plan_objective = plan.get_objective()
    for ob_i in range(objective_num):
        if plan_objective[ob_i] < Z[ob_i]:
            Z[ob_i] = plan_objective[ob_i]


def Tchebycheff_dist(w0, f0, z0):
    # 计算切比雪夫距离
    return w0 * abs(f0 - z0)


def cal_tchbycheff(plan, weigh_vectors, idx, Z, objective_num=3):
    # idx：X在种群中的位置
    # 计算X的切比雪夫距离（与理想点Z的）
    max = 0
    w = weigh_vectors.W[idx]
    F_X = plan.get_objective()
    for i in range(objective_num):
        fi = Tchebycheff_dist(w[i], F_X[i], Z[i])
        if fi > max:
            max = fi
    return max


if __name__ == '__main__':
    w = Weight_vector(99, 2, 20)
    print(w.W)
    print(len(w.W))
