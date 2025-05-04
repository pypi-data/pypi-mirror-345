import csv
import json
import os
import re
import shutil

import pandas as pd
from dask import dataframe as dd
from ordered_set import OrderedSet

from .dictutils import Dict

# from cchenutils import Dict
csv.field_size_limit(10_000_000)


def csv_write(data, fp, headers=None):
    writeheader = not os.path.exists(fp) and headers is not None
    rows = data if isinstance(data, list) else [data]
    rows = (dict(zip(headers, Dict(d).gets(headers, serialize=True))) for d in rows)

    with open(fp, 'a', encoding='utf-8') as o:
        writer = csv.DictWriter(o, fieldnames=headers, lineterminator='\n')
        if writeheader:
            writer.writeheader()
        writer.writerows(rows)


def jsonl_write(data, fp):
    rows = data if isinstance(data, list) else [data]
    with open(fp, 'a', encoding='utf-8') as o:
        o.writelines(json.dumps(d) + '\n' for d in rows)


def txt_write(data, fp):
    lines = data if isinstance(data, list) else [data]
    with open(fp, 'a', encoding='utf-8') as o:
        o.writelines(str(line) + '\n' for line in lines)


def write(data, fp, *args):
    """
    Writes data to a file based on its extension.

    Supported formats:
    - For CSV files (.csv), the tuple contains:
      - `fp` (str): The file path.
      - `data` (dict or list of dicts): The data to be written.
      - `headers` (iterable): The headers for the CSV columns.
      - `scrape_time` (optional, datetime in str): The time of scraping, added as the first column.
    - For JSON Line (.jsonl) files, the tuple contains:
      - `fp` (str): The file path.
      - `data` (dict or list of dicts): The data to be written.
    """
    if not data:
        return False
    data = data if isinstance(data, list) else [data]
    match os.path.splitext(fp)[1].lower():
        case '.csv':
            match len(args):
                case 0:
                    headers = None
                case 1:
                    headers = args[0]
                case _:
                    headers = ['scrape_time'] + args[0]
                    for d in data:
                        d['scrape_time'] = args[1]
            csv_write(data, fp, headers)
        case '.jsonl':
            jsonl_write(data, fp)
        case '.lst' | '.txt':
            txt_write(data, fp)
        case _:
            print(f'Unsupported file type for {fp}')
    return True


