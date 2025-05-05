import pandas as pd

from utils import DATA_DIR


def contains(string, words):
    for word in words:
        if word in string:
            return True
    return False


def main():
    df_uids = pd.read_csv(f'{DATA_DIR}/uids.csv')
    data = pd.read_csv(f'{DATA_DIR}/weibo_timeline.csv') \
        .fillna({'text': '', 'sent_from': '', 'media.urls': '[]', 'urls': '[]', 'redirect_urls': '[]'})
    data = data[data['reweibo'].isna()]
    data = df_uids.merge(data, how='right')
    data['redirect_urls'] = data['redirect_urls'].apply(eval)
    data['media.urls'] = data['media.urls'].apply(eval)
    data['urls'] = data['urls'].apply(eval)
    data['media.play_count'] = data['media.play_count'].fillna('0').apply(lambda x: x[:-1]+'0000' if '万' in x else x)
    data['streaming_from'] = ''

    keywords_text_other = ['陌陌电台', '淘宝直播', '淘寶直播', '微淘直播', '斗鱼直播', '战旗直播', '熊猫直播', 'tb直播',
                           '我正在陌陌', '全民K歌', '美拍直播']
    keywords_sent_other = ['陌陌', '淘宝主播', '花椒直播', '红豆角直播', '看点-直播间', '映客直播', '战鲨直播', '大美人直播',
                           '全民K歌']
    keywords_url_other = ['www.meipai.com/live',
                          'live-api.immomo.com',
                          'tb.cn',
                          'inke.cn',
                          'www.kuaishou.com/wap/live',
                          'huajiao.com']
    data.loc[(data['text'].apply(lambda x: contains(x, keywords_text_other))) |
             ((data['sent_from'].apply(lambda x: contains(x, keywords_sent_other))) & (data['contains_streaming'])) |
             (data['redirect_urls'].apply(lambda x: contains(x[0], keywords_url_other) if len(x) else False)),
             'streaming_from'] = 'other'

    data.loc[(((data['text'].apply(lambda x: contains(x, ['微博直播', '一直播', '正在直播中，场面异常火爆，小伙伴们速来围观']))) |
               (data['sent_from'].apply(lambda x: contains(x, ['微博直播', '一直播']) and '组件' not in x))) &
              (data['contains_streaming'])) |
             (data['redirect_urls'].apply(lambda x: contains(x[0], ['weibo.com/l/wblive']) if len(x) else False)),
             'streaming_from'] = 'weibo'
    data.loc[data['media.type'] == 'live', 'streaming_from'] = 'weibo'

    data = data.fillna({'likes': 0, 'comments': 0, 'forwards': 0, 'media.play_count': 0})
    data['n_videos'] = (data['media.type'] == 'video').astype(int)
    data['n_images'] = data.apply(lambda x: len(x['media.urls']) if x['media.type'] == 'image' else 0, axis=1)

    data.to_csv(f'{DATA_DIR}/weibo_timeline_streaming.csv', index=False)


if __name__ == '__main__':
    main()
