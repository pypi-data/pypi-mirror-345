'''
archive for 追评
'''


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