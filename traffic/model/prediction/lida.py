import numpy as np
import pandas as pd
import math

def cal_dist(a, b):
    return math.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2)

id2coor = {}
geo = pd.read_csv('raw_data/METR_LA/METR_LA.geo')

predict = np.load('libcity/cache/83773/evaluate_cache/2022_10_13_19_50_44_DCRNN_METR_LA_predictions.npz', allow_pickle=True)
#print(predict['truth'][0][0])


for index, row in geo.iterrows():
    id = int(row['geo_id'])
    coor_str = row['coordinates'][1:-1]
    coor_split = coor_str.split(',')
    coor_float = (float(coor_split[0]), float(coor_split[1]))
    id2coor[id] = coor_float

choose_id = 772596
dist = [(cal_dist(id2coor[choose_id], id2coor[x]), x) for x in id2coor]
dist.sort()

pick_id = []
for i in range(1, 16):
    pick_id.append(dist[i][1])

#print(pick_id)

'''dyna = pd.read_csv('raw_data/METR_LA_ori/METR_LA.dyna')
gr = dyna.groupby(['entity_id'])
gr.apply(lambda _df: _df.sort_values('dyna_id'))
ndf = pd.DataFrame(columns=dyna.columns)
for eid, subdf in gr:
    subdf.reset_index(inplace=True)
    if subdf.at[0, 'time'] != '2012-06-27T22:00:00Z':
        print(subdf.at[0, 'time'])
    #print(subdf)
    ndf = pd.concat([ndf, subdf.tail(24)])

ndf['dyna_id'] = range(len(ndf))
ndf.to_csv('test.dyna', index=False)
print(len(ndf))
print(ndf.head())'''

dyna = pd.read_csv('raw_data/METR_LA_ori/METR_LA.dyna')
entity_order = list(dyna['entity_id'].unique())

speed = [list() for i in range(12)]
for p in pick_id:
    for i in range(12):
        speed[i].append(predict['prediction'][0][i][entity_order.index(p)][0])

print(speed)