from typing import Optional, Union, Tuple, List, Dict
import re
from datetime import datetime
import pandas as pd
import requests
import json
import hashlib
import numpy as np
import pyarrow.parquet as pq
from io import BytesIO
import boto3
import polars as pl
import plotly.graph_objects as go
# from fastapi import HTTPException ## Dee

import pyarrow.parquet as pq

from sovai.api_config import ApiConfig
from sovai.errors.sovai_errors import InvalidInputData
from sovai.utils.converter import convert_data2df
from sovai.utils.stream import stream_data, stream_data_pyarrow
from sovai.utils.datetime_formats import datetime_format

from sovai.utils.client_side import client_side_frame
from sovai.utils.client_side_s3 import load_frame_s3
from sovai.utils.client_side_s3_part_high import load_frame_s3_partitioned_high


## Note run these for TEST - IT COULD BE HERE some silent problems
try:
    from sovai.extensions.pandas_extensions import CustomDataFrame
    from sovai.utils.plot import plotting_data
    HAS_FULL_INSTALL = True
except ImportError:
    HAS_FULL_INSTALL = False

def is_full_installation():
    return HAS_FULL_INSTALL

# client_side_frame is the one for very quick public files.

# Now you can call the method directly on any DataFrame with a 'date' index and 'prediction' column
# df_breakout.get_latest()


# Wall time: 2min 14s (pyarrow via fastapi)
# Wall time: 1min 38s (pandas via fastapi)
# Wall time: 50s (direct via gcp)


# Global cache
_query_cache = {}