def read_id(fp, ids=None, dtype=None, *, agg=None, filters=None, agg_filters=None, engine='pandas') -> Dict | OrderedSet:
    """
    Read data from a CSV file based on specified ID field(s), with optional filtering and aggregation.

    Args:
        fp (str): The file path to the CSV file.
        ids (str | iterable[str]): Field name(s) used to group the rows.
        dtype (dict, optional): Optional dictionary specifying column types.
        agg (dict, optional): Aggregation to apply, specified as a {field: aggregation} dictionary.
            Currently only one field-aggregation pair is supported.
            Use 'range' to return (min, max) tuples.
            If `agg` is used, `agg_filters` will be ignored
        filters (dict, optional): Filter conditions on individual rows, as {field: condition}.
            The condition can be:
              - A scalar (for exact match),
              - A bool (True for not-null, False for null),
              - A regex pattern (re.Pattern),
              - A callable (returns True/False per value).
        agg_filters (dict, optional): Filter rows based on agg'd data, as {field: (agg, condition)}.
            Conditions are same as above.
            If `agg` is used, `agg_filters` will be ignored
        engine (str): Backend to use for reading and processing. Either 'pandas' or 'dask'. Defaults to 'pandas'.

    Returns:
        Dict | OrderedSet:
            - If `agg` is provided, returns a Dict mapping ID(s) to aggregated values.
                If 'range' is used in the agg, values will be (min, max) tuples
            - Otherwise, returns an OrderedSet of distinct ID(s) after filtering.

    Example:
        >>> fp = "examples/comments.csv"
        >>> read_id(fp, 'mid',
        ...         filters={'cid': lambda x: int(x) > 5159662870334851},
        ...         agg_filters={'cid': ('count', lambda x: x > 99)})
        OrderedSet(['5161103483472724', '5161103554775418', '5161105569353685', '5161106621071564'])

        >>> read_id(fp, ('mid', 'cid'),
        ...         agg={'cid': 'range'},
        ...         filters={'cid': lambda x: int(x) > 5161130667278800})
        {('5161101911133285', '5161130675669325'): ('5161130675669325', '5161130675669325'),
         ('5161105569353685', '5161130830860213'): ('5161130830860213', '5161130830860213'),
         ('5161109302283398', '5161130729932350'): ('5161130729932350', '5161130729932350'),
         ('5161110719432632', '5161130729147695'): ('5161130729147695', '5161130729147695')}
    """
    if not os.path.exists(fp):
        return Dict() if agg is not None else OrderedSet()

    if ids is None:
        with open(fp) as f:
            return OrderedSet(line.strip() for line in f)

    if isinstance(ids, str):
        ids = [ids]
    else:
        ids = list(ids)

    cols = set(ids)
    if agg is not None:
        cols |= set(agg.keys())
    if filters is not None:
        cols |= set(filters.keys())
    if agg_filters is not None:
        cols |= set(agg_filters.keys())

    if dtype is None:
        dtype = {}
    dtype |= {idf: str for idf in ids if idf not in dtype}
    if filters is not None:
        dtype |= {k: 'object' for k, v in filters.items()
                  if k not in dtype and (agg is None or k not in agg) and (agg_filters is None or k not in agg_filters)}

    df = (dd if engine == 'dask' else pd).read_csv(fp, dtype=dtype, usecols=list(cols), encoding='utf-8')

    def _apply_filter(df, field, expected, backend='pandas'):
        match expected:
            case bool():  # True or False
                return df[df[field].notnull()] if expected else df[df[field].isnull()]
            case re.Pattern():  # Regex filter
                return df[df[field].str.contains(expected)]
            case func if callable(func):  # Custom function filter
                if backend == 'dask':
                    return df.map_partitions(lambda df: df[df[field].map(func)], meta=df)
                else:
                    return df[df[field].apply(func)]
            case _:  # Exact match
                return df[df[field] == expected]

    if filters:
        for field, expected in filters.items():
            df = _apply_filter(df, field, expected, backend=engine)

    if agg is not None:
        k, v = agg.popitem()
        if v == 'range':
            aggd = df.groupby(ids).agg({k: ['min', 'max']})
            if engine == 'dask':
                aggd = aggd.compute()
            return Dict(aggd.apply(lambda row: (row[(k, 'min')], row[(k, 'max')]), axis=1).to_dict())
        else:
            aggd = df.groupby(ids).agg({k: v})
            if engine == 'dask':
                aggd = aggd.compute()
            return Dict(aggd.apply(lambda row: row[k], axis=1).to_dict())

    if agg_filters is not None:
        # {'created_at_ts': ('count', lambda x: x > 5)}
        df = df.groupby(ids).agg({k: a for k, (a, v) in agg_filters.items()})
        for k, (a, v) in agg_filters.items():
            df = _apply_filter(df, k, v, backend=engine)
        df = df.reset_index()

    if engine == 'dask':
        df = df.compute()

    if len(ids) == 1:
        return OrderedSet(df[ids[0]].drop_duplicates().tolist())
    else:
        return OrderedSet(df[ids].drop_duplicates().apply(tuple, axis=1).tolist())


def dedup(fp, subset=None):
    temp_fp = f'{fp}.tmp'
    try:
        os.rename(fp, temp_fp)
        df = pd.read_csv(temp_fp, dtype=str, encoding='utf-8')
        df.drop_duplicates(subset=subset, inplace=True)
        df.to_csv(fp, index=False, encoding='utf-8')
        os.remove(temp_fp)
    except Exception:
        if os.path.exists(temp_fp):
            shutil.move(temp_fp, fp)


if __name__ == '__main__':
    fp = "examples/comments.csv"
    read_id(fp, 'mid', filters={'cid': lambda x: int(x) > 5159662870334851}, agg_filters={'cid': ('count', lambda x: x > 99)})


    read_id(fp, ('mid', 'cid'),
                agg={'cid': 'range'},
                filters={'cid': lambda x: int(x) > 5161130667278800})
