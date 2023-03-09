import random
import json

road_num = 836
speed_dict = dict()
for i in range(road_num):
    speed_dict[i] = random.randint(30, 40)
print(speed_dict)

with open("history_speed.json", "w") as f:
    json.dump(speed_dict, f)