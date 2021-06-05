import sys
import pickle
import os

import vrp.modes as modes
import vrp.util as util
import vrp.vrpclass as vrpclass

# 输入参数
dataset = sys.argv[1]  # c101, dt86...
mode = sys.argv[2]  # lem, moea...
extra_name = ''
if len(sys.argv) > 3:  # DR, temp...
    extra_name = '_'+'_'.join(sys.argv[3:])
MOmode = 'DRV'
if len(sys.argv) > 3:
    if sys.argv[3] in ['DR', 'DV', 'RV', 'D', 'R', 'V']:
        MOmode = sys.argv[3]
        extra_name = '_DRV'+extra_name

# 设置参数
trace = False
size = 100
maxiter = 100
N = 10
normal_hours = 8
normal_salary = 10
over_salary = 20
standard_deviation_file = 'data/standard_deviation.txt'

#解析参数
map_file = 'data/{}.txt'.format(dataset)
if dataset == 'dt86':
    map_type = 'dt86'
else:
    map_type = 'solomon'
spec_init = True
spec_inst = True
no_tree = False
if mode == 'lemv1':
    spec_init = False
elif mode == 'lemv2':
    spec_inst = False
elif mode == 'lemv3':
    spec_init = False
    spec_inst = False
elif mode == 'lem_no_tree':
    no_tree = True

# 调用流程
problem = vrpclass.Problem(map_file, map_type, normal_hours, normal_salary, over_salary, standard_deviation_file, standard_deviation_target=dataset)
problem.read_data()

evo_param = vrpclass.Evo_param(size=size, maxiter=maxiter, N=N, trace=trace, MOmode=MOmode, spec_init=spec_init, spec_inst=spec_inst, no_tree=no_tree)

Q, Q_trace, converge_trace_all, converge_trace_first = eval('modes.{mode}(evo_param, problem)'.format(mode=mode))

util.check_chro_legal(Q, problem.customers)

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

out_file.write('All solutions:\n'+util.cal_result(Q, evo_param.N, problem)[1]+'\n\n')
Qfirst = util.pareto_first(Q)
out_file.write('Non-dominated solutions:\n'+util.cal_result(Qfirst, evo_param.N, problem)[1]+'\n\n')

for num, chro in enumerate(Q):
    if num == len(Qfirst):
        out_file.write('-'*20+'Above solutions are non-dominated.'+'-'*20+'\n\n')
    out_file.write(str(chro)+'\n\n')

for t in converge_trace_all:
    trace_all_file.write("{} {} {} {} {}\n".format(t[0], t[1], t[2], t[3], t[4]))
for t in converge_trace_first:
    trace_first_file.write("{} {} {} {} {}\n".format(t[0], t[1], t[2], t[3], t[4]))
