import pandas as pd
import json

df = pd.read_csv("/home/mjt/CityRep/traffic/model/prediction/raw_data/Xiongan/Xiongan.dyna")
entity_id_list = list(set(list(df["entity_id"])))
entity_mapping = dict()
for index in range(len(entity_id_list)):
    entity_mapping[index] = entity_id_list[index]
with open("/home/mjt/CityRep/traffic/model/prediction/entity_mapping.json", "w") as f:
    json.dump(entity_mapping, f)