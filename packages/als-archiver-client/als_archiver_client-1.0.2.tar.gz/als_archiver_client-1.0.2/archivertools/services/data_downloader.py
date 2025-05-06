from ..utils import to_UTC
from urllib3 import PoolManager, disable_warnings
disable_warnings()
from datetime import datetime
from typing import List
from ..pv import PV
import os
import json
import warnings
import numpy as np
import pandas as pd
from urllib.parse import urlparse


class DataDownloader:
    """
    This class manages the download and the interactions with the archiver server.

    Properties (private):
    - ARCHIVER_URL, str: URL to archiver.
    - DATA_JSON, str: URL portion (to combine with ARCHIVER_URL) to download json data.
    - CHANNEL_FINDER, str: URL portion (to combine with ARCHIVER_URL) to download pv properties.
    - URL portion (to combine with ARCHIVER_URL) to download json data.

    Methods (see function's docs for more info):
    - __ping_archiver: it verifies if the archiver is reachable.
    - __http_request: it does http requests to archiver.
    - __download_data: it downloads data from a URL.
    - __filter_data: it filters data in a given timespan.
    - __pv_properties: it downloads the pv properties.
    - download_data: it downloads data from a URL.
    """
    def __init__(self, archiver_url: str = None):
        self.__ARCHIVER_URL = archiver_url
        self.__DATA_JSON: str = '/archappl_retrieve/data/getData.json?'
        self.__CHANNEL_FINDER: str = '/ChannelFinder/resources/channels?'
        self.__SEP = '==================================='

        is_reachable = self.__ping_archiver()
        if is_reachable is False:
            raise ConnectionError("Archiver server is unreachable. Hint: activate the ALS VPN and restart the application.")
        print('Archiver server is reachable via ping.')
    
    @property
    def archiver_url(self) -> str:
        return self.__ARCHIVER_URL
    
    def __ping_archiver(self) -> bool:
        """This function verifies if the archiver's server is reachable via ping. It is called only in the constructor"""
        print(self.__SEP)
        print("Verifying the reachability of the archiver's server...")
        parsed_url = urlparse(self.__ARCHIVER_URL)
        hostname = parsed_url.netloc.split(':')[0]
        exit_status: int = os.system(f"ping -c 1 {hostname}")
        print(self.__SEP)
        return exit_status == 0

    def __http_request(self, url: str) -> List:
        """
        http request to archiver server.

        params:
        - url, str: url built on request type (ask to Tynan for more info).

        returns:
        - json_data, list: data retrieved from http request.
        """
        http: PoolManager = PoolManager(cert_reqs='CERT_NONE')
        response = http.request('GET', url)
        data: bytes = response.data
        json_data: list = json.loads(data)        
        return json_data

    def __download_data(self, pv_name: str, 
                            start: datetime, 
                            end: datetime,
                            verbose: bool = False) -> pd.DataFrame:
        """
        This function returns the raw data from the archiver.

        params:
        - pv_name, str: pv_name name
        - start, datetime.datetime: start datetime in PST.
        - end, datetime.datetime: end datetime in PST.
        - verbose, bool (default, False): verbose level (default, True).

        returns:
        - data, pd.DataFrame: raw data.
        """
        if verbose: print(f"Downloading data from {start} to {end}")
        
        # archiver's http requests want dates in UTC
        start = to_UTC(start, tznaive=True)
        end = to_UTC(end, tznaive=True)

        # building URL
        url_components: list = [
            self.__ARCHIVER_URL,
            self.__DATA_JSON,
            f'pv={pv_name}&',
            f'from={start.isoformat()}Z&'
            f'to={end.isoformat()}Z&',
            'fetchLatestMetadata=true',
        ]
        url: str = "".join(url_components)
        
        # downloading data
        data: dict = self.__http_request(url)[0]

        # organizing data as dictionary
        data_keys: list = list(data['data'][0].keys())
        if 'fields' in data_keys: 
            data_keys.remove('fields')
        df: pd.DataFrame = pd.DataFrame({k: np.array([d[k] for d in data['data']]) for k in data_keys})
                
        return df
    
    def __filter_data(self, df: pd.DataFrame, start_ts: int, end_ts: int) -> pd.DataFrame:
        """
        This function returns the dataframe filtered by a timespan defined by the timestamps in input

        params:
        - df, pd.DataFrame: pv data.
        - start_ts, int: first timestamp.
        - end_ts, int: last timestamp.

        returns:
        - df, pd.DataFrame: filterd df.
        """
        if start_ts not in df['secs'].values:
            record: pd.DataFrame = df[df['secs'] < start_ts].tail(1)
            record['secs'] = start_ts
            idx: int = int(record.index[0]) + 1 # type: ignore
            df = pd.concat([df.iloc[:idx], record, df.iloc[idx:]]).reset_index(drop=True)
        if end_ts not in df['secs'].values:
            record: pd.DataFrame = df[df['secs'] < end_ts].tail(1)
            record['secs'] = end_ts
            idx: int = (record.index[0]) + 1 # type: ignore
            df = pd.concat([df.iloc[:idx], record, df.iloc[idx:]]).reset_index(drop=True)
        left_mask: pd.Series = df['secs'] >= start_ts
        right_mask: pd.Series = df['secs'] <= end_ts
        df = df.loc[left_mask & right_mask, :]
        return df

    def __pv_properties(self, pv: str) -> pd.DataFrame:
        """
        This function returns the properties of the PV in input as pandas DataFrame.

        params:
        - pv, str: PV name.

        returns:
        - properties, pd.DataFrame: dataframe containing properties of the PV.
        """
        url_components: list = [
            self.__ARCHIVER_URL,
            self.__CHANNEL_FINDER,
            f'~name={pv}'
        ]
        url = "".join(url_components)
        properties = self.__http_request(url)
        if len(properties) == 0: raise ValueError(f'PV {pv} not found.')
        if len(properties) == 0: warnings.warn('Multiple PVs retrieved, only the first one will be returned.')

        return pd.DataFrame(properties[0]['properties'])

    def download_data(self, pv_name: str, 
                            start: datetime, 
                            end: datetime,
                            verbose: bool = False) -> PV:
        """
        This function returns raw data downloaded from the archiver.

        params:
        - pv_name, str: pv name.
        - start, datetime.datetime: start datetime in PST.
        - end, datetime.datetime: end datetime in PST.
        - verbose, bool (default, False): verbose level.

        returns:
        - pv, PV: pv data as PV object.
        """
        start_ts: int = int(start.timestamp())
        end_ts: int = int(end.timestamp())
        assert start_ts < end_ts, 'Invalid: start date must be before end date'
        df: pd.DataFrame
        
        if verbose: 
            print(self.__SEP)
            print(f"Downloading data for pv {pv_name}")
        pv_properties = self.__pv_properties(pv_name)

        # Data download
        df = self.__download_data(pv_name, start, end, verbose=verbose)

        # What usually happens when we download data from the archiver for the first time is that 
        # (i) the first timestamp available is always lower than start 
        # (ii) the last timestamp too. 
        # For this reason, we introduce two timestamps having the values of our query equal
        # to the last valid values before. In this way, we can return the exact timespan
        df = self.__filter_data(df, start_ts, end_ts)

        # creating datetime index
        datetime_series = pd.to_datetime(df['secs'] + df['nanos']*1e-9, unit='s', utc=True).dt.tz_convert('US/Pacific')
        df = df.set_index(pd.DatetimeIndex(datetime_series, name='datetime'))
        df = df.drop(columns=['secs', 'nanos'])

        if verbose:
            print(f'First timestamp: {df.index[0]}')
            print(f'Last timestamp: {df.index[-1]}')
            print(self.__SEP)

        # Create PV object
        pv: PV = PV(name=pv_name, raw_data=df, properties=pv_properties)
            
        return pv
