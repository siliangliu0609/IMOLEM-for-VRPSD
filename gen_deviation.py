import random

tar = 'c101'

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
