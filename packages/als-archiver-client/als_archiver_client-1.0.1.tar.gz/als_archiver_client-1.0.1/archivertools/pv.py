from .archiving_policy import ArchivingPolicy
import pandas as pd

class PV:
    """
    Represents a Process Variable (PV) retrieved from an EPICS Archiver.

    Attributes:
        name (str): PV name.
        raw_data (pd.DataFrame): Raw time-series data retrieved from the archiver.
        properties (pd.DataFrame): Metadata returned by the archiver for this PV.
        clean_data (pd.DataFrame): Cleaned and interpolated time-series data.
        first_timestamp (pd.Timestamp): First timestamp in the raw data.
        last_timestamp (pd.Timestamp): Last timestamp in the raw data.
        archiving_policy (ArchivingPolicy): Frequency level of the archived PV.
    
    Notes:
        Only `clean_data` and `archiving_policy` are mutable after initialization.
        Directly modifying these is discouraged unless you're extending the package.
    """
    def __init__(self, name: str, raw_data: pd.DataFrame, properties: pd.DataFrame):
        """
        Initialize a PV instance.

        Parameters:
            name (str): Name of the PV.
            raw_data (pd.DataFrame): Raw time-series data (indexed by timestamp).
            properties (pd.DataFrame): Metadata as returned by the archiver server.
        """
        self.__name: str = name
        self.__raw_data: pd.DataFrame = raw_data
        self.__properties: pd.DataFrame = properties
        self.__clean_data: pd.DataFrame = None # type: ignore
        self.__first_timestamp: pd.Timestamp = raw_data.index[0] # type: ignore
        self.__last_timestamp: pd.Timestamp = raw_data.index[-1] # type: ignore

        def __extract_archiving_policy(pv_properties: pd.DataFrame) -> ArchivingPolicy:
            """
            Determine the ArchivingPolicy from PV properties.

            Parameters:
                pv_properties (pd.DataFrame): The metadata DataFrame from the archiver.

            Returns:
                ArchivingPolicy: Parsed archiving policy.
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