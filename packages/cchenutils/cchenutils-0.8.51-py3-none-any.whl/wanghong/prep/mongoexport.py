# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 2/11/20
# @File  : [wanghong] mongoexport.py


import os

from utils import DATA_DIR


def export_taobao_rates():
    fp = os.path.join(DATA_DIR, '_taobao_rates.csv')
    fd = ','.join(['_id', 'itemid', 'date', 'rate', 'validscore', 'content', 'dayAfterConfirm', 'lastModifyFrom',
                   'buyAmount', 'bidPriceMoney.amount', 'bidPriceMoney.currencyCode',
                   'video', 'photos', 'promotionType',
                   'user.nick', 'raterType', 'auction.sku',
                   'vicious', 'useful',
                   'reply', 'appendList'])
    os.system('mongoexport -d yizhibo -c taobao_comments --type csv -o {} --fields {}'.format(fp, fd))


def export_taobao_items():
    fp = os.path.join(DATA_DIR, '_taobao_items.csv')
    fd = ','.join(['_id', 'shopid', 'title', 'bookmarks',
                   'price', 'promo',  # 产品页面价格
                   'listprice',  # 列表里显示的价格
                   'comments', 'sales_item', 'stock',
                   'n_attributes', 'n_covers_images', 'n_desc_images', 'attributes'])
    os.system('mongoexport -d yizhibo -c taobao_items --type csv -o {} --fields {}'.format(fp, fd))


def export_taobao_items_30sold():
    fp = os.path.join(DATA_DIR, '_taobao_items_30sold.csv')
    fd = ','.join(['_id', 'shopid', 'sold_30d'])
    os.system('mongoexport -d wanghong -c taobao_items2 --type csv -o {} --fields {}'.format(fp, fd))


def export_taobao_shops():
    fp = os.path.join(DATA_DIR, '_taobao_shops.csv')
    fd = ','.join(['_id', 'shopname', 'weibo_id', 'ifashion', 'category_manual',
                   'category', 'seller_rate.main', 'seller_rate.overall', 'since',
                   'firststream_date',
                   'dsr.logistics.score', 'dsr.match.score', 'dsr.service.score',
                   'dsr.logistics.compare_industry', 'dsr.match.compare_industry', 'dsr.service.compare_industry'])
    os.system('mongoexport -d yizhibo -c taobao_shops --type csv -o {} --fields {}'.format(fp, fd))


def export_weibo_users():
    fp = os.path.join(DATA_DIR, '_weibo_users.csv')
    fd = ','.join(['_id', 'yizhibo_id', 'n_followers', 'n_followings', 'n_weibos', 'gender', 'bigV',
                   'level', 'nick', 'tags', 'pinfo', 'winfo'])
    os.system('mongoexport -d yizhibo -c weibo_users_target --type csv -o {} --fields {}'.format(fp, fd))


def export_weibo_timeline():
    fp = os.path.join(DATA_DIR, '_weibo_timeline.csv')
    fd = ','.join(['_id', 'mid62', 'uid', 'timestamp', 'text', 'likes', 'comments', 'forwards', 'reweibo', 'urls',
                   'media.play_count', 'media.type', 'media.urls', 'sent_from', 'location'])
    os.system('mongoexport -d yizhibo -c weibo_timeline --type csv -o {} --fields {}'.format(fp, fd))


def export_yizhibo_video():
    fp = os.path.join(DATA_DIR, '_yizhibo_lives.csv')
    fd = ','.join(['_id', 'uid', 'date', 'n_views', 'title', 'play.length', 'starttime', 'n_likes', 'n_messages'])
    os.system('mongoexport -d yizhibo -c replays_target --type csv -o {} --fields {}'.format(fp, fd))


def export_yizhibo_danmu():
    fp = os.path.join(DATA_DIR, '_yizhibo_danmu.csv')
    fd = ','.join(['_id', 'memberid', 'nickname', 'ts', 'replayid', 'content'])
    os.system('mongoexport -d yizhibo -c comments --type csv -o {} --fields {}'.format(fp, fd))


def main():
    print(__name__)
    export_taobao_rates()
    export_taobao_items()
    export_taobao_shops()
    export_weibo_users()
    export_weibo_timeline()
    export_yizhibo_video()
    export_yizhibo_danmu()
    export_taobao_items_30sold()


if __name__ == '__main__':
    main()
