import os
import multiprocessing

pythonpath = "D:\\Workspace\\virtualenvs\\sci\\Scripts\\python.exe"
CPUcore = 5

modes = ['lem', 'moea', 'lemV1', 'lemV2', 'lemV3', 'lemNoL']
datasets = ['dt86', 'c101', 'c201', 'r101', 'r201', 'rc101', 'rc201']
#datasets = ['dt86']
#datasets = ['c101 DR', 'c101 DV', 'c101 RV', 'c101 D', 'c101 R', 'c101 V']

pre = pythonpath+' main.py evo'

if __name__ == '__main__':
    p = multiprocessing.Pool(CPUcore)
    for mode in modes:
        for dataset in datasets:
            p.apply_async(os.system, (pre+' '+mode+' '+dataset,))
    p.close()
    p.join()
