import pandas as pd

from prep.utils import DATA_DIR

df = pd.read_csv(f'{DATA_DIR}/taobao_rates_discounts.csv')