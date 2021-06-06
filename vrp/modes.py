from collections import deque
from sklearn import tree
import random

from .vrpclass import VectorPlan
from . import util


def moea(evo_param, problem):
    Q_trace = []
    converge_trace_all = []
    converge_trace_first = []

    P = []  # 进化种群
    first_plan = util.build_first_plan(problem)
    P.append(first_plan)
    max_route = len(first_plan.routes)
    P.extend(util.initialization(problem, evo_param.size-1, max_route))
    Q = []  # 归档种群

    for iter in range(evo_param.maxiter):
        print('moea iter {}...'.format(iter))

        local_search = False
        if iter % 50 == 0:
            local_search = True

        for cus in problem.customers:
            cus.generate_actual_demand(evo_param.N)
        for plan in P:
            plan.RSM(evo_param.N, problem)  # 在计算完RSM目标值后，应重新将所有路线的客户需求设为平均值
            for route in plan.routes:
                route.set_mean_demand()

        Q.extend([plan.copy() for plan in P])
        #Q = util.deduplicate_objective(Q)
        Q = util.deduplicate(Q)
        if len(Q) > evo_param.size:
            Q = util.pareto_sort(Q, evo_param.size, 'DRV')

        P = util.pareto_sort(P, evo_param.size, 'DRV')
        #rank_P = dict(zip(range(len(P)), P))

        # if RSMmode == 'gen':
        #    if iter % M == 0:
        #        for cus in customers:
        #            cus.generate_actual_demand(N)
        #    for plan in Q:
        #        plan.RSM(N)
        # elif RSMmode == 'alter':
        #    if iter % (2*M) == 0:
        #        for cus in customers:
        #            cus.generate_actual_demand(N)
        #    if iter % (2*M) == M:
        #        for cus in customers:
        #            cus.actual_demand = [cus.mean]
        #    for plan in Q:
        #        if iter % 2*M < M:
        #            plan.RSM(N)
        #        else:
        #            plan.RSM(1)
        # elif RSMmode == 'determine':
        #    if iter == 0:
        #        for cus in customers:
        #            cus.actual_demand = [cus.mean]
        #    for plan in Q:
        #        plan.RSM(1)
        # else:
        #    print("wrong RSMmode")
        #    exit()

        pk_win = util.pk(len(P), 2)
        crossoverP = []
        for i in pk_win:
            crossoverP.append(P[i].copy())
        for i in range(0, len(P)-1, 2):
            if random.random() < 0.7:
                crossoverP[i].route_crossover(crossoverP[i+1], 0.3)
        P = crossoverP

        for plan in P:
            plan.mutation(problem, 0.4, 0.5, 0.5, 0.3)

            if local_search:
                for route in plan.routes:
                    route.set_mean_demand()
                plan.local_search_exploitation_SPS(problem)
                plan.local_search_exploitation_WDS(problem)

        if evo_param.trace:
            converge_trace_all.append(util.cal_result(Q, evo_param.N, problem)[0])
            converge_trace_first.append(util.cal_result(util.pareto_first(Q), evo_param.N, problem)[0])
            Q_trace.append([plan.copy() for plan in Q])

    return Q, Q_trace, converge_trace_all, converge_trace_first


