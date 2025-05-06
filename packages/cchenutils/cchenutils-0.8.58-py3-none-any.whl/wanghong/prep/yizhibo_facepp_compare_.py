import pandas as pd
from utils import DATA_DIR

df = pd.read_csv(f'{DATA_DIR}/yizhibo_facepp_compare.csv')
a = df.groupby(['Yizhibo_UID'], as_index=False).agg({'confidence': ['min', 'max', 'mean']})