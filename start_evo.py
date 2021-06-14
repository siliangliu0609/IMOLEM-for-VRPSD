import os
import multiprocessing

CPUcore = 5

command = []

pre = 'python main.py evo'

modes = ['lem', 'moea', 'dbmoea', 'lemV1', 'lemV2', 'lemV3', 'lemNoL']
datasets = ['dt86', 'c101', 'c201', 'r101', 'r201', 'rc101', 'rc201']
for mode in modes:
    for dataset in datasets:
        command.append(pre+' '+mode+' '+dataset)

modes = ['lem']
datasets = ['dt86', 'c101', 'c201', 'r101', 'r201', 'rc101', 'rc201']
MOmodes = ['DR', 'DV', 'RV', 'D', 'R', 'V']
for mode in modes:
    for dataset in datasets:
        for MOmode in MOmodes:
            command.append(pre+' '+mode+' '+dataset+' '+MOmode)

# for cmd in command:
#    print(cmd)
# exit()

if __name__ == '__main__':
    p = multiprocessing.Pool(CPUcore)
    for cmd in command:
        p.apply_async(os.system, (cmd,))
    p.close()
    p.join()
