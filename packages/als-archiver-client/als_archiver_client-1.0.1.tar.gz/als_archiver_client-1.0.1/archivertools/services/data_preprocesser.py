from typing import List
from ..pv import PV
from tqdm import tqdm
import pandas as pd

class DataPreprocesser:
    """
    Handles preprocessing of raw PV data retrieved from the Archiver.

    Main responsibilities:
    - Cleaning individual PV data by imputing missing values.
    - Aligning (matching) multiple PVs into a single DataFrame with shared timestamps.
    """
    
    SEP = '==================================='
    
    def clean_data(self, pv: PV, precision: int) -> PV:
        """
        Fill missing values in the raw data of a PV and resample it at a fixed interval.

        The cleaned DataFrame is stored as `clean_data` in the same PV object. Missing
        values are forward-filled, and timestamps are formatted as strings for consistency.

        Parameters:
            pv (PV): The PV object containing raw data.
            precision (int): Sampling resolution in milliseconds (ms).

        Returns:
            PV: The updated PV object with `clean_data` set.
        """
        pv.clean_data = pv.raw_data.drop(columns=['severity', 'status'])
        pv.clean_data = pv.clean_data.resample(f'{precision}ms').ffill()
        pv.clean_data.index = pv.clean_data.index.strftime('%Y-%m-%d %H:%M:%S.%f') # type: ignore
        pv.clean_data['val'].iloc[0] = pv.clean_data['val'].iloc[1] # first value is always NaN

        return pv
    
    def match_data(self, pv_list: List[PV], precision: int, verbose: bool = False) -> pd.DataFrame:
        """
        Align and merge cleaned data from multiple PVs based on a common time index.

        Each PV is cleaned using the specified precision, and then their time-series data
        is merged into a single DataFrame. All PVs must be cleaned before matching.

        Parameters:
            pv_list (List[PV]): A list of PV objects to be aligned.
            precision (int): Resampling interval in milliseconds.
            verbose (bool): If True, print matching information.

        Returns:
            pd.DataFrame: A DataFrame with timestamp index and one column per PV name.
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