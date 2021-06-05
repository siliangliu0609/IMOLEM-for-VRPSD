import sys

import vrp.plot as pl

arglist = ['allp', 'moea', 'noLearn', 'v123', 'lastp']

if sys.argv[1].isnumeric():
    mode = int(sys.argv[1])
else:
    mode = arglist.index(sys.argv[1])

if mode == 0:

    datamaps = ['c101']
    #modes = ['lem', 'lem_DRV_DR', 'lem_DRV_DV', 'lem_DRV_RV', 'lem_DRV_D', 'lem_DRV_R', 'lem_DRV_V', ]
    modes = ['moea']

    pl.plot_population_trace(datamaps, modes, '_trace')

elif mode == 1:

    datamaps = ['c101', 'c201', 'r101', 'r201', 'rc101', 'rc201']
    #datamaps = ['c201']
    modes = ['lem', 'dar']
    labels = ['IMOLEM', 'MOEA']

    titles = ['Travel distance', 'Driver remuneration', 'Travel distance * Driver remuneration']
    save = ['moea_distance', 'moea_pay', 'moea_product']

    trace = 'all'
    linestyles = ['-', ':', '--', '-.']

    pl.plot_trace(datamaps, modes, labels, titles, save, trace, linestyles)

elif mode == 2:

    datamaps = ['c101', 'c201', 'r101', 'r201', 'rc101', 'rc201']
    modes = ['lem', 'lem_no_tree']
    labels = ['IMOLEM', 'IMOLEM-dtc']

    titles = ['Travel distance', 'Driver remuneration', 'Travel distance * Driver remuneration']
    save = ['noL_distance', 'noL_pay', 'noL_product']

    trace = 'all'
    linestyles = ['-', ':', '--', '-.']

    pl.plot_trace(datamaps, modes, labels, titles, save, trace, linestyles)

elif mode == 3:

    datamaps = ['c101', 'c201', 'r101', 'r201', 'rc101', 'rc201']
    #datamaps = ['c201']
    modes = ['lem', 'lemv1', 'lemv2', 'lemv3']
    labels = ['IMOLEM', 'Variant-I', 'Variant-II', 'Variant-III']

    titles = ['Travel distance', 'Driver remuneration', 'Travel distance * Driver remuneration']
    save = ['v123_distance', 'v123_pay', 'v123_product']

    trace = 'all'
    linestyles = ['-', ':', '--', '-.']

    pl.plot_trace(datamaps, modes, labels, titles, save, trace, linestyles)

elif mode == 4:

    datamaps = ['dt86']
    #modes = ['lem', 'lem_DRV_DR', 'lem_DRV_DV', 'lem_DRV_RV', 'lem_DRV_D', 'lem_DRV_R', 'lem_DRV_V', ]
    modes = ['lem', 'moea']

    pl.plot_population_last(datamaps, modes)
