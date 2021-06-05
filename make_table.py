import sys

arglist = ['lem_dar', 'mo', 'noL', 'v123']

if sys.argv[1].isnumeric():
    mode = int(sys.argv[1])
else:
    mode = arglist.index(sys.argv[1])

if mode == 0:

    filenames = ['result/c101/lem.txt', 'result/c101/dar.txt', 'result/c201/lem.txt', 'result/c201/dar.txt', 'result/r101/lem.txt', 'result/r101/dar.txt', 'result/r201/lem.txt', 'result/r201/dar.txt', 'result/rc101/lem.txt', 'result/rc101/dar.txt', 'result/rc201/lem.txt', 'result/rc201/dar.txt']

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

    filenames = ['result/c101/lem.txt', 'result/c101/lem_no_tree.txt', 'result/c201/lem.txt', 'result/c201/lem_no_tree.txt', 'result/r101/lem.txt', 'result/r101/lem_no_tree.txt', 'result/r201/lem.txt', 'result/r201/lem_no_tree.txt', 'result/rc101/lem.txt', 'result/rc101/lem_no_tree.txt', 'result/rc201/lem.txt', 'result/rc201/lem_no_tree.txt']

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
    filenames = ['result/'+datamap+'/lem.txt', 'result/'+datamap+'/lemv1.txt', 'result/'+datamap+'/lemv2.txt', 'result/'+datamap+'/lemv3.txt']

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
