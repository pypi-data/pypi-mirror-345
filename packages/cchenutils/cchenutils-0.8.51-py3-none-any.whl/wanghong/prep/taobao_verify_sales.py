import json
from datetime import datetime, timedelta

import pandas as pd
from tqdm import tqdm

from taobao_rates import parse_default_rating
from utils import DATA_DIR

tqdm.pandas()


def calculate(x, df_rates):
    itemid = x['itemid']
    time_utc = x['sold_30d_date_utc']
    time_bjt = x['sold_30d_date_bjt']
    this_rates = df_rates[df_rates['itemid'] == itemid]
    t30_utc = time_utc - timedelta(days=30)
    t30_bjt = time_bjt - timedelta(days=30)
    this_rates_utc = this_rates[(this_rates['date'] <= time_utc) & (this_rates['date'] >= t30_utc)]
    this_rates_bjt = this_rates[(this_rates['date'] <= time_bjt) & (this_rates['date'] >= t30_bjt)]
    this_rates_utc_adj = this_rates[(this_rates['adj_date'] <= time_utc) & (this_rates['adj_date'] >= t30_utc)]
    this_rates_bjt_adj = this_rates[(this_rates['adj_date'] <= time_bjt) & (this_rates['adj_date'] >= t30_bjt)]
    return len(this_rates_utc), this_rates_utc['buyAmount'].sum(), \
           len(this_rates_bjt), this_rates_bjt['buyAmount'].sum(), \
           len(this_rates_utc_adj), this_rates_utc_adj['buyAmount'].sum(), \
           len(this_rates_bjt_adj), this_rates_bjt_adj['buyAmount'].sum()


def main():
    df_rates = pd.read_csv(f'{DATA_DIR}/_taobao_rates.csv'
                           , usecols=['_id', 'itemid', 'date', 'buyAmount', 'content']
                           , dtype=str
                           , converters={'buyAmount': int,
                                         'date': lambda x: datetime.strptime(x, '%Y年%m月%d日 %H:%M') if x else None}) \
        .dropna(subset=['date']) \
        .drop_duplicates(subset=['_id']) \
        .reset_index(drop=True)
    df_rates['buyAmount'] = df_rates['buyAmount'].apply(lambda x: 1 if x == 0 or not x else x)
    df_rates['default'] = df_rates['content'].apply(parse_default_rating)
    df_rates['adj_date'] = df_rates.apply(lambda x: x['date'] - timedelta(days=15) if x['default'] else x['date'], axis=1)

    itemids = set(df_rates['itemid'])
    df_30sales = pd.concat([pd.read_csv(f'{DATA_DIR}/_taobao_items_30sold_{i}.csv', dtype=str) for i in range(1, 4)]) \
        .dropna(subset=['sold_30d']) \
        .drop_duplicates() \
        .rename(columns={'_id': 'itemid'}) \
        .query('itemid in @itemids') \
        .reset_index(drop=True)
    df_30sales[['sold_30d_date_utc', 'sold_30d_date_bjt', 'sold_30d_amount']] = \
        df_30sales.apply(lambda x: [[(t := datetime.strptime(k, '%Y-%m-%d_%H:%M:%S')), t + timedelta(hours=8), v]
                                    for k, v in json.loads(x['sold_30d']).items()][0]
                         , axis=1, result_type='expand')
    df_30sales[['rates_utc', 'buyamount_utc', 'rates_bjt', 'buyamount_bjt',
                'rates_utc_adj', 'buyamount_utc_adj', 'rates_bjt_adj', 'buyamount_bjt_adj']] = \
        df_30sales.progress_apply(lambda x: calculate(x, df_rates), axis=1, result_type='expand')

    df_30sales = df_30sales.rename(columns={'itemid': 'Taobao_IID', 'shopid': 'Taobao_SID'})
    df_30sales['Taobao_SID'] = 'TS' + df_30sales['Taobao_SID']
    df_30sales['Taobao_IID'] = 'TI' + df_30sales['Taobao_IID']
    df_30sales.to_csv(f'{DATA_DIR}/taobao_items_30sold_utc.csv', index=False)


if __name__ == '__main__':
    # main()

    import pandas as pd
    import matplotlib.pyplot as plt
    import math
    from utils import DATA_DIR
    df_30sales = pd.read_csv(f'{DATA_DIR}/taobao_items_30sold_utc.csv')
    df_items = pd.read_csv(f'{DATA_DIR}/_taobao_items.csv', usecols=['_id', 'sales_item'], dtype={'_id': str}) \
        .rename(columns={'_id': 'Taobao_IID'})
    df_items['Taobao_IID'] = 'TI' + df_items['Taobao_IID']
    df_30sales = df_30sales.merge(df_items, on='Taobao_IID', how='left')
    df_30sales.to_csv(f'{DATA_DIR}/diff_sales.csv', index=False)

    b = (df_30sales['rates_bjt_adj'] - df_30sales['sales_item']).apply(lambda x: math.log(abs(x)+1))

    df_30sales.to_csv(f'{DATA_DIR}/taobao_items_30sold_utc_sales.csv', index=False)

    # b.to_csv(f'{DATA_DIR}/diff_sales.txt', index=False)
    b.hist(bins=100)#[(b < 100) & (b > -2)]
    plt.show()
    #
    # from scipy.stats import ttest_1samp
    #
    # ttest_1samp(b[(b < 2) & (b > -2)], 0)
