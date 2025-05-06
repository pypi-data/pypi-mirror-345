# ALS Archiver Tools

A Python library for interacting with EPICS archiver data. This tool allows you to easily download and process data from EPICS archiver servers.

## 📑 Table of Contents

- [⚙️ Installation](#️-installation)
- [🚀 Getting Started](#-getting-started)
- [🤝 Contributing](#-contributing)
- [📝 Citing](#-citing)
- [📄 License](#-license)

## ⚙️ Installation

### Using pip
You can install this package through `pip`:
```bash
pip install als-archiver-tools
```

### From source
If you want to install from source:
```bash
git clone https://github.com/andrea-pollastro/als-archiver-tools.git
cd archivertools
pip install -e .
```

## 🚀 Getting Started

Interactions with the archiver are managed by the `ArchiverClient` class. Let's see some examples.

### 📥 Single PV data downloading
To download the data of a given PV, refer to the `.download_data()` function:

```python
from datetime import datetime
from archivertools import ArchiverClient

# Initialize the client with your archiver server URL
archiver = ArchiverClient(archiver_url="http://your-archiver-url")
data = archiver.download_data(pv_name="your:pv:name", 
                              precision=100,
                              start=datetime(year=2023, month=4, day=25, hour=22), 
                              end=datetime(year=2023, month=4, day=25, hour=23))
print(data.head())
```

The returned `PV` object contains:
```python
pv.name  # PV name (string)
pv.raw_data  # Raw data as pandas.DataFrame
pv.clean_data  # Cleaned data as pandas.DataFrame
pv.properties  # PV properties as pandas.DataFrame
pv.first_timestamp  # First timestamp as datetime
pv.last_timestamp  # Last timestamp as datetime
```

### 🧮 Data matching
For a given `list` of PVs, data can be matched according to their timestamps. The list must be a sequence of `str`.
PVs could have different archiving policies. In order to have a matching on the timestamps, they must follow the same 
archiving policy (this means that all the archiving policies of the listed PVs must be reduced to a common archiving 
policy). The parameter `precision` allows to select the precision of the individual PVs to allow the data matching.

Example:
```python
pv_list = ['PV_NAME_1', 'PV_NAME_2']
matched_data = archiver.match_data(
    pv_list=pv_list,
    precision=100,
    start=datetime(year=2023, month=4, day=25, hour=22),
    end=datetime(year=2023, month=4, day=25, hour=23),
)
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📝 Citing

This package was developed in 2023 during my stay at Berkeley, hosted by the Accelerator Physics Group (ALS, LBNL). It was used throughout the experimental phase that led to the publication [Application of deep learning methods for beam size control during user operation at the Advanced Light Source](https://journals.aps.org/prab/abstract/10.1103/PhysRevAccelBeams.27.074602).

If you use this package in your work, please cite:
```bibtex
@article{hellert2024application,
  title={Application of deep learning methods for beam size control during user operation at the Advanced Light Source},
  author={Hellert, Thorsten and Ford, Tynan and Leemann, Simon C and Nishimura, Hiroshi and Venturini, Marco and Pollastro, Andrea},
  journal={Physical Review Accelerators and Beams},
  volume={27},
  number={7},
  pages={074602},
  year={2024},
  publisher={APS}
}
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
