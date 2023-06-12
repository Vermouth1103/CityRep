import json
import pandas as pd

json_data = {"type":"FeatureCollection", "features": []}
df = pd.read_csv("./Xiongan_grid.geo")
print(df)

for index, row in df.iterrows():
    id = int(row["geo_id"])
    lon = float(row["coordinates"][1:-1].split(",")[0].strip())
    lat = float(row["coordinates"][1:-1].split(",")[1].strip())
    temp = {"type":"Feature","geometry":{"type":"Point","coordinates":[lon, lat]},"id":id}
    print(temp)
    json_data["features"].append(temp)

with open("./Xiongan_grid.json", "w") as f:
    json.dump(json_data, f)