# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/26/20
# @File  : [wanghong] items_cover.py


import multiprocessing
import os
from functools import partial
from glob import iglob

import pandas as pd
from pymongo import MongoClient
from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util import Retry
from tqdm import tqdm


def setup(dp_dst, fp_src=None):
    sid_iids = {os.path.splitext(os.path.relpath(fp, dp_dst))[0] for fp in iglob(os.path.join(dp_dst, '*/*.jpg'))}
    if fp_src:
        df_src = pd.read_csv(fp_src, header=None, dtype=str, names=['shopid', 'itemid', 'cover_url'])
        for _, taobao_item in df_src.iterrows():
            taobao_iid = taobao_item['itemid']
            taobao_sid = taobao_item['shopid']
            if os.path.join(taobao_sid, taobao_iid) in sid_iids:
                continue
            cover_url = taobao_item['cover_url']
            os.makedirs(os.path.join(dp_dst, taobao_sid), exist_ok=True)
            yield '@_@'.join([taobao_sid, taobao_iid, cover_url])
    else:
        client = MongoClient()
        collection = client['yizhibo']['taobao_items']
        for taobao_item in collection.find():
            if not len(taobao_item.get('cover', {}).get('images', [])):
                continue
            taobao_iid = taobao_item['_id']
            taobao_sid = taobao_item['shopid']
            if os.path.join(taobao_sid, taobao_iid) in sid_iids:
                continue
            cover_url = taobao_item['cover']['images'][0]
            if cover_url.startswith('//'):
                cover_url = 'https:' + cover_url
            yield '@_@'.join([taobao_sid, taobao_iid, cover_url])


class Requests(object):
    MAX_RETRIES = 9
    STATUS_FORCELIST = [500]

    def __init__(self, session=None, proxy=None):
        self.session = session
        self.proxy = proxy

    def get(self, url, **kwargs):
        self.response = self.session.get(url, **kwargs)
        return self

    def save(self, fp_out):
        with open(fp_out, 'wb') as o:
            o.write(self.response.content)

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, val):
        if val:
            self._session = val
        else:
            self._session = Session()
            retries = Retry(total=self.MAX_RETRIES, status_forcelist=self.STATUS_FORCELIST)
            self._session.mount('https://', HTTPAdapter(max_retries=retries))
            self._session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 '
                                                        '(KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36'})


def mmap(fnc, lst, n=8, **kwargs):
    pool = multiprocessing.Pool(n)
    with tqdm(pool.imap_unordered(fnc, lst), total=169278, ascii=kwargs.get('ascii', True), ncols=160) as bar:
        for status in bar:
            bar.set_description(status)


def self(x):
    x = x.split('@_@', 2)
    return x[1], x


def download(sid_iid_url, dp_dst):
    sid, iid, url = sid_iid_url.split('@_@', 2)
    req = Requests()
    req.get(url).save(os.path.join(dp_dst, sid, iid + '.jpg'))
    return os.path.join(sid, iid)


def archive(dp_src, fp_dst):
    import numpy as np
    embeddings = {}
    for sfile in os.listdir(dp_src):
        sid, _ = os.path.splitext(sfile)
        if sfile.endswith('.npz') and not os.path.exists(os.path.join(dp_src, sid + '.run')):
            npz = np.load(os.path.join(dp_src, sfile))
            names = npz['name']
            embs = npz['embedding']
            for name, emb in zip(names, embs):
                if name in embeddings:
                    raise KeyError
                embeddings[name] = emb
    np.savez(fp_dst, **embeddings)


if __name__ == '__main__':
    # DATA_DIR = '/home/cchen224/data/'
    DATA_DIR = '/home/cchen/data/taobao/'
    os.makedirs(os.path.join(DATA_DIR, 'taobao_images'), exist_ok=True)
    target_list = setup(dp_dst=os.path.join(DATA_DIR, 'taobao_images'),
                        fp_src=None)#os.path.join(DATA_DIR, 'taobao_items_coverurl.csv'))
    target_func = partial(download, dp_dst=os.path.join(DATA_DIR, 'taobao_images'))
    mmap(target_func, target_list, n=64)
    # from utils import write_csv_1d, qmap
    # listen_func = partial(write_csv_1d, fp=os.path.join(DATA_DIR, 'taobao_items_coverurl.csv'))
    # target_func = self
    # qmap(target_func, target_list, listen_func, n=32)
