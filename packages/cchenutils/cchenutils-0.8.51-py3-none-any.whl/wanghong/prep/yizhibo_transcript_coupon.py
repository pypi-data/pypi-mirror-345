import pandas as pd

from utils import DATA_DIR


def contains(string, words):
    for word in words:
        if word in string:
            return True
    return False


def main():
    df_videos = pd.read_csv('../analysis/yizhibo_video_clothes.csv')
    df_transcript = pd.read_csv(f'{DATA_DIR}/yizhibo_transcript.csv', dtype=str)
    df_transcript = df_transcript[df_transcript['Yizhibo_VID'].isin(df_videos[df_videos['sell'] == 1]['Yizhibo_VID'])]
    discount_keywords = ['优惠', '折扣', '一折', '二折', '三折', '四折', '五折', '六折', '七折', '八折', '九折']
    df_tb = df_transcript.loc[df_transcript['transcript'].apply(lambda x: contains(x, discount_keywords))] \
        .reset_index(drop=True)

    df_discount = df_tb.groupby(['Yizhibo_VID'])\
        .agg({'transcript': 'count'})\
        .reset_index()\
        .rename(columns={'transcript': 'has_discount'})

    df_videos = df_videos.merge(df_discount, how='left').fillna({'has_discount': 0})
    df_uids = pd.read_csv(f'{DATA_DIR}/uids.csv')
    df_videos = df_uids.merge(df_videos, how='right')
    df_videos.to_csv('../analysis/yizhibo_video_clothes_discount.csv', index=False)


if __name__ == '__main__':
    main()
