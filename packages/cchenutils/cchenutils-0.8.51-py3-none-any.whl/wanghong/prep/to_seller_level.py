import pandas as pd

df = pd.read_csv('../analysis/df_panel_items_sellerrate.csv')
agg_opts = {
    'n_ratings': 'mean',
    'purchases': 'mean',
    'avail_purchases': 'mean',
    'promo': 'mean',
    'seller_rate.lvl_running': 'first',
    'n_weibos': 'first',
    'likes': 'first',
    'comments': 'first',
    'forwards': 'first',
}

df_panel = df.groupby(['Taobao_SID', 'time'], as_index=False).agg(agg_opts)
df_panel.to_csv('../analysis/df_panel_sellers.csv', index=False)

# import os
# os.environ["R_HOME"] = r"C:\Program Files\R\R-4.2.0"
# from rpy2.robjects import r, pandas2ri
# pandas2ri.activate()
# rdf = pandas2ri.py2rpy(df)
# print(rdf)
