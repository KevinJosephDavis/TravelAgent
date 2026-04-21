# 将 data 中的 .xlsx 转换为字典

import pandas as pd

excel_path = "C:\\Develop\\projects\\MyTravelAgent\\data\\AMap_adcode_citycode.xlsx"
output_path = "C:\\Develop\\projects\\MyTravelAgent\\lg_agent\\constants\\city_code.py"

df = pd.read_excel(excel_path)

CITY_ADCODE_MAP = {}
for _, row in df.iterrows():
    city = str(row["中文名"]).strip()
    adcode = str(row["adcode"]).strip()
    if city and adcode:
        CITY_ADCODE_MAP[city] = adcode

with open(output_path, "w", encoding="utf-8") as f:
    f.write("# 高德官方城市编码表（全国）\n")
    f.write("CITY_ADCODE_MAP = ")
    f.write(repr(CITY_ADCODE_MAP))