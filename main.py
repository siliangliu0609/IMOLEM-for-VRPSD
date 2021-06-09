import os
import sys
import pickle
import random

import vrp.vrpclass as vrpclass
import vrp.modes as modes
import vrp.util as util
import vrp.plot as pl


def evo():
    # 输入参数
    mode = sys.argv[2]  # lem, moea...
    dataset = sys.argv[3]  # c101, dt86...
    extra_name = ''
    if len(sys.argv) > 4:  # DR, temp...
        extra_name = '_'+'_'.join(sys.argv[4:])
    MOmode = 'DRV'
    if len(sys.argv) > 4:
        if sys.argv[4] in ['DR', 'DV', 'RV', 'D', 'R', 'V']:
            MOmode = sys.argv[4]
            extra_name = '_DRV'+extra_name

    # 设置参数
    trace = True
    size = 100
    maxiter = 200
    N = 10
    normal_hours = 8
    normal_salary = 10
    over_salary = 20
    standard_deviation_file = 'data/standard_deviation.txt'

    # 解析参数
    map_file = 'data/{}.txt'.format(dataset)
    if dataset == 'dt86':
        map_type = 'dt86'
    else:
        map_type = 'solomon'
    spec_init = True
    spec_inst = True
    no_tree = False
    tmp = None
    if mode in ['lemV1', 'lemV2', 'lemV3', 'lemNoL']:
        tmp = mode
        if mode == 'lemV1':
            spec_init = False
        elif mode == 'lemV2':
            spec_inst = False
        elif mode == 'lemV3':
            spec_init = False
            spec_inst = False
        elif mode == 'lemNoL':
            no_tree = True
        mode = 'lem'

    # 调用流程
    problem = vrpclass.Problem(map_file, map_type, normal_hours, normal_salary, over_salary, standard_deviation_file, standard_deviation_target=dataset, name=dataset+extra_name)
    problem.read_data()

    evo_param = vrpclass.Evo_param(size=size, maxiter=maxiter, N=N, trace=trace, MOmode=MOmode, spec_init=spec_init, spec_inst=spec_inst, no_tree=no_tree)

    Q, Q_trace, converge_trace_all, converge_trace_first = eval('modes.{}(evo_param, problem)'.format(mode))

    util.check_plan_legal(Q, problem.customers)

    if tmp != None:
        mode = tmp

    # 检查存结果的文件夹
    if not os.path.exists('result/'+dataset):
        os.mkdir('result/'+dataset)

    out_file = open('result/{}/{}{}.txt'.format(dataset, mode, extra_name), 'w')
    population_file = open('result/{}/{}{}_population.pickle'.format(dataset, mode, extra_name), 'wb')
    population_trace_file = open('result/{}/{}{}_population_trace.pickle'.format(dataset, mode, extra_name), 'wb')

    trace_all_file = open('result/{}/{}{}_trace_all.txt'.format(dataset, mode, extra_name), 'w')
    trace_first_file = open('result/{}/{}{}_trace_first.txt'.format(dataset, mode, extra_name), 'w')

    # 存储结果
    pickle.dump(Q, population_file)
    pickle.dump(Q_trace, population_trace_file)

    out_file.write('All solutions:\n'+util.show_result(Q, evo_param.N, problem)[1]+'\n\n')
    Qfirst = util.pareto_first(Q)
    out_file.write('Non-dominated solutions:\n'+util.show_result(Qfirst, evo_param.N, problem)[1]+'\n\n')

    for num, plan in enumerate(Q):
        if num == len(Qfirst):
            out_file.write('-'*20+'Above solutions are non-dominated.'+'-'*20+'\n\n')
        for route in plan:
            route.cal_restock_time_with_mean_demand(problem)
        out_file.write(str(plan)+'\n\n')

    for t in converge_trace_all:
        trace_all_file.write("{} {} {} {} {}\n".format(t[0], t[1], t[2], t[3], t[4]))
    for t in converge_trace_first:
        trace_first_file.write("{} {} {} {} {}\n".format(t[0], t[1], t[2], t[3], t[4]))


def fig():
    arg_list = ['allp', 'comparison', 'noLearn', 'v123', 'lastp']

    if sys.argv[2].isnumeric():
        mode = int(sys.argv[2])
    else:
        mode = arg_list.index(sys.argv[2])

    if mode == 0:

        #datamaps = ['c101', 'c201', 'r101', 'r201', 'rc101', 'rc201', 'dt86']
        datamaps = ['c101']
        modes = ['lem', 'moea', 'dbmoea', 'lem_DRV_DR', 'lem_DRV_DV', 'lem_DRV_RV', 'lem_DRV_D', 'lem_DRV_R', 'lem_DRV_V']
        #modes = ['lem', 'moea']

        pl.plot_population_trace(datamaps, modes)

    elif mode == 1:

        datamaps = ['c101', 'c201', 'r101', 'r201', 'rc101', 'rc201', 'dt86']
        #datamaps = ['dt86']
        modes = ['lem', 'moea', 'dbmoea']
        labels = ['IMOLEM', 'MOEA', 'DB-MOEA']

        titles = ['Travel distance', 'Driver remuneration', 'Travel distance * Driver remuneration']
        save = ['comparison_distance', 'comparison_pay', 'comparison_product']

        trace = 'all'
        linestyles = ['-', ':', '--', '-.']

        pl.plot_trace(datamaps, modes, labels, titles, save, trace, linestyles)

    elif mode == 2:

        datamaps = ['c101', 'c201', 'r101', 'r201', 'rc101', 'rc201', 'dt86']
        modes = ['lem', 'lemNoL']
        labels = ['IMOLEM', 'IMOLEM-dtc']

        titles = ['Travel distance', 'Driver remuneration', 'Travel distance * Driver remuneration']
        save = ['noL_distance', 'noL_pay', 'noL_product']

        trace = 'all'
        linestyles = ['-', ':', '--', '-.']

        pl.plot_trace(datamaps, modes, labels, titles, save, trace, linestyles)

    elif mode == 3:

        datamaps = ['c101', 'c201', 'r101', 'r201', 'rc101', 'rc201', 'dt86']
        modes = ['lem', 'lemV1', 'lemV2', 'lemV3']
        labels = ['IMOLEM', 'Variant-I', 'Variant-II', 'Variant-III']

        titles = ['Travel distance', 'Driver remuneration', 'Travel distance * Driver remuneration']
        save = ['v123_distance', 'v123_pay', 'v123_product']

        trace = 'all'
        linestyles = ['-', ':', '--', '-.']

        pl.plot_trace(datamaps, modes, labels, titles, save, trace, linestyles)

    elif mode == 4:

        #datamaps = ['dt86', 'c101', 'c201', 'r101', 'r201', 'rc101', 'rc201']
        datamaps = ['c101']
        modes = ['moea', 'lem', 'dbmoea']

        pl.plot_population_last(datamaps, modes)


