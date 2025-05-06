from datetime import datetime

import pandas as pd

from prep.utils import DATA_DIR, calc_time

data = pd.read_csv(f'{DATA_DIR}/weibo_timeline_streaming.csv')
data = data.loc[data['streaming_from'] == 'other']
data['time'] = data['timestamp'].apply(lambda x: calc_time(datetime.utcfromtimestamp(int(x) // 1000)))
data = data.loc[data['Weibo_MID'] != 'WM4194747448537724']
data = data.loc[data['time'] >= 2]
first = (pd.read_csv(f"{DATA_DIR}/../analysis/yizhibo_video_clothes_discount.csv")
         .groupby('Taobao_SID', as_index=False).agg({'stream_time': 'min'}))
data = data.merge(first, on='Taobao_SID', how='inner')
data = data.loc[data.apply(lambda x: x['time'] < x['stream_time'], axis=1)]

with open(f'{DATA_DIR}/../analysis/pom2/streamothers.lst', 'w') as o:
    for sid in set(data['Taobao_SID'].to_list()):
        o.write(f'{sid}\n')
