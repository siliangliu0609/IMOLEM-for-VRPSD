import sys
import matplotlib.pyplot as plt

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

for cus in problem.customers:
    if cus.id == 0:
        plt.scatter(cus.x, cus.y, marker='^')
    else:
        plt.scatter(cus.x, cus.y)

plt.title(sys.argv[1])
plt.show()
