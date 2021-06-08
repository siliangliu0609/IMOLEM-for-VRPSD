import os
import sys
import multiprocessing

pythonpath = "D:\\Workspace\\virtualenvs\\sci\\Scripts\\python.exe"
CPUcore = 5

task = int(sys.argv[1])

if task == 0:
    modes = ['lem', 'moea', 'lemV1', 'lemV2', 'lemV3', 'lemNoL']
    datasets = ['dt86', 'c101', 'c201', 'r101', 'r201', 'rc101', 'rc201']
    MOmodes = ['']
elif task == 1:
    modes = ['lem']
    datasets = ['dt86', 'c101', 'c201', 'r101', 'r201', 'rc101', 'rc201']
    MOmodes = ['DR', 'DV', 'RV', 'D', 'R', 'V']

pre = pythonpath+' main.py evo'

if __name__ == '__main__':
    p = multiprocessing.Pool(CPUcore)
    for mode in modes:
        for dataset in datasets:
            for MOmode in MOmodes:
                p.apply_async(os.system, (pre+' '+mode+' '+dataset+' '+MOmode,))
    p.close()
    p.join()
