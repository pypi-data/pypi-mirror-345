import pandas as pd
from tqdm.auto import tqdm, trange


def panelize(data, i, t, agg, fillna=None, rename=None, trange=None):
    if fillna is None:
        fillna = {}
    if rename is None:
        rename = {}

    def union(series):
        return reduce(set.union, [(set(r.split('|')) if r else set()) if isinstance(r, str) else r for r in series])

    def replace_agg(v):
        if isinstance(v, list):
            return [replace_agg(vv) for vv in v]
        if v in {'union', 'nuniques'}:
            v = union
        return v

    def fillgap(df):
        df = df.sort_values(by=t).set_index(t)
        if trange is not None:
            left, right = trange
            if left is None: left = df.index.min()
            if right is None: right = df.index.max() + 1
            df = df.reindex(pd.RangeIndex(left, right, name=t)).reset_index(t)
            df[i] = df[i].ffill().bfill()  #.fillna(method='ffill').fillna(method='bfill')
            df = df.fillna({k: fillna.get(k, 0) if v not in {'union', 'nuniques'} else '' for k, v in agg.items()})
        else:
            for k, v in agg.items():
                if v in {'union', 'nuniques'}:
                    df[k] = df[k].fillna('')
        # for k, v in agg.items():
        #     df[k] = df[k].fillna(fillna.get(k, 0) if v not in {'union', 'nuniques'} else '')
        return df

    tqdm.pandas()
    data = data.groupby([i, t], as_index=False).agg({k: replace_agg(v) for k, v in agg.items()})
    if trange is not None:
        data = data.groupby(i, as_index=False).progress_apply(fillgap)
    for k, v in agg.items():
        if v == 'union':
            data[f'{rename.get(k, k)}_nunique'] = data[k].apply(len)
        if v == 'nuniques':
            data[k] = data[k].apply(len)
    return data if rename is None else data.rename(columns=rename)
