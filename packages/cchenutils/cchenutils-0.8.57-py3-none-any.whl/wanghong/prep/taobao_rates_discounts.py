import pandas as pd

from prep.utils import DATA_DIR
from collections import Counter

def calc_discount(x):
    bid = x['bidPriceMoney.amount']
    try:
        promo = float(x['promo'])
    except:
        promo = 999999999999999999999999999

    try:
        price = float(x['price'])
    except:
        price = 999999999999999999999999999

    if bid in {x['price_bidhigh'], x['price_bidmost'], promo, price}:
        return 0
    p1 = bid / x['price_bidhigh']
    p2 = p2 if (p2 := bid / promo) <= 1 else 0
    p3 = p3 if (p3 := bid / price) <= 1 else 0
    p4 = p4 if (p4 := bid / x['price_bidmost']) <= 1 else 0
    return 1 - max(p1, p2, p3, p4)


def get_bid_most(x):
    c = Counter(x)
    total = sum(c.values())
    # return sorted([(key, value / total) for key, value in c.items()], key=lambda x: -x[1])
    pm, cm = sorted([(key, value / total) for key, value in c.items()], key=lambda x: -x[1])[0]
    return pm if cm >= 0.5 else None


def fix_err_bid(x):
    if pd.isna(bid := x['bidPriceMoney.amount']):
        return None
    if bid != 999:
        return bid

    if not pd.isna(promo := x['promo']) and '-' in promo:
        prc1 = float(promo.split('-')[0])
        prc2 = float(promo.split('-')[1])
        return bid if prc1 <= bid <= prc2 else None

    if not pd.isna(prc := x['price']) and  '-' in prc:
        prc1 = float(prc.split('-')[0])
        prc2 = float(prc.split('-')[1])
        return bid if prc1 <= bid <= prc2 else None


def main():
    print(__name__)

    df_items = pd.read_csv(f'../prep2/taobao_items.csv', dtype=str,
                           usecols=['Taobao_SID', 'Taobao_IID', 'title', 'price', 'promo'])
    df_rates = (pd.read_csv(f'{DATA_DIR}/taobao_rates.csv', #nrows=10000,
                            usecols=['Taobao_RID', 'Taobao_IID', 'auction.sku', 'bidPriceMoney.amount',
                                     'promotionType', 'default'],
                            dtype={'bidPriceMoney.amount': float})
                .dropna(subset=['bidPriceMoney.amount'])
                .fillna({'auction.sku': ''})
                .merge(df_items, on=['Taobao_IID'], how='inner'))
    df_rates['bidPriceMoney.amount'] = df_rates.apply(fix_err_bid, axis=1)

    df_prices_bidhigh = (df_rates.groupby(['Taobao_IID', 'auction.sku'], as_index=False)
                         .agg({'bidPriceMoney.amount': 'max'})
                         .rename(columns={'bidPriceMoney.amount': 'price_bidhigh'}))
    df_prices_bidmost = (df_rates.groupby(['Taobao_IID'], as_index=False)
                         .agg({'bidPriceMoney.amount': get_bid_most})
                         .rename(columns={'bidPriceMoney.amount': 'price_bidmost'}))
    df_rates = (df_rates
                .merge(df_prices_bidhigh, on=['Taobao_IID', 'auction.sku'], how='left')
                .merge(df_prices_bidmost, on=['Taobao_IID'], how='left')
                )
    df_rates['discount'] = df_rates.apply(calc_discount, axis=1)
    # df_rates = df_rates.merge(df_items, on=['Taobao_IID'], how='inner')
    (df_rates.dropna(subset=['discount'])[['Taobao_RID', 'discount']]
     .to_csv(f'{DATA_DIR}/taobao_rates_discounts.csv', index=False))
    # _a = df_rates.groupby(['Taobao_IID', 'title'], as_index=False).agg({'discount': 'max'})
    # a = df_rates.merge(_a[_a['discount']>=0.5],
    #                    on=['Taobao_IID', 'title', 'discount'], how='inner')
    #
    # df_items2 = pd.read_csv(f'../analysis/df_items_clothes.csv')
    # a = a[a['Taobao_IID'].isin(df_items2['Taobao_IID'])]
    #
    # b = df_rates[df_rates['Taobao_IID'] == 'TI561107478841']
    # df_prices_bidmost[df_prices_bidmost['Taobao_IID'] == 'TI561107478841']
    #
    # c = df_rates[df_rates['promo'].apply(lambda x: not pd.isna(x) and '-' in x)]

    (df_rates.loc[df_rates['default'] == 0].dropna(subset=['discount'])
     .groupby('Taobao_SID', as_index=False).agg({'discount': 'mean'})
     .to_csv(f'{DATA_DIR}/taobao_rates_discounts_user.csv', index=False))


if __name__ == '__main__':
    main()
