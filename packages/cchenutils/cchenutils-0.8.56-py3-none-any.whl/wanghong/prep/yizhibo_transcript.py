# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/16/20
# @File  : [wanghong] yizhibo_transcript.py


import pandas as pd
from tqdm import tqdm

from utils import DATA_DIR


def main():
    print(__name__)
    tqdm.pandas()

    df_transcript = pd.read_csv(f'{DATA_DIR}/_yizhibo_transcript.csv', dtype=str,
                                names=['Yizhibo_UID', 'Yizhibo_VID', 'start', 'end',
                                       'error', 'errcode', 'status', 'transcript'])
    df_transcript = df_transcript.dropna(subset=['transcript'])
    df_wavadj = pd.read_csv(f'{DATA_DIR}/wav_adj.csv')
    vid_duration = dict(zip(df_wavadj['Yizhibo_VID'].to_list(), df_wavadj['duration']))

    df_transcript['Yizhibo_UID'] = 'YU' + df_transcript['Yizhibo_UID']
    df_transcript['Yizhibo_VID'] = 'YV' + df_transcript['Yizhibo_VID']
    df_transcript['start_f'] = df_transcript['start'].astype(float)
    df_transcript['end_f'] = df_transcript['end'].astype(float)

    df_transcript = df_transcript.loc[df_transcript.progress_apply(
        lambda x: x['end_f'] <= vid_duration[x['Yizhibo_VID']], axis=1)]

    df_transcript = df_transcript.sort_values(by=['Yizhibo_UID', 'Yizhibo_VID', 'start_f'])
    df_transcript = df_transcript.drop(columns=['error', 'errcode', 'status', 'start_f', 'end_f'])

    df_transcript.to_csv(f'{DATA_DIR}/yizhibo_transcript.csv', index=False)


if __name__ == '__main__':
    main()