def lem(evo_param, problem):
    print('MOmode is {}'.format(evo_param.MOmode))

    Q_trace = []
    converge_trace_all = []
    converge_trace_first = []

    P = []
    if evo_param.spec_init:
        first_plan = util.build_first_plan(problem)
        P.append(first_plan)
        max_route = len(first_plan.routes)
        P.extend(util.initialization(problem, evo_param.size-1, max_route))
    else:
        max_route = len(problem.customers)-1
        P.extend(util.initialization(problem, evo_param.size, max_route))
    Q = []

    high_part = int(0.3*evo_param.size)
    low_part = int(0.3*evo_param.size)

    clf = tree.DecisionTreeClassifier()
    vectors = []  # deque(maxlen=600)
    category = []  # deque(maxlen=600)

    for iter in range(evo_param.maxiter):
        if evo_param.spec_init == True and evo_param.spec_inst == True:
            print('lem iter {}...'.format(iter))
        elif evo_param.spec_init == False and evo_param.spec_inst == True:
            print('lem v1 iter {}...'.format(iter))
        elif evo_param.spec_init == True and evo_param.spec_inst == False:
            print('lem v2 iter {}...'.format(iter))
        else:
            print('lem v3 iter {}...'.format(iter))

        local_search = False
        if iter % 50 == 0:
            local_search = True

        if iter % 20 == 0:
            vectors = []
            category = []

        for cus in problem.customers:
            cus.generate_actual_demand(evo_param.N)
        for plan in P:
            plan.RSM(evo_param.N, problem)  # 问题：在计算完RSM目标值后，应重新将所有客户需求设为平均值
            for route in plan.routes:
                route.set_mean_demand()

        Q.extend([plan.copy() for plan in P])
        #Q = util.deduplicate_objective(Q)
        Q = util.deduplicate(Q)
        if len(Q) > evo_param.size:
            Q = util.pareto_sort(Q, evo_param.size, 'DRV')

        if len(evo_param.MOmode) == 1:
            P = util.target_sort(P, evo_param.size, evo_param.MOmode)
        else:
            P = util.pareto_sort(P, evo_param.size, evo_param.MOmode)

        if not evo_param.no_tree:
            Hgroup = P[:high_part]
            Lgroup = P[-low_part:]

            for c in Hgroup:
                vectors.append(VectorPlan(problem.customers, c).vector)
                category.append(1)
            for c in Lgroup:
                vectors.append(VectorPlan(problem.customers, c).vector)
                category.append(0)

            clf.fit(vectors, category)

            newP = util.instantiating(problem, evo_param.size, max_route, clf)

            if evo_param.spec_inst:
                good = [plan.copy() for plan in Q]
                for plan in newP:
                    plan.mutation(problem, 0.4, 0.5, 0.5, 0.3)
                for plan in good:
                    plan.mutation(problem, 1, 0.5, 0.5, 0.3)
                newP.extend(good)

        else:
            newP = [plan.copy() for plan in P]
            for plan in newP:
                plan.mutation(problem, 0.4, 0.5, 0.5, 0.3)

        P = newP

        if evo_param.trace:
            result = util.cal_result(Q, evo_param.N, problem)[0]
            converge_trace_all.append(result)
            converge_trace_first.append(util.cal_result(util.pareto_first(Q), evo_param.N, problem)[0])
            Q_trace.append([plan.copy() for plan in Q])

    #tree_str = tree.export_text(clf, feature_names=['customer '+str(i+1) for i in range(0, len(customers)-1)])
    # print(tree_str)
    # exit()

    return Q, Q_trace, converge_trace_all, converge_trace_first


def random_mode(evo_param, problem):
    P = util.initialization(problem, evo_param.size, 100)
    Q = []

    for iter in range(evo_param.maxiter):
        print('random iter {}...'.format(iter))

        Q.extend(P)

        for cus in problem.customers:
            cus.generate_actual_demand(10)
        for plan in Q:
            plan.RSM(10, problem)
            for route in plan.routes:
                route.set_mean_demand()

        Q = util.pareto_sort(Q, evo_param.size, 'DRV')
        P = util.initialization(problem, evo_param.size, 100)

    return Q


def old_moea(evo_param, problem):
    Q_trace = []
    converge_trace_all = []
    converge_trace_first = []

    P = []
    first_plan = util.build_first_plan(problem)
    P.append(first_plan)
    max_route = len(first_plan.routes)
    P.extend(util.initialization(problem, evo_param.size-1, max_route))
    Q = []

    for iter in range(evo_param.maxiter):
        print('darwin iter {}...'.format(iter))

        #local_search = False
        # if iter % 10 == 0:
        #    local_search = True

        Q.extend(P)
        Q = util.deduplicate(Q)

        for cus in problem.customers:
            cus.generate_actual_demand(evo_param.N)
        for plan in Q:
            plan.RSM(evo_param.N, problem)  # 问题：在计算完RSM目标值后，应重新将所有客户需求设为平均值
            for route in plan.routes:
                route.set_mean_demand()

        Q = util.pareto_sort(Q, evo_param.size, 'DRV')
        P = [plan.copy() for plan in Q]
        random.shuffle(P)
        for i in range(0, len(P)-1, 2):
            if random.random() < 0.7:
                P[i].route_crossover(P[i+1], 0.3)

        for plan in P:
            plan.mutation(problem, 0.4, 0.5, 0.5, 0.3)

            # for route in plan.routes:
            #    route.set_mean_demand()
            # if local_search:
            #    plan.local_search_exploitation_SPS()
            #    plan.local_search_exploitation_WDS()

        if evo_param.trace:
            converge_trace_all.append(util.cal_result(Q, evo_param.N, problem)[0])
            converge_trace_first.append(util.cal_result(util.pareto_first(Q), evo_param.N, problem)[0])
            Q_trace.append([plan.copy() for plan in Q])

    return Q, Q_trace, converge_trace_all, converge_trace_first


