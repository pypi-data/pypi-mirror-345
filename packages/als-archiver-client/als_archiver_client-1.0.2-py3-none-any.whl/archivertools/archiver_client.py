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
    This class manages the interaction between the users and the archiver.

    Properties (private):
    - __data_downloader: DataDownloader object
    - __data_preprocesser: DataPreprocesser object

    Methods (see function's docs for more info):
    - __match_data: it matches data for a given list of PVs.
    - download_data: it downloads data from a URL.
    - match_data: it matches data for a given list of PVs (string or PV objects).
    """
    def __init__(self, archiver_url: str = 'https://controls-web.als.lbl.gov'):
        self.__data_downloader = DataDownloader(archiver_url=archiver_url)
        self.__data_preprocesser = DataPreprocesser()

    def download_data(self, pv_name: str,
                            precision: int,
                            start: datetime, 
                            end: datetime,
                            verbose: bool = False) -> PV:
        """
        This function data downloaded from the archiver.

        params:
        - pv_name, str: pv name.
        - precision, int: data rate precision (ms)
        - start, datetime.datetime: start datetime in PST.
        - end, datetime.datetime: end datetime in PST.
        - verbose, bool (default, False): verbose level.

        returns:
        - pv, PV: pv data as PV object.
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
        Private function for calling match_data on list ov PV objects.

        params:
        - pv_list, List[PV]|List[str]: list of PVs.
        - precision, int: data rate precision (ms)
        - strategy, str: reduction strategy. Values admitted: 'highest', 'lowest'.
        - verbose, bool (default, False): verbose

        returns:
        - matched_data, pd.DataFrame: matched data. Columns: [secs, nanos, [PVs]]
        """
        return self.__data_preprocesser.match_data(pv_list, precision, verbose)

    def match_data(self, pv_list: List[str], # type: ignore
                         precision: int,
                         start: datetime, 
                         end: datetime, 
                         verbose: int = 0) -> pd.DataFrame:
        """
        This function matches PVs defined in pv_list.

        params:
        - pv_list, List[PV]|List[str]: list of PVs.
        - precision, int: data rate precision (ms).
        - start, datetime.datetime: start datetime in PST.
        - end, datetime.datetime: end datetime in PST.
        - verbose, bool (default, True): verbose level, 0 to deactivate, 1 only for merge, 2 for merge and download.

        returns:
        - matched_data, pd.DataFrame: matched data. Columns: [secs, nanos, [PVs]]
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