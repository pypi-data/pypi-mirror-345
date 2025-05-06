# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/26/20
# @File  : [wanghong] taobao_shopinfo_manual.py


import os
import re

import pandas as pd
import time
from pymongo import MongoClient
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException

if __name__ == '__main__':
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)

    map = pd.read_csv('/home/cchen/data/wanghong/uids.csv')
    yids = map['Yizhibo_UID'].apply(lambda x: x[2:]).to_list()
    sids = map['Taobao_SID'].apply(lambda x: x[2:]).to_list()
    map = dict(zip(yids, sids))
    uids = set(map[yid] for yid in os.listdir('/media/cchen/exec/yizhibo/nosilence_20to30s/ts/') if yid in map and
               len(os.listdir(f'/media/cchen/exec/yizhibo/nosilence_20to30s/ts/{yid}')))
    
    items = pd.read_csv('/home/cchen/data/wanghong/taobao_items.csv').groupby('Taobao_SID').agg({'title': '\n'.join}).reset_index()
    items = dict((row[1:] for row in items.itertuples()))
    
    client = MongoClient()
    collection = client['yizhibo']['taobao_shops']
    shops = [shop for shop in collection.find({'shopname': None, 'closed': None})]
             # if shop['_id'] in uids]
    for cnt, shop in enumerate(shops):
        try:
            shopid = shop['_id']
            # if shopid not in uids:# or shop['n_items'] < 5 or len(items.get('TS' + shopid)) < 5:
            #     continue
            try:
                driver.get(f'https://shop{shopid}.taobao.com')
            except TimeoutException:
                pass
            # print(shopid)
            time.sleep(1)
            cc = shop.get('category')
            to_update = {}

            # if closed
            body = driver.find_element_by_tag_name('body').text
            if driver.current_url in {'https://store.taobao.com/shop/noshop.htm',
                                      'https://world.taobao.com/',
                                      'https://guang.taobao.com/'}:
                collection.update_one({'_id': shopid}, {'$set': {'closed': 1}})
                print(f'{cnt} / {len(shops)} {shopid}')
                continue
            elif '店铺终止经营公告' in body:
                closed = re.findall('本店铺拟于([0-9]{4})年([0-9]{2})月([0-9]{2})日自主终止经营', body)[0]
                collection.update_one({'_id': shopid}, {'$set': {'closed': '/'.join(closed)}})
                print(f'{cnt} / {len(shops)} {shopid} {closed}')
            # popup1_tag = driver.find_element_by_xpath('//div[@class="popup-content"]')\
            #     .find_elements_by_xpath('//a[@class="cat-name fst-cat-name"]')
            # popup2_tag = driver.find_element_by_xpath('//div[@class="popup-content"]')\
            #     .find_elements_by_xpath('//a[@class="cat-name snd-cat-name"]')
            # popup = '|'.join(ppp.get_attribute('text').strip() for ppp in popup1_tag + popup2_tag
            #          if re.findall('catName=.+', ppp.get_attribute('href')))
            # to_update['popup'] = popup if popup else ''


            title = driver.title
            name = ''
            if title.startswith('首页-') and title.endswith('-淘宝网'):
                name = title[3:-4]
            elif driver.find_elements_by_xpath('//span[@class="shop-name-title"]'):
                nametag = driver.find_element_by_xpath('//span[@class="shop-name-title"]')
                name = nametag.get_attribute('title')
            elif driver.find_elements_by_xpath('//span[@class="shop-name"]'):
                nametag = driver.find_element_by_xpath('//span[@class="shop-name"]').find_element_by_xpath('//a[@class="J_TGoldlog"]')
                name = nametag.text.replace('进入店铺', '').strip()
            if name:
                to_update['shopname'] = name
            else:
                continue

            # print(items.get('TS' + shopid))
            # try:
            #     driver.find_element_by_xpath('//img[@src="//img.alicdn.com/tps/TB1W_vlJFXXXXXxXXXXXXXXXXXX-150-45.png"]')
            #     category = 'fashion'
            # except NoSuchElementException:
            #     category = input(f'{cnt} / {len(shops)} {name} {cc} {shop["n_items"]}:')
            # if category:
            #     to_update['category_manual'] = category

            collection.update_one({'_id': shopid}, {'$set': to_update})
            print(f'{cnt+1} / {len(shops)} {name} {to_update}')
        except KeyboardInterrupt:
            break

['trinket', 'fashion', 'cosmetics', 'bag', 'shoe', 'farm', 'book', 'jewelry', 'instruments', 'food', 'sports', 'kids',
 'cosplay', 'plant', 'health', 'toy', 'paint_tool', 'decorator', 'maternity']