def old_lem(evo_param, problem):
    print('MOmode is {}'.format(evo_param.MOmode))

    Q_trace = []
    converge_trace_all = []
    converge_trace_first = []

    P = []
    if evo_param.spec_init:
        first_plan = util.build_first_plan(problem)
        P.append(first_plan)
        max_route = len(first_plan.routes)
        P.extend(util.initialization(problem, evo_param.size-1, max_route))
    else:
        max_route = len(problem.customers)-1
        P.extend(util.initialization(problem, evo_param.size, max_route))
    Q = []

    high_part = int(0.3*evo_param.size)
    low_part = int(0.3*evo_param.size)

    clf = tree.DecisionTreeClassifier()
    vectors = deque(maxlen=600)
    category = deque(maxlen=600)

    for iter in range(evo_param.maxiter):
        if evo_param.spec_init == True and evo_param.spec_inst == True:
            print('learn iter {}...'.format(iter))
        elif evo_param.spec_init == False and evo_param.spec_inst == True:
            print('learn v1 iter {}...'.format(iter))
        elif evo_param.spec_init == True and evo_param.spec_inst == False:
            print('learn v2 iter {}...'.format(iter))
        else:
            print('learn v3 iter {}...'.format(iter))

        # if iter % 20 == 0:
        #    vectors = []
        #    category = []

        Q.extend(P)
        Q = util.deduplicate(Q)

        for cus in problem.customers:
            cus.generate_actual_demand(evo_param.N)
        for plan in Q:
            plan.RSM(evo_param.N, problem)  # 问题：在计算完RSM目标值后，应重新将所有客户需求设为平均值
            for route in plan.routes:
                route.set_mean_demand()

        if len(evo_param.MOmode) == 1:
            Q = util.target_sort(Q, evo_param.size, evo_param.MOmode)
        else:
            Q = util.pareto_sort(Q, evo_param.size, evo_param.MOmode)

        if not evo_param.no_tree:
            Hgroup = Q[:high_part]
            Lgroup = Q[-low_part:]

            for c in Hgroup:
                vectors.append(VectorPlan(problem.customers, c).vector)
                category.append(1)
            for c in Lgroup:
                vectors.append(VectorPlan(problem.customers, c).vector)
                category.append(0)

            clf.fit(vectors, category)

            P = util.instantiating(problem, evo_param.size, max_route, clf)

            if evo_param.spec_inst:
                origin = [plan.copy() for plan in Q]
                for plan in origin:
                    plan.mutation(problem, 1, 0.5, 0.5, 0.3)
                for plan in P:
                    plan.mutation(problem, 0.4, 0.5, 0.5, 0.3)
                P.extend(origin)
        else:
            #P = util.initialization(customers, C, B, size, max_route)
            P = [plan.copy() for plan in Q]
            for plan in P:
                plan.mutation(problem, 0.4, 0.5, 0.5, 0.3)

        if evo_param.trace:
            result = util.cal_result(Q, evo_param.N, problem)[0]
            converge_trace_all.append(result)
            converge_trace_first.append(util.cal_result(util.pareto_first(Q), evo_param.N, problem)[0])
            Q_trace.append([plan.copy() for plan in Q])

    #tree_str = tree.export_text(clf, feature_names=['customer '+str(i+1) for i in range(0, len(customers)-1)])
    # print(tree_str)
    # exit()

    return Q, Q_trace, converge_trace_all, converge_trace_first
