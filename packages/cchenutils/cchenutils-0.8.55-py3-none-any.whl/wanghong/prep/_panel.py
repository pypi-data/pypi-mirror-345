# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 2/12/20
# @File  : [wanghong] _panel.py


from datetime import datetime

import pandas as pd
from tqdm import tqdm

from prep.utils import DATA_DIR, LEVEL, MAX_TIME, calc_time


def expand_by_time(df):
    df = df.set_index('time')
    left, right = df.index.min(), df.index.max() + 1
    df = df.reindex(pd.RangeIndex(left, right, name='time')).reset_index('time')
    df['first'] = df['first'].fillna(method='ffill')
    df['keep'] = left < 16
    return df.fillna(0)


def expand_by_default_time(df):
    df = df.set_index('time', append=False)
    left, right = 0, MAX_TIME
    df = df.reindex(pd.RangeIndex(left, right, name='time')).reset_index('time')
    df = df.fillna(method='ffill').fillna(0)
    return df


def expand_by_default_time_0(df):
    df = df.set_index('time', append=False)
    left, right = 0, MAX_TIME
    df = df.reindex(pd.RangeIndex(left, right, name='time')).reset_index('time')
    return df.fillna(0)


def main():
    print(__name__)
    tqdm.pandas()

    df_rates = pd.read_csv(f'{DATA_DIR}/taobao_rates_.csv', # nrows=100,
                           dtype={col: int for col in pd.read_csv(f'{DATA_DIR}/taobao_rates_.csv', nrows=1).columns
                                  if col[:4] in {'time', 'days'}})
    # , usecols=['Taobao_SID', 'Taobao_IID', 'Taobao_RID', 'content',
    #            'rate', 'date', 'rate_date', 'first', 'after', 'valid', 'purchases']


    # df_rates = df_rates.loc[df_rates['Taobao_IID'] == 'TI543336316082']
    # df_rates = df_rates.loc[df_rates['Taobao_SID'].isin(set(df_video_category['Taobao_SID']))]
    df_rates = df_rates[~df_rates['Taobao_SID'].isin(['TS575099047', 'TS110761502'])]  # sellers on JD
    # df_filter = pd.read_csv('../analysis/yizhibo_video_clothes_discount.csv').dropna(subset=['sell'])  # remove not labelled

    # total_rates = df_rates.groupby(['Taobao_IID'], as_index=False).agg({'Taobao_RID': 'count'})
    # df_rates = df_rates[df_rates['Taobao_IID'].isin(total_rates[total_rates['Taobao_RID'] < 6000]['Taobao_IID'])]

    # df_30sales = pd.read_csv(f'{DATA_DIR}/diff_sales.csv')
    # df_rates = df_rates[df_rates['Taobao_IID'].isin(
    #     df_30sales[df_30sales.apply(lambda x: -10 <(x['rates_bjt_adj'] - x['sales_item']) < 10, axis=1)]['Taobao_IID'])]
    # df_faces = pd.read_csv(f'{DATA_DIR}/yizhibo_facepp_compare.csv')\
    #     .groupby(['Yizhibo_UID'], as_index=False)\
    #     .agg({'confidence': 'max'})\
    #     .merge(pd.read_csv(f'{DATA_DIR}/uids.csv'), on='Yizhibo_UID', how='left')
    # df_rates = df_rates[df_rates['Taobao_SID'].isin(df_faces[df_faces['confidence'] > 0.8]['Taobao_SID'])]

    # df_items = pd.read_csv(f'{DATA_DIR}/_taobao_items.csv', usecols=['_id', 'sales_item'], dtype={'_id': str}) \
    #     .rename(columns={'_id': 'Taobao_IID'})
    # df_items['Taobao_IID'] = 'TI' + df_items['Taobao_IID']

    # df_rates = df_rates[df_rates['Taobao_SID'].isin(df_filter['Taobao_SID'])]

    df_rates['time'] = df_rates['date'].progress_apply(calc_time)
    df_rates['time1'] = df_rates['date1'].progress_apply(calc_time)
    df_rates['time2'] = df_rates['date2'].progress_apply(calc_time)
    df_rates['time12'] = df_rates['date12'].progress_apply(calc_time)
    df_rates['rate_time'] = df_rates['rate_date'].progress_apply(calc_time)
    df_rates = df_rates.loc[df_rates['rate_time'] >= 0].reset_index(drop=True)
    df_rates['neg_rate'] = df_rates['rate'] < 0
    df_rates['pos_rate'] = df_rates['rate'] > 0
    df_rates['neu_rate'] = df_rates['rate'] == 0
    df_rates['n_valid'] = df_rates['valid']
    df_rates = df_rates.loc[df_rates['time'] < MAX_TIME]
    df_rates['content'] = df_rates['content'].fillna('')

    # df_items = pd.read_csv(os.path.join(DATA_DIR, 'taobao_items.csv'), usecols=['Taobao_SID', 'Taobao_IID'])

    agg_opts = {'Taobao_RID': 'count',
                'purchases': 'sum',
                'n_valid': 'sum',
                'neg_rate': 'sum',
                'pos_rate': 'sum',
                'neu_rate': 'sum',
                'rate': 'sum',
                'promo': 'sum',
                'after': 'max',
                'first': 'first'}

    if LEVEL.endswith('IID'):
        agg_opts['Taobao_SID'] = 'first'

    # df_panel = df_rates.groupby(LEVEL) \
    #     .filter(lambda x: x['after'].mean() < 1).reset_index(drop=True)
    df_panel = df_rates.groupby([LEVEL, 'time']).agg(agg_opts).rename(columns={'Taobao_RID': 'n_ratings'}).reset_index()
    df_panel = df_panel.groupby([LEVEL]).filter(lambda x: len(x) > 1).reset_index(drop=True)
    df_panel = df_panel.groupby(list({'Taobao_SID', LEVEL})).progress_apply(expand_by_time) \
        .drop(columns=list({'Taobao_SID', LEVEL})).reset_index(list({'Taobao_SID', LEVEL}))

    df_panel1 = df_rates.groupby([LEVEL, 'time1'], as_index=False) \
        .agg({'Taobao_RID': 'count', 'purchases': 'sum', 'promo': 'sum'}) \
        .rename(columns={'Taobao_RID': 'n_ratings1', 'purchases': 'purchases1', 'promo': 'promo1', 'time1': 'time'})
    df_panel2 = df_rates.groupby([LEVEL, 'time2'], as_index=False) \
        .agg({'Taobao_RID': 'count', 'purchases': 'sum', 'promo': 'sum'}) \
        .rename(columns={'Taobao_RID': 'n_ratings2', 'purchases': 'purchases2', 'promo': 'promo2', 'time2': 'time'})
    df_panel12 = df_rates.groupby([LEVEL, 'time12'], as_index=False) \
        .agg({'Taobao_RID': 'count', 'purchases': 'sum', 'promo': 'sum'}) \
        .rename(columns={'Taobao_RID': 'n_ratings12', 'purchases': 'purchases12', 'promo': 'promo12', 'time12': 'time'})
    df_panel = df_panel.merge(df_panel1, on=[LEVEL, 'time'], how='left') \
        .merge(df_panel2, on=[LEVEL, 'time'], how='left') \
        .merge(df_panel12, on=[LEVEL, 'time'], how='left') \
        .fillna({'n_ratings1': 0, 'n_ratings2': 0, 'purchases1': 0, 'purchases2': 0, 'promo1': 0, 'promo2': 0})

    # df_video = df_video.rename(columns={'stream_time': 'time'}).groupby(['Taobao_SID']) \
    #     .progress_apply(expand_by_default_time) \
    #     .drop(columns='Taobao_SID').reset_index('Taobao_SID')

    agg_funcs = {'Taobao_RID': 'count', 'seller_replied': 'sum', 'vicious': 'sum', 'valid': 'sum',
                 'neg_rate': 'sum', 'neu_rate': 'sum', 'pos_rate': 'sum'}
    # for cnt in range(1, 11):
    #     df_rates[f'avail_valid{cnt}'] = df_rates.apply(lambda x: x['n_valid'] * (len(x['content']) >= cnt), axis=1)
    #     agg_funcs[f'avail_valid{cnt}'] = 'sum'

    df_rdate = df_rates.groupby([LEVEL, 'rate_time']).agg(
        {'Taobao_RID': 'count', 'seller_replied': 'sum', 'vicious': 'sum', 'valid': 'sum',
         'neg_rate': 'sum', 'neu_rate': 'sum', 'pos_rate': 'sum', 'rate': 'sum', 'purchases': 'sum'}) \
        .reset_index() \
        .rename(columns={'Taobao_RID': 'avail_ratings', 'valid': 'avail_valid', 'rate_time': 'time',
                         'seller_replied': 'avail_seller_replied', 'vicious': 'avail_vicious',
                         'neg_rate': 'avail_neg_rate', 'neu_rate': 'avail_neu_rate', 'pos_rate': 'avail_pos_rate',
                         'rate': 'avail_rate', 'purchases': 'avail_purchases'}) \
        .set_index(['Taobao_IID', 'time'])

    # del df_rates
    df_append = pd.read_csv(f'{DATA_DIR}/taobao_appendrates.csv', parse_dates=['rate_date'])
    df_append['rate_time'] = df_append['rate_date'].progress_apply(calc_time)
    df_append['valid'] = 1
    df_append = df_append.loc[df_append['rate_time'] < MAX_TIME]
    df_rdate2 = df_append.groupby([LEVEL, 'rate_time']).agg(
        {'Taobao_RID': 'count', 'seller_replied': 'sum', 'vicious': 'sum', 'valid': 'sum',}) \
        .reset_index() \
        .rename(columns={'Taobao_RID': 'avail_ratings', 'valid': 'avail_valid', 'rate_time': 'time',
                         'seller_replied': 'avail_seller_replied', 'vicious': 'avail_vicious'}) \
        .set_index(['Taobao_IID', 'time'])

    df_rdate = df_rdate.add(df_rdate2, fill_value=0).reset_index()
    df_rdate = df_rdate.groupby(LEVEL).apply(lambda x: x.sort_values(by=['time'])).reset_index(drop=True)

    df_cumsum = pd.concat(
        [df_rdate[[LEVEL, 'time']], df_rdate.drop(columns=['time']).groupby([LEVEL]).cumsum()], axis=1)
    df_cumsum = df_cumsum.groupby(LEVEL).progress_apply(expand_by_default_time).drop(columns=LEVEL).reset_index(LEVEL)
    df_rdate_e = df_rdate.groupby(LEVEL).progress_apply(expand_by_default_time_0).drop(columns=LEVEL).reset_index(LEVEL)
    df_cumsum['avail_ratings'] -= df_rdate_e['avail_ratings']
    df_cumsum['avail_valid'] -= df_rdate_e['avail_valid']
    df_cumsum['avail_seller_replied'] -= df_rdate_e['avail_seller_replied']
    df_cumsum['avail_vicious'] -= df_rdate_e['avail_vicious']
    df_cumsum['avail_neg_rate'] -= df_rdate_e['avail_neg_rate']
    df_cumsum['avail_neu_rate'] -= df_rdate_e['avail_neu_rate']
    df_cumsum['avail_pos_rate'] -= df_rdate_e['avail_pos_rate']
    df_cumsum['avail_rate'] -= df_rdate_e['avail_rate']
    df_cumsum['avail_purchases'] -= df_rdate_e['avail_purchases']
    # for cnt in range(1, 11):
    #     df_cumsum[f'avail_valid{cnt}'] -= df_rdate_e[f'avail_valid{cnt}']

    df_panel = df_panel.merge(df_cumsum, on=[LEVEL, 'time'], how='left')
    # .merge(df_video, on=['Taobao_SID', 'time'], how='left') \

    # videos
    df_video = pd.read_csv(f'{DATA_DIR}/yizhibo_video_clothes.csv').dropna(subset=['sell'])
    df_video['issell'] = df_video['sell'] == 1
    df_video['notsell'] = df_video['sell'] == 0
    df_videos = df_video.groupby(['Taobao_SID', 'stream_time']) \
        .agg({'play.length': 'sum', 'issell': 'sum', 'notsell': 'sum',
              'n_likes': 'sum', 'n_messages': 'sum', 'n_views': 'sum'}) \
        .rename(columns={'play.length': 'avail_play.length', 'issell': 'avail_issell', 'notsell': 'avail_notsell',
                         'n_likes': 'avail_likes', 'n_messages': 'avail_messages', 'n_views': 'avail_views'}) \
        .reset_index() \
        .rename(columns={'stream_time': 'time'})
    df_videos_cumsum = df_videos.groupby('Taobao_SID').apply(expand_by_default_time).drop(columns=['Taobao_SID']).reset_index(['Taobao_SID'])
    df_videos_cumsum_e = df_videos.groupby('Taobao_SID').apply(expand_by_default_time_0).drop(columns=['Taobao_SID']).reset_index(['Taobao_SID'])
    df_videos_cumsum['avail_play.length'] -= df_videos_cumsum_e['avail_play.length']
    df_videos_cumsum['avail_issell'] -= df_videos_cumsum_e['avail_issell']
    df_videos_cumsum['avail_notsell'] -= df_videos_cumsum_e['avail_notsell']
    df_videos_cumsum['avail_likes'] -= df_videos_cumsum_e['avail_likes']
    df_videos_cumsum['avail_messages'] -= df_videos_cumsum_e['avail_messages']
    df_videos_cumsum['avail_views'] -= df_videos_cumsum_e['avail_views']

    df_panel = df_panel.merge(df_videos_cumsum, on=['Taobao_SID', 'time'], how='left')

    # miaopai
    # df_miaopai = pd.read_csv(f'{DATA_DIR}/weibo_miaopai.csv'
    #                          , usecols=['Weibo_UID', 'timestamp', 'Weibo_MID', 'media_play_count']) \
    #     .merge(pd.read_csv(f'{DATA_DIR}/uids.csv'), on='Weibo_UID', how='inner')
    # df_miaopai['time'] = df_miaopai['timestamp'].apply(lambda x: calc_time(datetime.utcfromtimestamp(int(x) // 1000)))
    # df_miaopai['time_lag'] = df_miaopai['time'] + 1
    # df_miaopai_panel = df_miaopai.groupby(['Taobao_SID', 'time']).agg({'Weibo_MID': 'count', 'media_play_count': 'sum'}) \
    #     .rename(columns={'Weibo_MID': 'miaopai'}).reset_index()
    # df_miaopai_panel_lag = df_miaopai.groupby(['Taobao_SID', 'time_lag']).agg({'Weibo_MID': 'count', 'media_play_count': 'sum'}) \
    #     .reset_index().rename(columns={'Weibo_MID': 'miaopai_lag', 'time_lag': 'time', 'media_play_count': 'media_play_count_lag'})
    # df_panel = df_panel.merge(df_miaopai_panel, on=['Taobao_SID', 'time'], how='left') \
    #     .merge(df_miaopai_panel_lag, on=['Taobao_SID', 'time'], how='left')
    # df_panel['miaopai'] = df_panel['miaopai'].fillna(0)
    # df_panel['miaopai_lag'] = df_panel['miaopai_lag'].fillna(0)
    # df_panel['media_play_count'] = df_panel['media_play_count'].fillna(0)
    # df_panel['media_play_count_lag'] = df_panel['media_play_count_lag'].fillna(0)

    # weibo timeline
    df_timeline = pd.read_csv(f'{DATA_DIR}/weibo_timeline_streaming.csv')
    df_timeline['time'] = df_timeline['timestamp'].apply(
        lambda x: calc_time(datetime.utcfromtimestamp(int(x) // 1000)))
    # df_streamed_before = df_timeline[~df_timeline['streaming_from'].isna()] \
    #     .groupby(['Weibo_UID']).agg({'time': 'min'}).reset_index()
    # df_streamed_before = df_streamed_before[df_streamed_before['time'] < 0]
    # streaming_other = set(df_timeline[df_timeline['streaming_from'] == 'other']['Weibo_UID'])
    # df_timeline = df_timeline[~df_timeline['Weibo_UID'].isin(set(df_streamed_before['Weibo_UID']) | streaming_other)]
    df_timeline_nonstreaming = df_timeline[(df_timeline['streaming_from'].isna()) & (df_timeline['time'] >= 0)] \
        .groupby(['Taobao_SID', 'time']) \
        .agg({'Weibo_MID': 'count',
              'likes': 'sum',
              'comments': 'sum',
              'forwards': 'sum',
              'media.play_count': 'sum',
              'n_videos': 'sum',
              'n_images': 'sum'}).reset_index() \
        .rename(columns={'Weibo_MID': 'n_weibos'})
    #df_panel[(df_panel['Taobao_SID'].isin(df_timeline_nonstreaming['Taobao_SID']))]
    df_panel = df_panel \
        .merge(df_timeline_nonstreaming, on=['Taobao_SID', 'time'], how='left') \
        .fillna({'n_weibos': 0,
                 'likes': 0,
                 'comments': 0,
                 'forwards': 0,
                 'media.play_count': 0,
                 'n_videos': 0,
                 'n_images': 0})

    # export
    df_panel.to_csv(f'../analysis/df_panel_{"users" if LEVEL.endswith("SID") else "items"}_.csv', index=False)


if __name__ == '__main__':
    main()