def table():
    arglist = ['comparison', 'mo', 'noLearn', 'v123']

    if sys.argv[2].isnumeric():
        mode = int(sys.argv[2])
    else:
        mode = arglist.index(sys.argv[2])

    if mode == 0:

        filenames = ['result/c101/lem.txt', 'result/c101/moea.txt', 'result/c201/lem.txt', 'result/c201/moea.txt', 'result/r101/lem.txt', 'result/r101/moea.txt', 'result/r201/lem.txt', 'result/r201/moea.txt', 'result/rc101/lem.txt', 'result/rc101/moea.txt', 'result/rc201/lem.txt', 'result/rc201/moea.txt']

        retstr = ''

        for fn in filenames:
            f = open(fn)
            results = []
            for row, line in enumerate(f):
                if row < 10:
                    continue
                if row > 14:
                    break
                results.append(float(line.split()[-1]))
            retstr += '& {:.2f} & {:.2f} & {:.2f} & {:.2f} & {:.2f} \\\\\n'.format(*results)

        print(retstr)
        open('result/table.txt', 'w').write(retstr)

    elif mode == 1:

        datamap = 'rc201'
        filenames = ['result/'+datamap+'/lem.txt', 'result/'+datamap+'/lem_DRV_DR.txt', 'result/'+datamap+'/lem_DRV_DV.txt', 'result/'+datamap+'/lem_DRV_RV.txt', 'result/'+datamap+'/lem_DRV_D.txt', 'result/'+datamap+'/lem_DRV_R.txt', 'result/'+datamap+'/lem_DRV_V.txt']

        retstr = ''

        for fn in filenames:
            f = open(fn)
            results = []
            for row, line in enumerate(f):
                if row < 9:
                    continue
                if row > 14:
                    break
                results.append(float(line.split()[-1]))
            retstr += '& {:.0f} & {:.2f} & {:.2f} & {:.2f} & {:.2f} & {:.2f} \\\\\n'.format(*results)

        print(retstr)
        open('result/table.txt', 'w').write(retstr)

    elif mode == 2:

        filenames = ['result/c101/lem.txt', 'result/c101/lemNoL.txt', 'result/c201/lem.txt', 'result/c201/lemNoL.txt', 'result/r101/lem.txt', 'result/r101/lemNoL.txt', 'result/r201/lem.txt', 'result/r201/lemNoL.txt', 'result/rc101/lem.txt', 'result/rc101/lemNoL.txt', 'result/rc201/lem.txt', 'result/rc201/lemNoL.txt']

        retstr = ''

        for fn in filenames:
            f = open(fn)
            results = []
            for row, line in enumerate(f):
                if row < 10:
                    continue
                if row > 14:
                    break
                results.append(float(line.split()[-1]))
            retstr += '& {:.2f} & {:.2f} & {:.2f} & {:.2f} & {:.2f} \\\\\n'.format(*results)

        print(retstr)
        open('result/table.txt', 'w').write(retstr)

    elif mode == 3:

        datamap = 'rc201'
        filenames = ['result/'+datamap+'/lem.txt', 'result/'+datamap+'/lemV1.txt', 'result/'+datamap+'/lemV2.txt', 'result/'+datamap+'/lemV3.txt']

        retstr = ''

        for fn in filenames:
            f = open(fn)
            results = []
            for row, line in enumerate(f):
                if row < 10:
                    continue
                if row > 14:
                    break
                results.append(float(line.split()[-1]))
            retstr += '& {:.2f} & {:.2f} & {:.2f} & {:.2f} & {:.2f} \\\\\n'.format(*results)

        print(retstr)
        open('result/table.txt', 'w').write(retstr)


def gen_deviation():
    #tar = 'c101'
    tar = sys.argv[2]

    demands = []
    fp = open('data/{}.txt'.format(tar))
    for num, line in enumerate(fp.readlines()):
        if num <= 8:  # 跳过无关行
            continue
        demand = float(line.split()[3])
        demands.append(demand)

    standard_deviation = [random.uniform(0.1, 1/3*mean) for mean in demands]
    standard_deviation[0] = 0

    st_de_file = open('data/standard_deviation.txt', 'a')

    st_de_file.write(tar)
    for sd in standard_deviation:
        st_de_file.write(' '+str(sd))
    st_de_file.write('\n')


if __name__ == '__main__':
    task_list = ['evo', 'fig', 'table', 'gen_deviation']
    task_index = task_list.index(sys.argv[1])
    exec(sys.argv[1]+'()')
