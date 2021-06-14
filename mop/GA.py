# GA操作代码来源：https://blog.csdn.net/jiang425776024/article/details/84635353

import sys
import random
import numpy as np
import matplotlib.pyplot as plt
from abc import abstractmethod

import vrp.util as util
from . import moead, mrdl


class ZDT:
    @classmethod
    def objective(cls, x):
        f1x = cls.f1(x)
        f2x = cls.g(x)*cls.h(f1x, cls.g(x))
        return f1x, f2x

    @abstractmethod
    def f1(x):
        pass

    @abstractmethod
    def g(x):
        pass

    @abstractmethod
    def h(f1, g):
        pass


class ZDT1(ZDT):
    dimension = 30
    func_num = 2
    bound = [0, 1]

    def f1(x):
        return x[0]

    def g(x):
        gx = 1+9*(np.sum(x[1:], axis=0)/(x.shape[0]-1))
        return gx

    def h(f1, g):
        return 1-np.sqrt(f1/g)


class Solution:
    def __init__(self, x: np.ndarray, problem: ZDT1) -> None:
        self.x = x
        self.problem = problem

    def get_objective(self):
        return self.problem.objective(self.x)

    def cal_difference(self, other_plan):
        objective1 = np.array(self.get_objective())
        objective2 = np.array(other_plan.get_objective())
        diff_vec = objective1-objective2
        return (np.sum(diff_vec**2))**0.5

    def equal(self, other):
        assert(len(self.x) == len(other.x))
        for a, b in zip(self.x, other.x):
            if a != b:
                return False
        return True

    def copy(self):
        return type(self)(np.copy(self.x), self.problem)

    def mutation(self):
        # 突变个体的策略2
        dj = 0
        uj = np.random.rand()
        if uj < 0.5:
            dj = (2 * uj) ** (1 / 6) - 1
        else:
            dj = 1 - 2 * (1 - uj) ** (1 / 6)
        self.x = self.x + dj
        self.x[self.x > self.problem.bound[1]] = self.problem.bound[1]
        self.x[self.x < self.problem.bound[0]] = self.problem.bound[0]

    def crossover(self, y2):
        # 交叉个体的策略2
        var_num = self.problem.dimension
        yj = 0
        uj = np.random.rand()
        if uj < 0.5:
            yj = (2*uj)**(1/3)
        else:
            yj = (1/(2*(1-uj)))**(1 / 3)
        self.x = 0.5*(1+yj)*self.x+(1-yj)*y2.x
        y2.x = 0.5*(1-yj)*self.x+(1+yj)*y2.x
        self.x[self.x > self.problem.bound[1]] = self.problem.bound[1]
        self.x[self.x < self.problem.bound[0]] = self.problem.bound[0]
        y2.x[y2.x > self.problem.bound[1]] = self.problem.bound[1]
        y2.x[y2.x < self.problem.bound[0]] = self.problem.bound[0]

    def cross_mutation(self, p2):
        y1 = self.copy()
        y2 = p2.copy()
        c_rate = 1
        m_rate = 0.5
        if np.random.rand() < c_rate:
            y1.crossover(y2)
        if np.random.rand() < m_rate:
            y1.mutate()
            y2.mutate()
        return y1, y2


class Evolution:
    def __init__(self, problem: ZDT1, size: int, maxiter: int) -> None:
        self.problem = problem
        self.size = size
        self.maxiter = maxiter

    def creat_child(self):
        # 创建一个个体
        child = self.problem.bound[0]+(self.problem.bound[1]-self.problem.bound[0])*np.random.rand(self.problem.dimension)
        return Solution(child, self.problem)

    def creat_pop(self, size):
        # 创建moead.Pop_size个种群
        P = []
        while len(P) != size:
            X = self.creat_child()
            P.append(X)
        return P

    def run_moead(self):

        P = self.creat_pop(self.size)

        weigh_vectors = moead.Weight_vector(99, 2, 20)
        weigh_vectors.cal_B()

        Z = moead.initialize_Z(P, 2)

        for iter in range(self.maxiter):
            print('iter {}...'.format(iter))
            plot_P(P, iter)

            C = []

            for index in range(self.size):
                k, j = weigh_vectors.pick_x_neighbor_of_i(index, 2)
                plan_k = P[k].copy()
                plan_j = P[j].copy()
                plan_k.crossover(plan_j)
                plan_k.mutation()
                new_plan = plan_k
                moead.update_Z(Z, new_plan, 2)
                if moead.cal_tchbycheff(new_plan, weigh_vectors, index, Z, 2) <= moead.cal_tchbycheff(P[index], weigh_vectors, index, Z, 2):
                    C.append(new_plan)
                else:
                    C.append(P[index])

            P = C

        return P

    def run_mrdl(self):

        P = self.creat_pop(self.size)

        weigh_vectors = moead.Weight_vector(99, 2, 20)
        weigh_vectors.cal_B()

        gamma = 20

        Z = moead.initialize_Z(P, 2)

        for iter in range(self.maxiter):
            print('iter {}...'.format(iter))
            plot_P(P, iter)

            C = []

            for index in range(self.size):
                k, j = weigh_vectors.pick_x_neighbor_of_i(index, 2)
                plan_k = P[k].copy()
                plan_j = P[j].copy()
                plan_k.crossover(plan_j)
                plan_k.mutation()
                new_plan = plan_k
                moead.update_Z(Z, new_plan, 2)
                C.append(new_plan)

            P = mrdl.environmental_selection(P, C, weigh_vectors, Z, gamma, 2)

        return P

    def run_moea(self):

        P = self.creat_pop(self.size)
        Q = []

        for iter in range(self.maxiter):
            print('iter {}...'.format(iter))

            Q.extend([plan.copy() for plan in P])
            if len(Q) > self.size:
                Q = util.pareto_sort(Q, self.size)
            plot_P(Q, iter)

            P = util.pareto_sort(P, self.size)

            pk_win = util.pk(self.size, 2)
            crossoverP = []
            for i in pk_win:
                crossoverP.append(P[i].copy())
            for i in range(0, self.size-1, 2):
                if random.random() < 0.7:
                    crossoverP[i].crossover(crossoverP[i+1])
            P = crossoverP

            for plan in P:
                plan.mutation()

        return Q

    def run_lem(self):

        P = self.creat_pop(self.size)
        Q = []

        for iter in range(self.maxiter):
            print('iter {}...'.format(iter))

            Q.extend([plan.copy() for plan in P])
            if len(Q) > self.size:
                Q = util.pareto_sort(Q, self.size)

            plot_P(Q, iter)

            newP = self.creat_pop(self.size//2)
            good = [plan.copy() for plan in Q[:self.size//2]]
            for plan in good:
                plan.mutation()
            newP.extend(good)
            P = newP

        return Q


def plot_P(P, iter):
    plt.ion()
    x = []
    y = []
    for sol in P:
        x.append(sol.get_objective()[0])
        y.append(sol.get_objective()[1])
    plt.title('iter:{} sol:{}'.format(iter, len(P)))
    plt.scatter(x, y)
    plt.pause(0.01)
    plt.clf()


def plot_P_long(P):
    plt.ioff()
    x = []
    y = []
    for sol in P:
        x.append(sol.get_objective()[0])
        y.append(sol.get_objective()[1])
    plt.title('result sol:{}'.format(len(P)))
    plt.scatter(x, y)
    plt.show()


if __name__ == '__main__':
    evo = Evolution(ZDT1, 100, 100)
    P = eval('evo.run_{}()'.format(sys.argv[1]))
    plot_P_long(P)
