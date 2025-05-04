from setuptools import setup, find_packages

def read_requirements():
    with open(r"requirements.txt") as f:
        return f.read().splitlines()

setup(
    name="atlas_algo_trading",
    version="1.0.6",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "MetaTrader5==5.0.4424",
        "mplfinance==0.12.9b1",
        "numpy==1.24.2",
        "pandas==2.2.3",                        
        ],
    author="Moises Nava",
    author_email="navam9897@gmail.com",
    description="This module use the Metatatrader5 library to connect with the platform, the functions were adapted to make it easier",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Moises898/AtlasAlgoTrading",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"       
    ],
    python_requires=">=3.9",
)