from datetime import datetime

import pandas as pd

from prep.utils import DATA_DIR, calc_time

data = pd.read_csv(f'{DATA_DIR}/weibo_timeline.csv').fillna(0).sort_values(by='timestamp')
first = (pd.read_csv(f"{DATA_DIR}/../analysis/yizhibo_video_clothes_discount.csv")
         .groupby('Taobao_SID', as_index=False).agg({'stream_time': 'min'}))
data = (data.merge(pd.read_csv(f'{DATA_DIR}/uids.csv'), on='Weibo_UID', how='inner')
        .merge(first, on='Taobao_SID', how='inner'))
data['time'] = data['timestamp'].apply(lambda x: calc_time(datetime.utcfromtimestamp(int(x) // 1000)))
data = data.loc[data.apply(lambda x: 0 > x['time'] - x['stream_time'], axis=1)]
users = data.groupby('Taobao_SID', as_index=False).agg({'Weibo_MID': 'count'})
for w in [8, 6, 4]:
    users = users.merge(data.loc[data.apply(lambda x: x['time'] - x['stream_time'] >= -w, axis=1)]
                        .groupby('Taobao_SID', as_index=False).agg({'comments': 'mean', 'likes': 'mean'})
                        .rename(columns={'comments': f'comments_{w}w', 'likes': f'likes_{w}w'})
                        , on='Taobao_SID', how='left')
for l in [5, 10, 15, 20]:
    users = users.merge(data.groupby('Taobao_SID', as_index=False).tail(l)
                        .groupby('Taobao_SID', as_index=False).agg({'comments': 'mean', 'likes': 'mean'})
                        .rename(columns={'comments': f'comments_l{l}', 'likes': f'likes_l{l}'})
                        , on='Taobao_SID', how='left')
users.drop(columns=['Weibo_MID']).to_csv(f'{DATA_DIR}/../analysis/pom2/comments.csv', index=False)

