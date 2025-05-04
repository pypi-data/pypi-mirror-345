import json
import os
import traceback
from datetime import datetime
from multiprocessing import Pool, Manager

import pandas as pd
import requests
from tqdm import tqdm

from utils import DATA_DIR


def get_servers(ncols, shift=0):
    with open('azure_servers.txt') as i:
        lines = [line.strip() for line in i if line.strip()]
        servers = [[(int(lines[i * ncols].lower()[1:]) + shift - 1) % (len(lines) // 6) + 1,
                    lines[(i + 1) * ncols - 1]]
                   for i in range(len(lines) // ncols)]
        servers = sorted(servers)
        return servers


def download_avatar(args):
    def _download_avatar(url, fp):
        res = requests.get(url, proxies=proxies)
        if '.jpg' not in res.request.url:
            return False
        with open(fp, 'wb') as o:
            o.write(res.content)
        return True

    clientq, row = args
    ip = clientq.get()
    proxies = {
        'http': f'http://{ip}:8888',
        'https': f'http://{ip}:8888',
    }
    img_dir = r"C:\Users\chench\Downloads\weibo_timeline_images"
    urls = row['media.urls']
    uid = row['Weibo_UID']
    mid = row['Weibo_MID']
    dp_out = f'{img_dir}/{uid}/{mid}'
    os.makedirs(dp_out, exist_ok=True)
    for url in urls:
        fp = f'{dp_out}/{os.path.split(url)[1]}'
        if os.path.exists(fp):
            continue
        try:
            url_candidates = [url.replace('/thumb150/', '/mw2000/')
                , url.replace('/thumb150/', '/orj360/')
                , url.replace('/thumb150/', '/thumb300/')
                , url]
            for url_candidate in url_candidates:
                if _download_avatar(url_candidate, fp):
                    break
        except KeyboardInterrupt:
            exit()
        except:
            print(f'{uid}/{mid}', url, traceback.format_exc())
    clientq.put(ip)


if __name__ == '__main__':
    df_items = pd.read_csv(r"C:\Users\chench\OneDrive - UWM\projects\porkspace\wanghong\analysis\df_items_clothes.csv")
    df_panel = pd.read_csv(
        r"C:\Users\chench\OneDrive - UWM\projects\porkspace\wanghong\analysis\df_panel_items_sellerrate.csv")
    df_items = df_items[df_items['Taobao_IID'].isin(set(df_panel['Taobao_IID']))]
    df_links = pd.read_csv(f'{DATA_DIR}/uids.csv')
    df_items = df_items.merge(df_links, on='Taobao_SID', how='left')
    weibo_uids = set(df_items['Weibo_UID'].to_list())

    df_wusers = pd.read_csv(f'{DATA_DIR}/weibo_users.csv', usecols=['Weibo_UID', 'nick'])
    df_shops = pd.read_csv(f'{DATA_DIR}/taobao_shops.csv', usecols=['Taobao_SID', 'shopname', 'Weibo_UID'])\
        .query('Weibo_UID in @weibo_uids')\
        .merge(df_wusers, on='Weibo_UID', how='left')
    df_shops.to_csv(r"C:\Users\chench\Downloads\shop_list.csv", index=False, encoding='utf-8')

    df_wbtimeline = pd.read_csv(f'{DATA_DIR}/weibo_timeline.csv')
    df_wbtimeline = df_wbtimeline[df_wbtimeline['media.type'] == 'image']
    df_wbtimeline['datetime'] = df_wbtimeline['timestamp'].apply(lambda x: datetime.utcfromtimestamp(x//1000))
    df_wbtimeline['media.urls'] = df_wbtimeline['media.urls'].apply(json.loads)
    df_wbtimeline = df_wbtimeline[df_wbtimeline['datetime'] >= datetime.strptime('20170701', '%Y%m%d')]
    df_wbtimeline = df_wbtimeline[df_wbtimeline['Weibo_UID'].isin(weibo_uids)]



    with Pool(60) as pool:
        manager = Manager()
        clientq = manager.Queue()
        for _, ip in get_servers(6):
            clientq.put(ip)
            clientq.put(ip)
            clientq.put(ip)

        with tqdm(pool.imap_unordered(download_avatar, ((clientq, row) for _, row in df_wbtimeline.iterrows())),
                  total=len(df_wbtimeline)) as bar:
            for _ in bar:
                pass
