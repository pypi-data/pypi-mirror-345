# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 2/28/20
# @File  : [wanghong] ts_downbind.py


import os
from functools import partial
from utils import touch
import pandas as pd
import requests
from requests.exceptions import ConnectionError, Timeout
from tqdm import tqdm

from utils import mmap

# os.chdir('/project')
# os.chdir('/home/yuhenghu/Dropbox/porkspace/streaming')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "",
    "DNT": "1",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache"
}


# def tmp_incomplete(tmp_dir):
#     for uid in os.listdir(tmp_dir):
#         for vid in os.listdir(os.path.join(tmp_dir, uid)):
#             if vid.endswith('.ts'):
#                 # os.remove(os.path.join(tmp_dir, uid, vid))
#                 continue
#             if os.listdir(os.path.join(tmp_dir, uid, vid)):
#                 yield vid
#
#
# def setup(out_dir, m3u8_dir):
#     df_users = pd.read_csv('df_shops.csv', dtype=str)
#     users = set(df_users['Yizhibo_UID'].apply(lambda x: x[2:]).tolist())
#     end_time = datetime.strptime('2018-05-01', '%Y-%m-%d')
#     df1 = pd.read_csv('replays.csv', dtype=str)
#     df1 = df1.drop_duplicates().dropna(subset=['play.url'])
#     df1 = df1.loc[df1['uid'].isin(users)]
#     df2 = pd.read_csv('yizhibo_replays.csv', dtype=str)[['_id', 'uid', 'date']]
#     df2 = df2.drop_duplicates().dropna(subset=['date'])
#     df2 = df2.loc[df2['uid'].isin(users)]
#     df2 = df2.loc[df2['date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d') < end_time)]
#     df = pd.merge(df1, df2, on=['_id', 'uid'], how='inner')
#     # incomplete = set(tmp_incomplete(tmp_dir))
#     # df['length'] = df.apply(lambda x: load_length(os.path.join(m3u8_dir, x['uid'], x['_id'] + '.m3u8')), axis=1)
#
#     for _, row in tqdm(df.iterrows()):
#         uid, vid, url = row[['uid', '_id', 'play.url']]
#         if os.path.exists(os.path.join(out_dir, uid, vid + '.ts')): continue
#         mkdir(m3u8_dir, uid)
#         m3u8 = load_m3u8(url, os.path.join(m3u8_dir, uid, vid + '.m3u8'))
#         if not m3u8:
#             continue
#         urlr, _ = url.rsplit('/', 1)
#         if vid == '_1yWKxa-vVLBO7TS':
#             yield os.path.join(uid, vid), urlr, m3u8
#
#
def load_m3u8(url, fp_in, preloaded=True):
    if not os.path.exists(fp_in):
        if preloaded:
            return []
        return load_m3u8(url, fp_in) if download_m3u8(url, fp_in) else []
    with open(fp_in, 'r') as i:
        return [line.strip() for line in i if line.strip().endswith('.ts')]


def download_m3u8(url, fp_out, max_retry=5):
    for _ in range(max_retry):
        try:
            m3u8 = requests.get(url, timeout=60).content
            with open(fp_out, 'w') as o:
                o.write(m3u8)
            return True
        except ConnectionError:
            continue
    return False
#
#
# def load_length(fp_in):
#     if not os.path.exists(fp_in):
#         return 0.
#     with open(fp_in, 'r') as i:
#         return sum([float(line.strip()[8:-1]) for line in i if line.strip().startswith('#EXTINF:')])
#
#
# def downbind((uid_vid, urlr, tss), out_dir, tmp_dir='/mnt/data/tmp'):
#     is_complete = False
#     for _ in range(5):
#         download_ts((uid_vid, urlr, tss), out_dir=tmp_dir)
#         is_complete = complete_ts((uid_vid, tss), out_dir=tmp_dir)
#         if is_complete:
#             break
#     if not is_complete:
#         return uid_vid + 'failed.', False
#
#     merge_ts((uid_vid, tss), out_dir=tmp_dir)
#     uid, vid = uid_vid.split(os.sep)
#     mkdir(out_dir, uid)
#     shutil.move(os.path.join(tmp_dir, uid_vid + '.ts'), os.path.join(out_dir, uid_vid + '.ts'))
#     shutil.rmtree(os.path.join(tmp_dir, uid_vid))
#     return uid_vid, True
#
#
# def download_ts((uid_vid, urlr, tss), out_dir='/mnt/data/tmp', max_retry=5):
#     # urlr = urlr.replace('http:', 'https:')
#     mkdir(out_dir, uid_vid)
#     for ts in tss:
#         if os.path.exists(os.path.join(out_dir, uid_vid, ts)):
#             continue
#         for _ in range(max_retry):
#             try:
#                 res = requests.get(urlr + '/' + ts, headers=HEADERS, timeout=60)
#                 video = res.content
#                 if video.startswith('<?xml version="1.0"'):
#                     return False
#                 with open(os.path.join(out_dir, uid_vid, ts), 'wb') as o:
#                     o.write(video)
#                 break
#             except (ConnectionError, Timeout):
#                 pass
#     return True
#
#
# def merge_ts((uid_vid, tss), out_dir='/mnt/data/tmp'):
#     with open(os.path.join(out_dir, uid_vid + '.ts'), 'wb') as o:
#         for ts in tss:
#             with open(os.path.join(out_dir, uid_vid, ts), 'rb') as i:
#                 for line in i:
#                     o.write(line)
#     return True
#
#
# def complete_ts((uid_vid, tss), out_dir='/mnt/data/tmp'):
#     for ts in tss:
#         if not os.path.exists(os.path.join(out_dir, uid_vid, ts)):
#             return False
#     return True


