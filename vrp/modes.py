import random
from sklearn import tree
from collections import deque

from . import util
from .vrpclass import VectorPlan


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
        print('moea iter {} at {}...'.format(iter, problem.name))

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
            Q = util.pareto_sort(Q, evo_param.size)

        P = util.pareto_sort(P, evo_param.size)

        if iter != 0:
            elite = [plan.copy() for plan in util.pareto_sort(Q, 0.03*evo_param.size, 3)]
            P = P[0:len(P)-len(elite)]
            P.extend(elite)

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
            converge_trace_all.append(util.show_result(Q, evo_param.N, problem)[0])
            converge_trace_first.append(util.show_result(util.pareto_first(Q), evo_param.N, problem)[0])
            Q_trace.append([plan.copy() for plan in Q])

    return Q, Q_trace, converge_trace_all, converge_trace_first


def lem(evo_param, problem):
    if evo_param.MOmode != 'DRV':
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
            variety = ''
        elif evo_param.spec_init == False and evo_param.spec_inst == True:
            variety = 'V1'
        elif evo_param.spec_init == True and evo_param.spec_inst == False:
            variety = 'V2'
        else:
            variety = 'V3'
        if evo_param.no_tree == True and evo_param.spec_init == True and evo_param.spec_inst == True:
            variety = 'NoL'
        print('lem{} iter {} at {}...'.format(variety, iter, problem.name))

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
            Q = util.pareto_sort(Q, evo_param.size, MOmode=evo_param.MOmode)

        if len(evo_param.MOmode) == 1:
            P = util.target_sort(P, evo_param.size, evo_param.MOmode)
        else:
            P = util.pareto_sort(P, evo_param.size, MOmode=evo_param.MOmode)

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
            result = util.show_result(Q, evo_param.N, problem)[0]
            converge_trace_all.append(result)
            converge_trace_first.append(util.show_result(util.pareto_first(Q), evo_param.N, problem)[0])
            Q_trace.append([plan.copy() for plan in Q])

    #tree_str = tree.export_text(clf, feature_names=['customer '+str(i+1) for i in range(0, len(customers)-1)])
    # print(tree_str)
    # exit()

    return Q, Q_trace, converge_trace_all, converge_trace_first


def random_evo(evo_param, problem):
    P = util.initialization(problem, evo_param.size, 100)
    Q = []

    for iter in range(evo_param.maxiter):
        print('random iter {} at {}...'.format(iter, problem.name))

        for cus in problem.customers:
            cus.generate_actual_demand(evo_param.N)
        for plan in P:
            plan.RSM(evo_param.N, problem)

        Q.extend([plan.copy() for plan in P])
        Q = util.deduplicate(Q)
        if len(Q) > evo_param.size:
            Q = util.pareto_sort(Q, evo_param.size)

        P = util.initialization(problem, evo_param.size, 100)

    return Q


def lem_explore(evo_param, problem):
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

    #high_part = int(0.3*evo_param.size)
    #low_part = int(0.3*evo_param.size)

    #clf = tree.DecisionTreeClassifier()
    # vectors = []  # deque(maxlen=600)
    # category = []  # deque(maxlen=600)

    for iter in range(evo_param.maxiter):
        if evo_param.spec_init == True and evo_param.spec_inst == True:
            variety = ''
        elif evo_param.spec_init == False and evo_param.spec_inst == True:
            variety = ' v1'
        elif evo_param.spec_init == True and evo_param.spec_inst == False:
            variety = ' v2'
        else:
            variety = ' v3'
        print('lem{} iter {} at {}...'.format(variety, iter, problem.name))

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
            Q = util.pareto_sort(Q, evo_param.size, MOmode=evo_param.MOmode)

        if len(evo_param.MOmode) == 1:
            P = util.target_sort(P, evo_param.size, evo_param.MOmode)
        else:
            P = util.pareto_sort(P, evo_param.size, MOmode=evo_param.MOmode)

        if not evo_param.no_tree:
            #Hgroup = P[:high_part]
            #Lgroup = P[-low_part:]

            # for c in Hgroup:
            #    vectors.append(VectorPlan(problem.customers, c).vector)
            #    category.append(1)
            # for c in Lgroup:
            #    vectors.append(VectorPlan(problem.customers, c).vector)
            #    category.append(0)

            #clf.fit(vectors, category)

            newP = util.initialization(problem, evo_param.size, max_route)

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
            result = util.show_result(Q, evo_param.N, problem)[0]
            converge_trace_all.append(result)
            converge_trace_first.append(util.show_result(util.pareto_first(Q), evo_param.N, problem)[0])
            Q_trace.append([plan.copy() for plan in Q])

    #tree_str = tree.export_text(clf, feature_names=['customer '+str(i+1) for i in range(0, len(customers)-1)])
    # print(tree_str)
    # exit()

    return Q, Q_trace, converge_trace_all, converge_trace_first
