import pandas as pd
from utils import DATA_DIR


def find_max(df, col):
    return df[df[col] == df[col].max()].reset_index(drop=True).iloc[0]


if __name__ == '__main__':
    df = pd.read_csv(f'{DATA_DIR}/yizhibo_face.csv', dtype=str)
    df['probabilities'] = df['probabilities'].fillna('0').apply(lambda x: [float(p) for p in x.split('|')])
    df['faces'] = df['probabilities'].apply(len)
    df['probs'] = df['probabilities'].apply(lambda x: sum(x) / len(x))

    frames = df.groupby(['Yizhibo_UID', 'Yizhibo_VID', 'snippet']).apply(lambda x: find_max(x, 'probs'))\
        .reset_index(drop=True)
    frames = frames[frames['probs'] != 0]

    frames.to_csv(f'{DATA_DIR}/yizhibo_faces_snippet.csv', index=False)
