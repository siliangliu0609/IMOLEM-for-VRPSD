import sys

import vrp.vrpclass as vrpclass

dataset = sys.argv[1]

standard_deviation_file = 'data/standard_deviation.txt'
map_file = 'data/{}.txt'.format(dataset)
if dataset == 'dt86':
    map_type = 'dt86'
else:
    map_type = 'solomon'

problem = vrpclass.Problem(map_file, map_type, standard_deviation_file=standard_deviation_file, standard_deviation_target=dataset)
problem.read_data()

xs = []
ys = []

for cus in problem.customers:
    xs.append(cus.x)
    ys.append(cus.y)

max_x = max(xs)
max_y = max(ys)

double_diagonal = (max_x**2+max_y**2)**0.5*2

print('max_x = {}\nmax_y = {}\ndouble_diagonal = {}'.format(max_x, max_y, double_diagonal))