def load_df_from_wasabi(bucket_name, file_name, access_key, secret_key):
    import boto3
    s3_client = boto3.client(
        "s3",
        endpoint_url="https://s3.wasabisys.com",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    parquet_buffer = BytesIO()
    s3_client.download_fileobj(bucket_name, file_name, parquet_buffer)
    parquet_buffer.seek(0)
    df = pq.read_table(source=parquet_buffer).to_pandas()
    return CustomDataFrame(df) if HAS_FULL_INSTALL else df



def is_all(tickers):
    # Include "" in the pattern list
    PATTERN = ["ENTIRE", "ALL", "FULL", ""]

    # Return False if tickers is None
    if tickers is None:
        return False

    # Check if tickers is a string and not a list, then convert it to a list
    if isinstance(tickers, str):
        tickers = [tickers]

    # Check if any ticker matches the pattern
    return any(ticker.upper() in PATTERN for ticker in tickers)


import pandas as pd
import polars as pl
from typing import Union


def read_parquet(url: str, use_polars: bool = False) -> Union[pd.DataFrame, pl.DataFrame]:
    if use_polars:
        return pl.read_parquet(url)
    else:
        df = pd.read_parquet(url)
        return CustomDataFrame(df) if HAS_FULL_INSTALL else df
    

import pandas as pd
from typing import Union, List

def filter_data(
    data: Union[pd.DataFrame, 'pl.DataFrame'],
    columns: Union[str, List[str]] = None,
    start_date: str = None,
    end_date: str = None,
    use_polars: bool = False
) -> Union[pd.DataFrame, 'pl.DataFrame']:
    """
    Filter the data based on specified columns and date range.
    Always includes 'ticker', 'date', and 'calculation' columns if they exist in the original DataFrame.
    
    :param data: Input DataFrame (pandas or polars)
    :param columns: Columns to select (string or list of strings)
    :param start_date: Start date for filtering (string in 'YYYY-MM-DD' format)
    :param end_date: End date for filtering (string in 'YYYY-MM-DD' format)
    :param use_polars: Boolean indicating whether to use polars instead of pandas
    :return: Filtered DataFrame
    """
    if use_polars:
        import polars as pl
        
        # Prepare columns list
        if columns:
            if isinstance(columns, str):
                columns = columns.split(',')
            columns = [col.strip() for col in columns]
        else:
            columns = data.columns.to_list()
        
        # Always include 'ticker', 'date', and 'calculation' if they exist
        for col in ['calculation', 'date', 'ticker']:
            if col in data.columns and col not in columns:
                columns.insert(0, col)
        
        # Column filtering
        data = data.select(columns)
        
        # Date filtering
        if start_date or end_date:
            if 'date' in data.columns:
                if start_date:
                    data = data.filter(pl.col('date') >= pl.Date.parse(start_date))
                if end_date:
                    data = data.filter(pl.col('date') <= pl.Date.parse(end_date))
            else:
                # Assume date is in index if not in columns
                data = data.with_row_count('temp_index')
                if start_date:
                    data = data.filter(pl.col('temp_index').cast(pl.Date) >= pl.Date.parse(start_date))
                if end_date:
                    data = data.filter(pl.col('temp_index').cast(pl.Date) <= pl.Date.parse(end_date))
                data = data.drop('temp_index')
    
    else:
        # Prepare columns list
        if columns:
            if isinstance(columns, str):
                columns = columns.split(',')
            columns = [col.strip() for col in columns]
        else:
            columns = list(data.columns)
        
        # Always include 'ticker', 'date', and 'calculation' if they exist
        for col in ['calculation', 'date', 'ticker']:
            if col in data.columns and col not in columns:
                columns.insert(0, col)
        
        # Column filtering
        data = data[columns]
        
        if start_date or end_date:
            if 'date' in data.columns:
                data['date'] = pd.to_datetime(data['date'])
                if start_date:
                    data = data[data['date'] >= pd.to_datetime(start_date)]
                if end_date:
                    data = data[data['date'] <= pd.to_datetime(end_date)]
            elif isinstance(data.index, pd.DatetimeIndex):
                if start_date:
                    data = data[data.index >= pd.to_datetime(start_date)]
                if end_date:
                    data = data[data.index <= pd.to_datetime(end_date)]
            elif isinstance(data.index, pd.MultiIndex) and any(isinstance(level, pd.DatetimeIndex) for level in data.index.levels):
                date_level = next(level for level in data.index.levels if isinstance(level, pd.DatetimeIndex))
                if start_date:
                    data = data[data.index.get_level_values(date_level.name) >= pd.to_datetime(start_date)]
                if end_date:
                    data = data[data.index.get_level_values(date_level.name) <= pd.to_datetime(end_date)]
            else:
                print("Warning: Unable to filter by date. Date column or index not found.")
    
    
    return data

# Global cache
_query_cache = {}

### |||||||||||||||||| VERY IMPORTANT, IF HAVE FULL DATAFRAME ADD THE PATH HERE |||||||||||||||||| ###

## None means no ticker. "" Mean ticker but on parquet for all.

endpoint_to_ticker = {
    "/risks": "",
    "/government/traffic/domains": "",
    "/government/traffic/agencies": "",
    "/risks": "",
    "/bankruptcy": "",
    "/bankruptcy/shapleys": "",
    "/bankruptcy/description": "",
    "/corprisk/accounting": "",
    "/corprisk/events": "",
    "/corprisk/misstatement": "",
    "/corprisk/risks": "",
    "/bankruptcy/risks": "",
    "/breakout": "",
    "/breakout/median": "",
    "/institutional/trading": "",
    "/institutional/flow_prediction": "",
    "/news/daily": "",
    "/news/match_quality": "",
    "/news/match_quality": "",
    "/news/within_article": "",
    "/news/relevance": "",
    "/news/magnitude": "",
    "/news/sentiment": "",
    "/news/article_count": "",
    "/news/associated_people": "",
    "/news/associated_companies": "",
    "/news/tone": "",
    "/news/positive": "",
    "/news/negative": "",
    "/news/polarity": "",
    "/news/activeness": "",
    "/news/pronouns": "",
    "/news/word_count": "",
    "/news/sentiment_score": None,
    "/insider/trading": "",
    "/wikipedia/views": "",
    # "/spending/contracts": "",
    "/spending/details": "",
    # "/spending/transactions": "",
    "/spending/products": "",
    "/spending/location": "",
    "/spending/compensation": "",
    "/spending/competition": "",
    "/spending/entities": "",
    "/accounting/weekly": "",
    "/visas/h1b": "",
    "/factors/accounting": "",
    "/factors/alternative": "",
    "/factors/comprehensive": "",
    "/factors/coefficients": "",
    "/factors/standard_errors": "",
    "/factors/t_statistics": "",
    "/factors/model_metrics": "",
    "/ratios/normal": "",
    "/ratios/relative": "",
    "/movies/boxoffice": "",
    "/complaints/private": "",
    "/complaints/public": "",
    "/short/over_shorted": "",
    "/short/volume": "",
    "/earnings/surprise": "",
    "/news/sentiment_score": "",
    "/news/topic_probability": "",
    "/news/polarity_score": "",
    "/macro/features": "",
    "/congress": "",
    "/market/closeadj": "",
    "/lobbying/public": "",

    "/liquidity/price_improvement":"",
    "/liquidity/market_opportunity":"",



    ## remember to add leading "/"
    "/trials/predict": "",
    "/trials/describe": "",
    "/trials/all/predict": "",
    "/trials/all/decribe": "",
    "/trials/all": ""


}

## There are give types of file retrievals
# Postgres - SQL
# Large Parquet Wasabi - Via FastaAPI
# Small Parquet Pandas GCP - Via FastaAPI
# Small Parquet Pyarrow GCP - Via FastaAPI (Same speed above)
# Small Parquet GCP Pub - Via FastaAPI (Same speed above) - By far the best


def normalize_endpoint(endpoint):
    return endpoint.strip("/").strip()


## If you also want access by full file, please also add to endpoint_to_ticker



# Define your endpoint sets
client_side_endpoints_gcs = {
    "ratios/relative",
    "market/prices",
    "market/closeadj",
    "short/volume",
    "complaints/public",
    "complaints/private",
    "lobbying/public",
}

client_side_endpoints_s3 = {
    "sec/10k",
    "trials/predict",
    "trials/describe",
    "trials/all/predict",
    "trials/all/decribe",
    "trials/all",
}

client_side_endpoints_s3_part_high = {
    "patents/applications",
    "patents/grants",
    "clinical_trials",
    "spending/awards"


}

# Create a list of handlers
handlers = [
    (client_side_endpoints_gcs, client_side_frame, "Grabbing GCS client side"),
    (client_side_endpoints_s3, load_frame_s3, "Grabbing S3 client side"),
    (client_side_endpoints_s3_part_high, load_frame_s3_partitioned_high, "Grabbing S3 Partitioned High client side"),
]


# In your main function or wherever this logic is implemented:


def get_ticker_from_endpoint(endpoint: str, tickers, endpoint_to_ticker_map):
    """
    Returns the appropriate ticker value based on the endpoint and tickers.

    :param endpoint: The endpoint string.
    :param tickers: The current tickers value.
    :param endpoint_to_ticker_map: A dictionary mapping endpoints to ticker values.
    :return: The ticker value from the map if the endpoint is found and tickers is None or False, otherwise the original tickers.
    """
    if tickers is None or tickers is False:
        # Check if the endpoint is in the map and return its value, else return the original tickers
        return endpoint_to_ticker_map.get(endpoint, tickers)
    return tickers


class VerboseMode:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def vprint(self, *args, **kwargs):
        if self.verbose:
            print(*args, **kwargs)

    def toggle_verbose(self, verbose=None):
        if verbose is None:
            self.verbose = not self.verbose
        else:
            self.verbose = verbose


verbose_mode = VerboseMode()


def print_tickers_value(tickers):
    if tickers is None:
        verbose_mode.vprint("tickers is None")
    elif tickers is False:
        verbose_mode.vprint("tickers is False")
    else:
        verbose_mode.vprint(f"tickers is: {tickers}")


def map_synonyms(params):
    synonym_mapping = {
        "start": "start_date",
        "from_date": "start_date",
        "end": "end_date",
        "to_date": "end_date",
        "ticker": "tickers",
        "symbol": "tickers",
        "columns_name": "columns",
        "col": "columns",
        "cols": "columns",
    }

    return {synonym_mapping.get(key, key): value for key, value in params.items()}


import pandas as pd
import re
from collections import defaultdict


def find_tickers(sample_identifiers, df_codes, verbose=False):
    # Classify sample identifiers using regular expressions
    cusip_pattern = re.compile(r'^[A-Za-z0-9]{9}$')
    cik_pattern = re.compile(r'^\d{10}$')
    openfigi_pattern = re.compile(r'^BBG[A-Za-z0-9]{9}$')

    classified = defaultdict(set)
    for identifier in sample_identifiers:
        if identifier and identifier != 'None':
            identifier = str(identifier).strip()
            if openfigi_pattern.match(identifier):
                classified['openfigis'].add(identifier)
            elif cik_pattern.match(identifier):
                classified['ciks'].add(identifier)
            elif cusip_pattern.match(identifier):
                classified['cusips'].add(identifier)
            else:
                classified['tickers'].add(identifier)

    # Prepare DataFrame columns for vectorized operations
    ticker_columns = ['ticker', 'ticker_1', 'ticker_2', 'ticker_3', 'ticker_4']
    cusip_columns = ['cusip', 'cusip_1']

    # Create boolean masks for each identifier type
    masks = pd.DataFrame(index=df_codes.index)

    # Direct ticker matches
    masks['ticker_match'] = df_codes['ticker'].isin(classified['tickers'])

    # Alternative ticker matches
    alt_ticker_df = df_codes[ticker_columns[1:]]
    masks['alt_ticker_match'] = alt_ticker_df.isin(classified['tickers']).any(axis=1)

    # CUSIP matches
    cusip_df = df_codes[cusip_columns]
    masks['cusip_match'] = cusip_df.isin(classified['cusips']).any(axis=1)

    # CIK matches
    masks['cik_match'] = df_codes['cik'].isin(classified['ciks'])

    # OpenFIGI matches
    masks['openfigi_match'] = df_codes['top_level_openfigi_id'].isin(classified['openfigis'])

    # Combine matches where the 'ticker' is valid
    masks['valid_ticker'] = masks['ticker_match'] | masks['cusip_match'] | masks['cik_match'] | masks['openfigi_match']

    # Now, we only include rows where:
    # - The 'ticker' is valid (direct match or via identifiers), or
    # - An alternative ticker matches and the 'ticker' is valid
    masks['any_match'] = masks['valid_ticker'] | (masks['alt_ticker_match'] & masks['valid_ticker'])

    # Prepare the DataFrame of matching rows
    matching_rows = df_codes[masks['any_match']].copy()

    # Reindex masks to align with matching_rows
    matching_masks = masks.loc[matching_rows.index]

    # Generate verbose output if required
    if verbose:
        mappings = []

        # For direct matches
        direct_matches = matching_rows[matching_masks['ticker_match']]
        for ticker in direct_matches['ticker']:
            mappings.append(f"{ticker} -> {ticker} (Direct match)")

        # For alternative ticker matches where 'ticker' is valid
        alt_matches = matching_rows[~matching_masks['ticker_match'] & matching_masks['alt_ticker_match'] & matching_masks['valid_ticker']]
        for idx, row in alt_matches.iterrows():
            alt_tickers = row[ticker_columns[1:]].dropna()
            matching_alt_tickers = alt_tickers[alt_tickers.isin(classified['tickers'])]
            if not matching_alt_tickers.empty:
                alt_ticker = matching_alt_tickers.iloc[0]
                main_ticker = row['ticker']
                mappings.append(f"{alt_ticker} -> {main_ticker} (Alternative ticker match)")

        # For CUSIP matches
        cusip_matches = matching_rows[~matching_masks['ticker_match'] & ~matching_masks['alt_ticker_match'] & matching_masks['cusip_match']]
        for idx, row in cusip_matches.iterrows():
            cusips = row[cusip_columns].dropna()
            matching_cusips = cusips[cusips.isin(classified['cusips'])]
            if not matching_cusips.empty:
                cusip = matching_cusips.iloc[0]
                mappings.append(f"{cusip} -> {row['ticker']} (CUSIP match)")

        # For CIK matches
        cik_matches = matching_rows[~matching_masks['ticker_match'] & ~matching_masks['alt_ticker_match'] & ~matching_masks['cusip_match'] & matching_masks['cik_match']]
        for idx, row in cik_matches.iterrows():
            mappings.append(f"{row['cik']} -> {row['ticker']} (CIK match)")

        # For OpenFIGI matches
        openfigi_matches = matching_rows[~matching_masks['ticker_match'] & ~matching_masks['alt_ticker_match'] & ~matching_masks['cusip_match'] & ~matching_masks['cik_match'] & matching_masks['openfigi_match']]
        for idx, row in openfigi_matches.iterrows():
            mappings.append(f"{row['top_level_openfigi_id']} -> {row['ticker']} (OpenFIGI match)")

        # Print all mappings
        print("\n".join(mappings))

    # Get the unique tickers from the 'ticker' column
    result = matching_rows['ticker'].unique().tolist()

    return result


def ticker_mapper(params, verbose=False):
    # Extract the tickers parameter after mapping synonyms
    tickers = params.get('tickers')
    
    if verbose:
        print(f"Original tickers: {tickers}")

    # Load df_codes (tickers_meta)
    df_codes = pd.read_parquet("data/codes.parq")

    # If tickers is a string, split it into a list
    if isinstance(tickers, str):
        tickers_list = [ticker.strip() for ticker in tickers.split(',')]
    elif isinstance(tickers, list):
        tickers_list = tickers
    else:
        raise ValueError(f"Unexpected type for tickers: {type(tickers)}")

    if verbose:
        print(f"Tickers list: {tickers_list}")

    # Map tickers using find_tickers
    mapped_tickers = find_tickers(tickers_list, df_codes, verbose=verbose)

    if verbose:
        print(f"Mapped tickers: {mapped_tickers}")

    # Convert mapped_tickers back to a comma-separated string
    tickers_string = ','.join(mapped_tickers)

    # Update tickers with mapped_tickers string
    params['tickers'] = tickers_string

    if verbose:
        print(f"Final tickers string: {tickers_string}")

    return params

def data(
    endpoint: str,
    tickers: Union[str, list] = None,
    chart: str = None,
    columns: str = None,
    version: str = None,
    start_date: str = None,
    end_date: str = None,
    # predict: bool = False,
    plot: bool = False,
    limit: int = None,
    params: dict = None,
    body: dict = None,
    use_polars: bool = False,
    purge_cache: bool = False,
    parquet: bool = True,
    frequency: str = None,
    verbose: bool = False,
    full_history: bool = False,
    # **kwargs,                  ## kwargs if you want to allow for random
) -> Union[pd.DataFrame, 'CustomDataFrame']:
    verbose_mode.toggle_verbose(verbose)

    params = params or {}
    params = map_synonyms(params)

    if start_date is not None or end_date is not None:
        full_history = True

    params.update(
        _prepare_params(
            tickers=params.get("tickers", tickers),
            chart=params.get("chart", chart),
            version=params.get("version", version),
            from_date=params.get("start_date", start_date),
            to_date=params.get("end_date", end_date),
            limit=params.get("limit", limit),
            # predict=params.get('predict', predict),
            columns=params.get("columns", columns),
            parquet=params.get("parquet", parquet),
            frequency=params.get("frequency", frequency),
            full_history=params.get("full_history", full_history),

        )
    )
    endpoint, params = _prepare_endpoint(endpoint, params)
    # print(endpoint)
    verbose_mode.vprint(endpoint)
    params = params or None
    headers = {"Authorization": f"Bearer {ApiConfig.token}"}
    url = ApiConfig.base_url + endpoint

    verbose_mode.vprint(f"Requesting URL: {url} with params: {params}")

    # Create a unique cache key
    cache_key = hashlib.sha256(
        json.dumps([url, params], sort_keys=True).encode()
    ).hexdigest()

    # Check if the result is already in the cache
    # Purge cache if requested
    if purge_cache and cache_key in _query_cache:
        del _query_cache[cache_key]
        verbose_mode.vprint("Cache entry purged.")

    # Check if the result is already in the cache
    if not purge_cache and cache_key in _query_cache:
        verbose_mode.vprint("Returning cached data")
        return _query_cache[cache_key]

    # print(endpoint)
    # print(client_side_endpoints)
    # print(tickers)
    # print(frequency)

    normalized_endpoint = normalize_endpoint(endpoint)

    # ACTAULLY I DON'T CARE, TICKERS CAN BE NONE FOR PATENTS

    # Iterate through the handlers to find a matching handler
    for endpoint_set, handler_func, message in handlers:
        if (
            normalized_endpoint in endpoint_set and
            (tickers is not None or start_date is not None) and
            frequency is None
        ):
            verbose_mode.vprint(message)
            _query_cache[cache_key] = handler_func(
                normalized_endpoint, tickers, columns, start_date, end_date
            )
            return _query_cache[cache_key]


    try:
        if tickers is not None and not is_all(tickers):
            params = ticker_mapper(params,verbose)


        res = requests.get(
            url=url,
            headers=headers,
            data=body,
            params=params,
            stream=True,
            verify=ApiConfig.verify_ssl,
        )
        
        verbose_mode.vprint(f"Response Status: {res.status_code}")
        verbose_mode.vprint(f"Response Content-Type: {res.headers.get('content-type')}")

        print_tickers_value(tickers)

        verbose_mode.vprint(params)

        tickers = get_ticker_from_endpoint(endpoint, tickers, endpoint_to_ticker)

        print_tickers_value(tickers)
  

        res.raise_for_status()

        data_format = res.headers.get("X-Data-Format")
        content_type = res.headers["content-type"]

        plot_header = res.headers.get("X-Plotly-Data")
        # print(data_format)
        # print(plot_header)

        # print(content_type)

        if (content_type == "application/octet-stream") and not plot_header:
            if data_format == "pyarrow":
                verbose_mode.vprint(f"header: {data_format}")
                data = stream_data_pyarrow(res)
            else:
                verbose_mode.vprint(f"header: not pyarrow")
                data = stream_data(res)
            
            if HAS_FULL_INSTALL:
                data = CustomDataFrame(data)
            else:
                data = pd.DataFrame(data)
            
            _query_cache[cache_key] = data
            return data
 
        # Example usage in your existing code:
        if is_all(tickers):
            verbose_mode.vprint("All ticker Initialized")
            urls = [u.strip() for u in res.text.strip('"').split(',') if u.strip()]
            data = None
            for i, url in enumerate(urls):
                verbose_mode.vprint(f"Attempting URL {i+1}: {url} (download link)")
                try:
                    data = read_parquet(url, use_polars=use_polars)
                    verbose_mode.vprint(f"Successfully downloaded data from URL {i+1}")
                    break
                except Exception as e:
                    verbose_mode.vprint(f"Failed to download from URL {i+1}: {str(e)}")
            
            if data is None:
                raise Exception("Failed to download data from all provided URLs")
            
            # Apply filters
            data = filter_data(data, columns=columns, start_date=start_date, end_date=end_date, use_polars=use_polars)

            # Wrap the result with CustomDataFrame if HAS_FULL_INSTALL is True
            if HAS_FULL_INSTALL and not use_polars:
                data = CustomDataFrame(data)

            verbose_mode.vprint("It reached the DF")

            _query_cache[cache_key] = data

            verbose_mode.vprint("It passed the DF")

        elif not plot_header:
            if HAS_FULL_INSTALL:
                data = CustomDataFrame(convert_data2df(res.json()))
            else:
                data = pd.DataFrame(convert_data2df(res.json()))

            _query_cache[cache_key] = data

            verbose_mode.vprint("It passed the DF")

        import pickle
        from plotly.graph_objs import Figure
        def set_dark_mode(fig: Figure):
            return fig.update_layout(
                template="plotly_dark",
                plot_bgcolor="rgba(10, 10, 10, 1)",
                paper_bgcolor="rgba(10, 10, 10, 1)",
            )

        if plot_header:
            # print(res.content[:100])
            if HAS_FULL_INSTALL:
                # Decompress the data
                pickle_bytes = res.content
                # Unpickle the data
                fig = pickle.loads(pickle_bytes)
                fig = go.Figure(json.loads(fig))
                fig = set_dark_mode(fig)

                return fig
            else:
                print("Plotting is only available with the full installation. Please install 'sovai[full]' to use this feature.")
            return None
        
        if plot:
            if HAS_FULL_INSTALL:
                return _draw_graphs(data)
            else:
                print("Plotting is only available with the full installation. Please install 'sovai[full]' to use this feature.")
            return None
        return data
    except Exception as err:
        verbose_mode.vprint("An error occurred, check dictionaries for 'data/name':'None':", err)
        return data
        if res.status_code == 404:
            msg = res.json()
            msg.update({"status_code": 404, "error": err.args[0]})
            raise InvalidInputData(str(msg))
    return None


def _prepare_params(**kwargs):
    finish_params = {}

    if isinstance(kwargs["tickers"], list):
        kwargs["tickers"] = ",".join(kwargs["tickers"])

    if isinstance(kwargs["columns"], list):
        kwargs["columns"] = ",".join(kwargs["columns"])

    for server_param, client_param in kwargs.items():
        if client_param is not None:
            finish_params[server_param] = str(client_param)

    return finish_params


def _prepare_endpoint(endpoint: str, params: dict) -> Tuple[str, dict]:
    if not endpoint.startswith("/"):
        endpoint = "/" + endpoint
    endpoint_params_key = re.findall(r"\{(.*?)\}", endpoint)
    endpoint_params = {
        key: value for key, value in params.items() if key in endpoint_params_key
    }
    other_params = {
        key: value for key, value in params.items() if key not in endpoint_params_key
    }
    _uniform_datetime_params(other_params)
    if endpoint_params:
        endpoint = endpoint.format(**endpoint_params)
    return endpoint.lower(), other_params


def _uniform_datetime_params(datetime_params: dict[str, str]):
    for key, val in datetime_params.items():
        if "date" in key.lower():
            for _format in datetime_format:
                try:
                    origin_datetime = datetime.strptime(val, _format)
                    datetime_params[key] = origin_datetime.strftime(datetime_format[0])
                    break
                except ValueError:
                    continue
        else:
            datetime_params[key] = val


def _draw_graphs(data: Union[Dict, List[Dict]]):
    if isinstance(data, list):
        for plot in data:
            for _, val in plot.items():
                return plotting_data(val)
    else:
        for _, val in data.items():
            return plotting_data(val)
