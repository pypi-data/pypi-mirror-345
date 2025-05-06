from .archiving_policy import ArchivingPolicy
import pandas as pd

class PV:
    """
    This class represents the PV entity.
    
    Properties:
    - name, str: pv name.
    - raw_data, pd.DataFrame: raw data downloaded from the archiver.
    - properties, pd.DataFrame: pv properties as reported into the archiver.
    - clean_data, pd.DataFrame: cleaned data (with missing values imputed).
    - first_timestamp: pd.Timestamp: first timestamp of the timespan covered by the data.
    - last_timestamp: pd.Timestamp: last timestamp of the timespan covered by the data.
    - archiving_policy, ArchivingPolicy: archiving policy as reported on the archiver.
    Methods:
    - getter of the attributes
    - setter only of attributes clean_data and archiving_policy. It is suggested to don't
      change this values outside the other classes of the same package.
    """
    def __init__(self, name: str, raw_data: pd.DataFrame, properties: pd.DataFrame):
        self.__name: str = name
        self.__raw_data: pd.DataFrame = raw_data
        self.__properties: pd.DataFrame = properties
        self.__clean_data: pd.DataFrame = None  # type: ignore
        self.__first_timestamp: pd.Timestamp = raw_data.index[0] # type: ignore
        self.__last_timestamp: pd.Timestamp = raw_data.index[-1] # type: ignore

        def __extract_archiving_policy(pv_properties: pd.DataFrame) -> ArchivingPolicy:
            """
            Private function, it returns the archiving policy stored in the pv properties 
            in input as ArchivingPolicy object.

            params:
            - pv_properties, pd.DataFrame:

            returns:
            - archiving_policy, ArchivingPolicy: archiving policy of the pv into the archiver
            """
            ap_str = pv_properties[pv_properties['name'] == 'archive']['value'].values[0]
            ap_str = ap_str.lower().strip().replace('controlled', '')
            ap: ArchivingPolicy = ArchivingPolicy.FAST
            match ap_str:
                case 'veryfast':
                    ap = ArchivingPolicy.VERYFAST
                case 'fast':
                    ap = ArchivingPolicy.FAST
                case 'medium':
                    ap = ArchivingPolicy.MEDIUM
                case 'slow':
                    ap = ArchivingPolicy.SLOW
                case 'veryslow':
                    ap = ArchivingPolicy.VERYSLOW
            return ap
        self.__archiving_policy: ArchivingPolicy = __extract_archiving_policy(properties)

    @property
    def archiving_policy(self) -> ArchivingPolicy:
        return self.__archiving_policy
    
    @archiving_policy.setter
    def archiving_policy(self, archiving_policy) -> None:
        self.__archiving_policy = archiving_policy

    @property
    def first_timestamp(self) -> pd.Timestamp:
        return self.__first_timestamp
    
    @property
    def last_timestamp(self) -> pd.Timestamp:
        return self.__last_timestamp
    
    @property
    def name(self) -> str:
        return self.__name

    @property
    def raw_data(self) -> pd.DataFrame:
        return self.__raw_data
    
    @property
    def properties(self) -> pd.DataFrame:
        return self.__properties
    
    @property
    def clean_data(self) -> pd.DataFrame:
        return self.__clean_data
    
    @clean_data.setter
    def clean_data(self, clean_data: pd.DataFrame) -> None:
        self.__clean_data = clean_data

    def __repr__(self):
        return f'name:{self.name}, first timestamp:{self.first_timestamp}, last timestamp:{self.last_timestamp}, archiving policy:{self.archiving_policy}'