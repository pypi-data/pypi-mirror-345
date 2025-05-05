# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 4/2/20
# @File  : [wanghong] yizhibo_transcript_match.py


import os

import pandas as pd
from utils import DATA_DIR

if __name__ == '__main__':
    df_transcript = pd.read_csv(f'{DATA_DIR}/yizhibo_transcript.csv', dtype=str)
    df_tb = df_transcript.loc[df_transcript['transcript'].apply(lambda x: '号链接' in x)].reset_index(drop=True)
    df_tb['path'] = df_tb.apply(lambda x:
                                os.path.join('/media/cchen/exec/yizhibo/nosilence_20to30s/ts',
                                             x['Yizhibo_UID'][2:], x['Yizhibo_VID'][2:], f'{x["start"]}_{x["end"]}.ts')
                                , axis=1)

    map = pd.read_csv(f'{DATA_DIR}/uids.csv')
    yids = map['Yizhibo_UID'].to_list()
    sids = map['Taobao_SID'].to_list()
    map = dict(zip(yids, sids))
    uids = set(map[yid] for yid in os.listdir('/media/cchen/exec/yizhibo/nosilence_20to30s/ts/') if yid in map and
               len(os.listdir(f'/media/cchen/exec/yizhibo/nosilence_20to30s/ts/{yid}')))

    items = pd.read_csv('/home/cchen/data/wanghong/taobao_items.csv').groupby('Taobao_SID').agg(
        {'title': '\n'.join}).reset_index()
    items = dict((row[1:] for row in items.itertuples()))

    idx = 16428
    print(items[map[df_tb['Yizhibo_UID'].to_list()[idx]]])
    print(df_tb['path'].to_list()[idx])


    import numpy as np

    def cos_mat(lst_a, lst_b):
        sims = []
        for cnt_a, it_a in enumerate(lst_a):
            for cnt_b, it_b in enumerate(lst_b):
                sim = cos_sim(it_a, it_b)
                sims.append((cnt_a, cnt_b, sim))
                print('{:8.2f}'.format(sim), end='')
            print()
        return sims

    def cos_sim(a, b):
        """Takes 2 vectors a, b and returns the cosine similarity according
        to the definition of the dot product
        """
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        return dot_product / (norm_a * norm_b)

    yi = np.load('/mnt/nvme/yizhibo/fashionnet_consumer2shop_consumer/98291007/paxseHbamtaA0vn7.npz')
    lst_a = yi['embedding']
    tb = np.load('/mnt/nvme/yizhibo/fashionnet_consumer2shop_shop/35257690.npz')
    lst_b = tb['embedding']

    sims = cos_mat(lst_a, lst_b)
    sims_val = [sim[2] for sim in sims]
    pd.DataFrame(sims_val).describe()
    sims[sims_val.index(max(sims_val))]
    yi['name'][95]
    tb['name'][5]