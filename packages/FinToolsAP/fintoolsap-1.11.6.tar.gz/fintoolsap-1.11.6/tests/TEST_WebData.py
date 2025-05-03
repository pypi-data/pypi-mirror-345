import os
import sys
import time
import numpy
import pandas
import pathlib
import datetime
import functools

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

# standard plotting options
import matplotlib
import matplotlib.pyplot as plt

# Define a new list of colors
COLORS = ['#002676', '#FDB515', '#C0362C', '#FFFFFF', '#010133',
          '#FC9313', '#00553A', '#770747', '#431170', '#004AAE',
          '#FFC31B', '#018943', '#E7115E', '#8236C7', '#9FD1FF',
          '#FFE88D', '#B3E59A', '#FFCFE5', '#D9CEFF', '#000000',
          '#808080', '#F2F2F2', '#C09748']

plt.rcParams['axes.grid'] = True
plt.rcParams['lines.linewidth'] = 1.5
plt.rcParams['legend.frameon'] = 'True'
matplotlib.rcParams['text.usetex'] = True
plt.rcParams['axes.facecolor'] = '#f0f0f0'
plt.rcParams['patch.force_edgecolor'] = True
plt.rcParams['axes.prop_cycle'] = plt.cycler(color = COLORS)

class Colors:
     BLUE = '#002676'
     YELLOW = '#FDB515'
     RED = '#C0362C'
     WHITE = '#FFFFFF'
     BLACK = '#000000'


def main():
    
    WD = WebData.WebData('andrewperry')
    
    df = WD.getData(tickers=['AAPL', 'MSFT', 'F', 'GE'], freq = 'D')
    
    df = df.set_index('date')
    
    f, a = plt.subplots(2, 2, figsize=(12, 8), tight_layout=True)
    df[df.ticker == 'AAPL'].pps.plot(ax=a[0, 0])
    a[0, 0].set_title('AAPL')
    df[df.ticker == 'MSFT'].pps.plot(ax=a[0, 1])
    a[0, 1].set_title('MSFT')
    df[df.ticker == 'F'].pps.plot(ax=a[1, 0])
    a[1, 0].set_title('F')
    df[df.ticker == 'GE'].pps.plot(ax=a[1, 1])
    a[1, 1].set_title('GE')

    plt.show()
        
    
    



if __name__ == '__main__':
    main()