#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 2/1/20
# @File  : [wanghong] taobao_rates.py

'''
1. Add prefix to IDs
2. Identify default ratings
3. Identify real reviews
4. [REMOVED] Fill NA with 0s for purchases
5. Adjust sales_item for default ratings
6. [Moved] Adjust sales_item for nondefault ratings by 0-15 (and random 0-15) days
7. [Moved] Adjust sales_item by 3-5 days and random 3-5 days for all ratings
8. Other basic variables
9. [REMOVED] Handle 追加评论
'''

import csv
import sys
from datetime import datetime, timedelta

import pandas as pd
from tqdm.auto import tqdm

from prep.utils import DATA_DIR


def parse_default_rating(content):
    return 1 if content in {'评价方未及时做出评价,系统默认好评!', '15天内买家未作出评价'} else 0


def parse_valid_comment(content):
    return 0 if content in {'此用户没有填写评价。', '评价方未及时做出评价,系统默认好评!', '系统默认评论', '15天内买家未作出评价'} else 1


def main():
    print(__name__)



if __name__ == '__main__':
    main()
    pass


    clothes = set(pd.read_csv(f'../analysis/df_items_clothes.csv')['Taobao_IID'])

    csv.field_size_limit(1000000000)

    data = []
    with open(f'{DATA_DIR}/_taobao_rates.csv', encoding='utf-8') as i:
        csvreader = csv.DictReader(i)
        for row in tqdm(csvreader, desc='loading file'):
            if not all([row['_id'], row['itemid'], row['date']]):  # dropna
                continue
            if 'TI' + row['itemid'] not in clothes:
                continue
            if row['bidPriceMoney.currencyCode'] not in {'', 'CNY'}:
                continue
            try:
                row['_id'] = 'TR' + row['_id']
                row['itemid'] = 'TI' + row['itemid']
                row['date'] = datetime.strptime(row['date'], '%Y年%m月%d日 %H:%M').strftime('%Y-%m-%d')
                if not row['rate'] or not row['validscore']:
                    print('issue')
                row['rate'] = int(row['rate'])
                row['validscore'] = int(row['validscore'])
                row['default'] = parse_default_rating(row['content'])
                row['valid'] = parse_valid_comment(row['content'])
                del row['dayAfterConfirm']
                del row['lastModifyFrom']
                row['buyAmount'] = int(row['buyAmount']) if row['buyAmount'] and row['buyAmount'] != '0' else None
                row['bidPriceMoney.amount'] = float(amt) if (amt := row['bidPriceMoney.amount']) else None
                del row['bidPriceMoney.currencyCode']
                row['video'] = int(bool(row['video']))
                row['photos'] = len(eval(row['photos']))
                del row['raterType']
                row['vicious'] = int(row['vicious']) if row['vicious'] else None
                del row['useful']
                row['seller_replied'] = int(bool(row.pop('reply')))
                del row['appendList']
            except Exception as err:
                print(row)
                print(err)
                continue
            data.append(row)
    df_rates = (pd.DataFrame(data)
                .rename(columns={'_id': 'Taobao_RID',
                                 'itemid': 'Taobao_IID',
                                 'date': 'rate_date',
                                 'buyAmount': 'purchases'})
                .drop_duplicates(subset=['Taobao_RID', 'Taobao_IID', 'rate_date', 'content', 'user.nick',
                                         'purchases', 'bidPriceMoney.amount', 'promotionType', 'rate'])
                .drop(columns=['user.nick', 'content'])
                .reset_index(drop=True))

    # df_rates = (pd.read_csv(f'{DATA_DIR}/_taobao_rates.csv',  # nrows=10,
    #                         dtype={
    #                             '_id': str,
    #                             'itemid': str,
    #                             'bidPriceMoney.currencyCode': pd.CategoricalDtype(categories=['CNY'])},
    #                         encoding='utf-8',
    #                         usecols=[
    #                             '_id', 'itemid', 'date', 'rate', 'validscore', 'content',
    #                             'buyAmount',
    #                             'bidPriceMoney.amount', 'bidPriceMoney.currencyCode', 'video', 'photos',
    #                             'promotionType', 'user.nick', 'auction.sku', 'vicious',
    #                             'reply', 'appendList',
    #                             # 'dayAfterConfirm', 'lastModifyFrom', 'raterType', 'useful'
    #                         ],
    #                         on_bad_lines='warn')
    #             .dropna(subset=['date', 'itemid', '_id'])
    #             .assign(default= lambda x: x['content'].apply(parse_default_rating),
    #                     valid=lambda x: x['content'].apply(parse_valid_comment))
    #             .fillna({'vicious': 0})
    #             .rename(columns={'_id': 'Taobao_RID',
    #                              'itemid': 'Taobao_IID',
    #                              'date': 'rate_date',
    #                              'buyAmount': 'purchases',
    #                              'reply': 'seller_replied'})
    #             .drop_duplicates(subset=['Taobao_RID', 'Taobao_IID', 'rate_date', 'content', 'user.nick',
    #                                      'purchases', 'bidPriceMoney.amount', 'promotionType', 'rate'])
    #             .drop(columns=['user.nick', 'content', 'bidPriceMoney.currencyCode'])
    #             .reset_index(drop=True))
    # df_rates['photos'] = df_rates['photos'].fillna('[]').apply(lambda x: len(eval(x)) if x != '0' else 0)

    # df_rates['Taobao_RID'] = 'TR' + df_rates['Taobao_RID']
    # df_rates['Taobao_IID'] = 'TI' + df_rates['Taobao_IID']
    # df_rates['rate_date'] = df_rates['rate_date'].apply(
    #     lambda x: pd.to_datetime(datetime.strptime(x, '%Y年%m月%d日 %H:%M').strftime('%Y-%m-%d')))
    # df_rates['default'] = df_rates['content'].apply(parse_default_rating)
    # df_rates['valid'] = df_rates['content'].apply(parse_valid_comment)
    # df_rates['purchases'] = df_rates['purchases'].apply(lambda x: None if x == 0 or pd.isna(x) else x)
    # df_rates['promo'] = df_rates.pop('promotionType').fillna('').apply(lambda x: '活动促销' in x).astype(int)
    # df_rates['video'] = df_rates['video'].notnull().astype(int)
    # df_rates['seller_replied'] = df_rates.pop('reply').notnull().astype(int)
    # df_rates['validscore'] = df_rates['validscore'].astype(int)
    # df_rates['purchases'] = df_rates['purchases'].astype(int)
    # df_rates['content'] = df_rates.apply(lambda x: x['content'] if x['valid'] else '', axis=1)

    df_rates.to_csv(f'{DATA_DIR}/taobao_rates.csv', index=False)
    # df_rates.to_pickle(f'{DATA_DIR}/taobao_rates.pkl')



    # # Adjust sales_item for nondefault ratings by 0-15 (and random 0-15) days
    # rdates = {}
    # for dr in trange(0, 16, desc='Adjusting sales_item for reviewing process'):  # days for reviewing
    #     rdates[f'date_r{dr}'] = df_rates.apply(lambda x: adj_date_by(x['rate_date'], -dr * x['default']), axis=1)
    # seed(1)
    # rdates['date_rr'] = df_rates.apply(lambda x: adj_date_by(x['rate_date'], -randint(0, 15) * x['default']), axis=1)
    #
    # # Adjust sales_item by 3-5 days and random 3-5 days for all ratings
    # sales_item = {}
    # for col in tqdm(rdates.keys()):
    #     for ds in trange(3, 6, desc=col):  # days for shipping
    #         sales_item[f'{col}_s{ds}'] = rdates[col].apply(lambda x: adj_date_by(x, -ds))
    #     seed(1)
    #     sales_item[f'{col}_sr35'] = rdates[col].apply(lambda x: adj_date_by(x, -randint(3, 5)))
    #     seed(1)
    #     sales_item[f'{col}_sr15'] = rdates[col].apply(lambda x: adj_date_by(x, -randint(1, 5)))
    #
    # df_rates = pd.concat([df_rates, pd.DataFrame(sales_item)], axis=1)
    # df_rates.drop(columns=['appendList']).to_csv(f'{DATA_DIR}/taobao_rates.csv', index=False)

    # 追加评论
    # append_rates = []
    # for idx, row in df_rates[df_rates['appendList'].apply(lambda x: x != '[]')].iterrows():
    #     for rate in json.loads(row['appendList']):
    #         if rate['appendId'] == 0:
    #             continue
    #         Taobao_RID = 'TR' + rate['appendId']['$numberLong']
    #         Taobao_IID = row['Taobao_IID']
    #         rate_date = (datetime.strptime(row['rate_date'], '%Y-%m-%d') + timedelta(days=rate['dayAfterConfirm'])) \
    #             .strftime('%Y-%m-%d')
    #         photos = len(rate['photos'])
    #         video = len(rate['videos'])
    #         vicious = rate['vicious']
    #         content = rate['content']
    #         seller_replied = int(rate['reply'] is not None)
    #         append_rates.append([Taobao_RID, Taobao_IID, rate_date, photos, video, vicious, seller_replied, content])
    # df_append = pd.DataFrame(append_rates,
    #                          columns=['Taobao_RID', 'Taobao_IID',
    #                                   'rate_date', 'photos', 'video',
    #                                   'vicious', 'seller_replied', 'content'])
    # df_append.to_csv(f'{DATA_DIR}/taobao_appendrates.csv', index=False)