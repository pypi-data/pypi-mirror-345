from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="als-archiver-client",
    version="1.0.2",
    author="Andrea Pollastro",
    author_email="apollastro@lbl.gov",
    description="A Python package for interacting with the ALS archiver.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/andrea-pollastro/als-archiver-client",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.26.3",
        "pandas>=2.1.4",
        "python-dateutil>=2.8.2",
        "pytz>=2023.3",
        "six>=1.16.0",
        "tzdata>=2023.3",
        "urllib3>=2.0.0",
        "tqdm>=4.65.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires='>=3.10',
    keywords="epics, archiver, data-mining, engineering, research, particle-accelerator",
)
