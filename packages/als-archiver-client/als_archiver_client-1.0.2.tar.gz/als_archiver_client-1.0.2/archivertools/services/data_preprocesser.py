from typing import List
from ..pv import PV
from tqdm import tqdm
import pandas as pd

class DataPreprocesser:
    """
    This class preprocess (raw) data downloaded from the archiver and stored into PV objects.

    Methods (see function's docs for more info):
    - clean_data: it fills raw data with missing values according to their archiving policy. 
    - match_data: it matches data for a given list of PVs.
    """
    SEP = '==================================='
    
    def clean_data(self, pv: PV, precision: int) -> PV:
        """
        This function imputes missing values in the raw_data. Imputed data will be stored ad
        clean_data into the pv object. 
        
        params:
        - pv, PV: pv data
        - precision, int: data rate precision (ms)

        returns:
        - pv, PV: imputed pv.
        """
        pv.clean_data = pv.raw_data.drop(columns=['severity', 'status'])
        pv.clean_data = pv.clean_data.resample(f'{precision}ms').ffill()
        pv.clean_data.index = pv.clean_data.index.strftime('%Y-%m-%d %H:%M:%S.%f') # type: ignore
        pv.clean_data['val'].iloc[0] = pv.clean_data['val'].iloc[1] # first value is always NaN

        return pv
    
    def match_data(self, pv_list: List[PV], precision: int, verbose: bool = False) -> pd.DataFrame:
        """
        This function matches data listed in the list pv_list according to their timestamps.
        Using the precision param, you can define the timestamp precision in ms to upsample/downsample the series.

        params:
        - pv_list, List[PV]: list of PVs.
        - precision, int: data rate precision (ms)
        - strategy, str: reduction strategy. Values admitted: 'highest', 'lowest'.
        - verbose, bool (default, False): verbose

        returns:
        - matched_data, pd.DataFrame: matched data. Columns: [datetime(index), [PVs]]
        """
        pbar = tqdm(pv_list)
        for pv in pbar:
            pbar.set_description(f"Cleaning data PV {pv.name}")
            pv = self.clean_data(pv, precision)
        
        def extract_data(pv: PV) -> pd.DataFrame:
            data: pd.DataFrame = pv.clean_data
            data = data.rename(columns={'val': pv.name})
            return data
        
        # match data on secs and nanos
        matched_data: pd.DataFrame = extract_data(pv_list[0])
        for pv in pv_list[1:]:
            matched_data = matched_data.merge(extract_data(pv), on=['datetime'])
        
        if verbose:
            print(DataPreprocesser.SEP)
            print(f'PV matched: {[pv_name for pv_name in matched_data.columns]}')
            print(f'First timestamp: {matched_data.index[0]}')
            print(f'Last timestamp: {matched_data.index[-1]}')
            print(DataPreprocesser.SEP)

        return matched_data