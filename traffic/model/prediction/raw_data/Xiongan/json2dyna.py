import json
import pandas as pd
from datetime import datetime
import random 

from math import sin, cos, sqrt, atan2, radians

def is_within_10_meters(lon1, lat1, lon2, lat2):
    #print(lat1, lon1, lat2, lon2)
    R = 6371e3  # radius of the Earth in meters
    phi1 = radians(lat1)
    phi2 = radians(lat2)
    delta_phi = radians(lat2 - lat1)
    delta_lambda = radians(lon2 - lon1)

    a = sin(delta_phi / 2)**2 + cos(phi1) * cos(phi2) * sin(delta_lambda / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    #print(distance)
    return distance < 10

def cal_meters(lon1, lat1, lon2, lat2):
    R = 6371e3  # radius of the Earth in meters
    phi1 = radians(lat1)
    phi2 = radians(lat2)
    delta_phi = radians(lat2 - lat1)
    delta_lambda = radians(lon2 - lon1)

    a = sin(delta_phi / 2)**2 + cos(phi1) * cos(phi2) * sin(delta_lambda / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return distance


# 这一段用的是Road.json
'''with open('Road.json') as f:
    data = json.load(f)

m = {}
record = []
features = data['features'] # list
for f in features:
    geo, pro = f['geometry']['coordinates'], f['properties']
    #print(geo, pro)
    start_coor, end_coor = geo[0], geo[-1]
    start_id, end_id = -1, -1
    flag = 0
    for k in m:
        if is_within_10_meters(start_coor[0], start_coor[1], m[k][0], m[k][1]):
            start_id = k
            flag = 1
            break
    if flag == 0:
        start_id = len(m)
        m[start_id] = start_coor
    
    flag = 0
    for k in m:
        if is_within_10_meters(end_coor[0], end_coor[1], m[k][0], m[k][1]):
            end_id = k
            flag = 1
            break
    if flag == 0:
        end_id = len(m)
        m[end_id] = end_coor

    record.append((start_id, end_id))
'''

# 这一段用的是Node.json
with open('Node.json', 'r') as f:
    data = json.load(f)

m = {}
label_id = []
record = []
features = data['features'] # list
for f in features:
    geo, pro = f['geometry']['coordinates'], f['properties']
    #print(pro)
    id, neibours = str(f['id']), pro['LINKLIST']
    neibours = neibours.split(',')

    m[id] = {'geo': geo, 'neibours': neibours}
    label_id.append(id)


# generate .geo file
geofile = pd.DataFrame(columns=['geo_id', 'type', 'coordinates'])
cnt = 0
for key in m:
    geofile.loc[cnt] = [key, 'Point', str(m[key]['geo'])]
    cnt += 1
    
geofile.to_csv('Xiongan.geo', index=False)

# generate .rel file
appear = set()
relfile = pd.DataFrame(columns=['rel_id', 'type', 'origin_id', 'destination_id', 'cost'])
cnt = 0

for key in m:
    neibours = m[key]['neibours']
    for nei in neibours:
        if nei not in m: continue
        small = min(key, nei)
        big = max(key, nei)
        if (small, big) not in appear:
            relfile.loc[cnt] = [cnt, 'geo', small, big, cal_meters(m[small]['geo'][0], m[small]['geo'][1], m[big]['geo'][0], m[big]['geo'][1])]
            cnt += 1
            appear.add((small, big))

relfile.to_csv('Xiongan.rel', index=False)

# generate .dyna file
metrla_dyna = pd.read_csv('../METR_LA_ori/METR_LA.dyna')
dyna_file = pd.DataFrame(columns=['dyna_id','type','time','entity_id','traffic_speed'])

keys = list(m.keys())
curid = -1
last_road = -1
flag = 0
cnt = 0

start_tm = 1367418000
for key in keys:
    for i in range(60):
        tm = start_tm + i*300
        ti = datetime.fromtimestamp(tm).strftime('%Y-%m-%dT%H:%M:%SZ')
        dyna_file.loc[cnt] = [cnt, 'state', ti, key, random.uniform(50, 70)]
        cnt += 1
        print(cnt)

dyna_file.to_csv('Xiongan.dyna', index=False)

    
