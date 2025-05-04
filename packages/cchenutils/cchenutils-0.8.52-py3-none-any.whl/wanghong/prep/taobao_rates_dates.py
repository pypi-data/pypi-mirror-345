from datetime import datetime, timedelta
from random import seed, randint
import numpy as np

import pandas as pd
from tqdm.auto import tqdm, trange

from prep.utils import DATA_DIR, calc_time


def adj_date_by(date, days):
    this_date = datetime.strptime(date, u'%Y-%m-%d') if isinstance(date, str) else date
    this_date += timedelta(days=days)
    return this_date  #.strftime('%Y-%m-%d')


def main():
    print(__name__)

    df_users = pd.read_csv(f'{DATA_DIR}/uids.csv', usecols=['Taobao_SID', 'Yizhibo_UID'])
    df_first = pd.read_csv(f'{DATA_DIR}/yizhibo_first.csv', parse_dates=['first_stream_date'])
    df_items = pd.read_csv(f'../prep2/taobao_items.csv', usecols=['Taobao_SID', 'Taobao_IID'])
    df_rates = pd.read_csv(f'{DATA_DIR}/taobao_rates.csv', #nrows=100,
                           usecols=['Taobao_RID', 'Taobao_IID', 'rate_date', 'default'],
                           parse_dates=['rate_date'])
    print(df_rates.shape)
    df = (df_users
          .merge(df_items, on='Taobao_SID', how='inner')
          .merge(df_first, on='Yizhibo_UID', how='inner')
          .merge(df_rates, on='Taobao_IID', how='inner'))

    # Adjust sales_item for default ratings
    df['date'] = df.apply(lambda x: adj_date_by(x['rate_date'], -15 * x['default']), axis=1)
    df['time'] = df['date'].apply(calc_time)
    df['daysafter'] = (df['date'] - df['first_stream_date']).dt.days

    # Adjust sales_item for nondefault ratings by 0-15 (and random 0-15) days
    seed(1)
    df['rand015'] = pd.Series(np.random.randint(0, 16, len(df['date'])))
    rdates = {}
    for dr in trange(0, 16, desc='Adjusting sales_item for reviewing process'):  # days for reviewing
        rdates[f'date_r{dr}'] = df.apply(lambda x: adj_date_by(x['date'], -dr * (not x['default'])), axis=1)
    rdates['date_rr'] = df.apply(lambda x: adj_date_by(x['date'], -x['rand015'] * (not x['default'])), axis=1)

    # Adjust sales_item by 3-5 days and random 3-5 days for all ratings
    seed(1)
    rand35 = pd.Series(np.random.randint(3, 6, len(df['date'])))
    seed(1)
    rand15 = pd.Series(np.random.randint(1, 6, len(df['date'])))
    dates = {}
    for col, rdate in tqdm(rdates.items()):
        if not col.startswith('date'):
            continue
        for ds in trange(1, 6, desc=col):  # days for shipping
            dates[f'{col}_s{ds}'] = rdate.apply(lambda x: adj_date_by(x, -ds))
        dates[f'{col}_sr35'] = pd.Series(map(adj_date_by, rdate, -rand35))
        dates[f'{col}_sr15'] = pd.Series(map(adj_date_by, rdate, -rand15))
        # seed(1)
        # sales_item[f'{col}_sr35'] = rdate.apply(lambda x: adj_date_by(x, -randint(3, 5)))
        # seed(1)
        # sales_item[f'{col}_sr15'] = rdate.apply(lambda x: adj_date_by(x, -randint(1, 5)))

    times = {}
    for col, date in tqdm(dates.items()):
        times[f'time{col[4:]}'] = date.apply(calc_time)
        times[f'daysafter{col[4:]}'] = (date - df['first_stream_date']).dt.days

    df_out = pd.concat([df[['Taobao_RID', 'date', 'time', 'daysafter']], pd.DataFrame(times)], axis=1)
    df_out.to_csv(f'{DATA_DIR}/taobao_rates_dates.csv', index=False)

if __name__ == '__main__':
    main()