def downbind_ts(uid_vid, dp_dst, dp_m3u8):
    url = pd.read_csv('/home/cchen/Dropbox/streaming/replays.csv', dtype=str)
    url = dict(zip(url['_id'].to_list(), url['play.url'].to_list()))

    if os.path.exists(dp_dst + '.ts') and not os.path.exists(dp_dst + '.run'):
        return uid_vid, True

    _, vid = uid_vid.split('/')
    os.makedirs(os.path.join(dp_dst, uid_vid), exist_ok=True)
    urlr, _ = url[vid].rsplit('/', 1)
    print(urlr)
    tss = load_m3u8(url[vid], os.path.join(dp_m3u8, uid_vid + '.m3u8'))
    for ts in tqdm(tss):
        download_ts(ts, os.path.join(dp_dst, uid_vid), urlr)
    combine_ts(os.path.join(dp_dst, uid_vid), dp_m3u8)
    return uid_vid, True


def download_ts(ts, dp_dst, urlr):
    fp_dst = os.path.join(dp_dst, ts)
    fp_run = os.path.join(dp_dst, ts + '.run')
    fp_tmo = os.path.join(dp_dst, ts + '.tmo')
    fp_na = dp_dst + '.na'
    if os.path.exists(fp_dst) and not os.path.exists(fp_run):
        return True
    try:
        touch(fp_run)
        res = requests.get(urlr + '/' + ts, headers=HEADERS, timeout=60)
        video = res.content
        if video.startswith(b'<?xml version="1.0"'):
            touch(fp_na)
            return False
        with open(fp_dst, 'wb') as o:
            o.write(video)
        os.remove(fp_run)
        return True
    except (ConnectionError, Timeout):
        touch(fp_tmo)
        return False


def combine_ts(dp_ts, dp_m3u8):
    if not is_complete(dp_ts, dp_m3u8) or os.path.exists(dp_ts + '.ts'):
        return False

    touch(dp_ts + '.run')
    tss = [ts for ts in os.listdir(dp_ts) if ts.endswith('.ts')]
    tss = sorted(tss, key=lambda x: int(x.split('.')[0]))

    with open(dp_ts + '.ts', 'wb') as o:
        for ts in tss:
            with open(os.path.join(dp_ts, ts), 'rb') as i:
                for line in i:
                    o.write(line)
    os.remove(dp_ts + '.run')
    return True


def is_complete(dp_ts, dp_m3u8):
    _, uid, vid = dp_ts.rsplit(os.path.sep, 2)
    tss = os.listdir(dp_ts)
    fps = [ts for ts in tss if ts.endswith('.ts')]
    chk = load_m3u8('', os.path.join(dp_m3u8, uid, vid + '.m3u8'))
    run = [ts for ts in tss if ts.endswith('.run')]
    return True if len(fps) == len(chk) and not run else False


if __name__ == '__main__':
    dp_dst = '/home/cchen/Downloads/ts'
    dp_m3u8 = '/media/cchen/data/yizhibo/m3u8'
    # tmp_dir = '/media/yuhenghu/data/tmp/'

    ids = pd.read_csv('../../redown.txt', sep='\t', header=None, dtype=str)
    ids = zip(ids[0].to_list(), ids[1].to_list())
    target_list = [os.path.join(uid, vid) for uid, vid in ids]

    # downbind_ts(out_dir, m3u8_dir)

    # target_list = list(setup(out_dir, m3u8_dir))
    # target_list = random.sample(target_list,  len(target_list))
    target_func = partial(downbind_ts, dp_dst=dp_dst, dp_m3u8=dp_m3u8)
    mmap(target_func, target_list, n=2)

    # import shutil
    # from glob import glob
    # for fp in tqdm(glob(os.path.join(dp_dst, '*', '*.ts'))):
    #     _, uid, vfile = fp.rsplit('/', 2)
    #     shutil.move(fp, os.path.join('/media/cchen/data/yizhibo/ts/', uid, vfile))