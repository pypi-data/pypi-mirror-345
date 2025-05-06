from .services.data_downloader import DataDownloader
from .services.data_preprocesser import DataPreprocesser
from .pv import PV
from datetime import datetime
from typing import List
from tqdm import tqdm
import pandas as pd
import warnings

class ArchiverClient:
    """
    Client interface for downloading and processing EPICS Archiver data.

    This class handles communication with the EPICS archiver server and provides
    cleaned, timestamp-aligned data as `PV` objects or pandas DataFrames.
    """
    def __init__(self, archiver_url: str):
        """
        Initialize the ArchiverClient.

        Parameters:
        - archiver_url (str): Base URL of the EPICS archiver server.
        """
        self.__data_downloader = DataDownloader(archiver_url=archiver_url)
        self.__data_preprocesser = DataPreprocesser()

    def download_data(self, pv_name: str,
                            precision: int,
                            start: datetime, 
                            end: datetime,
                            verbose: bool = False) -> PV:
        """
        Download and clean data for a single PV from the archiver.

        Parameters:
        - pv_name (str): Name of the Process Variable (PV).
        - precision (int): Temporal resolution in milliseconds.
        - start (datetime): Start time of the query (in PST).
        - end (datetime): End time of the query (in PST).
        - verbose (bool): If True, print archiver responses and progress.

        Returns:
        - PV: A PV object containing raw and cleaned data, metadata, and timestamps.
        """
        pv: PV =  self.__data_downloader.download_data(
            pv_name, start, end, verbose
        )
        pv = self.__data_preprocesser.clean_data(pv, precision)
        return pv
    
    def __match_data(self, pv_list: List[PV], 
                           precision: int,
                           verbose: bool = True) -> pd.DataFrame:
        """
        Align and merge data from multiple PV objects based on timestamps.

        Parameters:
        - pv_list (List[PV]): List of PV objects to match.
        - precision (int): Temporal resolution in milliseconds.
        - verbose (bool): If True, show progress during matching.

        Returns:
        - pd.DataFrame: Matched and aligned data with columns: [secs, nanos, PV1, PV2, ...]
        """
        return self.__data_preprocesser.match_data(pv_list, precision, verbose)

    def match_data(self, pv_list: List[str], # type: ignore
                         precision: int,
                         start: datetime, 
                         end: datetime, 
                         verbose: int = 0) -> pd.DataFrame:
        """
        Download and align data for multiple PVs based on timestamps.

        Parameters:
        - pv_list (List[str]): List of PV names as strings.
        - precision (int): Temporal resolution in milliseconds.
        - start (datetime): Start time of the query (in PST).
        - end (datetime): End time of the query (in PST).
        - verbose (int): Verbosity level:
            - 0: Silent
            - 1: Show only matching progress
            - 2: Show download and matching progress

        Returns:
        - pd.DataFrame: Matched data with timestamps and PV columns.
        """
        assert all(filter(lambda x: isinstance(x, str), pv_list)), 'please use only lists of strings.'
        verbose_download = verbose == 2
        verbose_match = verbose > 0
        pv_list_obj: List[PV] = []
        pbar = tqdm(pv_list)
        for pv in pbar:
            pbar.set_description(f"Downloading PV {pv}")
            try:
                pv = self.download_data(pv, precision, start, end, verbose_download)
                pv_list_obj.append(pv) # type: ignore
            except:
                warnings.warn(f'An error occurred while fetching {pv} data. PV skipped.')
        return self.__match_data(pv_list_obj, precision, verbose_match) # type: ignore