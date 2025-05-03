import os
import sys
import time
import numpy
import pandas
import pathlib
import datetime
import functools
import matplotlib.pyplot as plt

# add source directory to path
sys.path.insert(0, '../src/FinToolsAP/')

import WebData
import LaTeXBuilder
import LocalDatabase
import UtilityFunctions

# set printing options
import shutil
pandas.set_option('display.max_rows', None)
pandas.set_option('display.max_columns', None)
pandas.set_option('display.width', shutil.get_terminal_size()[0])
pandas.set_option('display.float_format', lambda x: '%.3f' % x)


def main():
    
    WD = WebData.WebData('andrewperry')
    
    df = WD.getData(tickers=['AAPL', 'MSFT', 'GOOGL'], freq = 'M', start_date = datetime.datetime(2020, 1, 1))
    
    print(df.head())
        
        
    
    



if __name__ == '__main__':
    main()