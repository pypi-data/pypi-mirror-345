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
    Handles downloading raw data and metadata from the Archiver server.

    This class builds the required URLs, sends HTTP requests to the archiver,
    processes the JSON responses, and returns structured data ready for further
    processing or analysis.

    Attributes (private):
        - __ARCHIVER_URL (str): Base URL of the archiver server.
        - __DATA_JSON (str): URL path for retrieving archived PV data in JSON format.
        - __CHANNEL_FINDER (str): URL path for querying PV metadata.
    """
    def __init__(self, archiver_url: str = None):
        """
        Initialize the downloader with a specified archiver URL and test connectivity.

        Parameters:
            archiver_url (str): Full base URL to the Archiver server.
        
        Raises:
            ConnectionError: If the archiver is unreachable via ping.
        """
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
        """Return the base URL of the configured archiver."""
        return self.__ARCHIVER_URL
    
    def __ping_archiver(self) -> bool:
        """
        Test whether the archiver server is reachable via ping.

        Returns:
            bool: True if reachable, False otherwise.
        """
        print(self.__SEP)
        print("Verifying the reachability of the archiver's server...")
        parsed_url = urlparse(self.__ARCHIVER_URL)
        hostname = parsed_url.netloc.split(':')[0]
        exit_status: int = os.system(f"ping -c 1 {hostname}")
        print(self.__SEP)
        return exit_status == 0

    def __http_request(self, url: str) -> List:
        """
        Perform an HTTP GET request to the specified archiver URL.

        Parameters:
            url (str): Fully constructed request URL.

        Returns:
            list: Parsed JSON response.
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
        Download raw PV data for a specified time interval.

        Parameters:
            pv_name (str): Name of the process variable.
            start (datetime): Start of the interval (assumed PST).
            end (datetime): End of the interval (assumed PST).
            verbose (bool): If True, prints additional logs.

        Returns:
            pd.DataFrame: Raw data with 'secs' and 'nanos' columns.
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
        Ensure the data strictly matches the requested time span.

        Parameters:
            df (pd.DataFrame): Raw PV data with 'secs' column.
            start_ts (int): Start time as a POSIX timestamp.
            end_ts (int): End time as a POSIX timestamp.

        Returns:
            pd.DataFrame: DataFrame cropped to the exact interval.
        """
        if start_ts not in df['secs'].values:
            record: pd.DataFrame = df[df['secs'] < start_ts].tail(1)
            record['secs'] = start_ts
            idx: int = int(record.index[0]) + 1
            df = pd.concat([df.iloc[:idx], record, df.iloc[idx:]]).reset_index(drop=True)
        if end_ts not in df['secs'].values:
            record: pd.DataFrame = df[df['secs'] < end_ts].tail(1)
            record['secs'] = end_ts
            idx: int = (record.index[0]) + 1
            df = pd.concat([df.iloc[:idx], record, df.iloc[idx:]]).reset_index(drop=True)
        left_mask: pd.Series = df['secs'] >= start_ts
        right_mask: pd.Series = df['secs'] <= end_ts
        df = df.loc[left_mask & right_mask, :]
        return df

    def __pv_properties(self, pv: str) -> pd.DataFrame:
        """
        Retrieve metadata properties of a PV from the ChannelFinder service.

        Parameters:
            pv (str): Name of the process variable.

        Returns:
            pd.DataFrame: DataFrame containing the PV's properties.

        Raises:
            ValueError: If no metadata is found.
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
        Public method to download and return PV data as a structured object.

        Parameters:
            pv_name (str): Name of the process variable.
            start (datetime): Start time of the interval (assumed PST).
            end (datetime): End time of the interval (assumed PST).
            verbose (bool): If True, prints detailed logs.

        Returns:
            PV: Object containing raw data, metadata, and timestamps.
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
