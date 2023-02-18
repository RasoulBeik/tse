import os
import re
import sys
from datetime import datetime, time, timedelta
from symbol import Symbol, SymbolsBaseInfo, SymbolsDic

import jdatetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytse_client as tse
import tabloo
from dash import Dash
from pandas.core.base import PandasObject

import globals
import indicator
import symbol_repository as rep
import trendline
from chart import SymbolChart
from dftable import DataFrameTable
from market import ColumnsMap, Market
import pytse_client as tse
from pytse_client.symbols_data import get_ticker_index
from pytse_client import config, symbols_data, tse_settings, download_client_types_records, Ticker

#--------------------- main ------------------------
if __name__ == "__main__":
    
    mw = Market(by='realtime')
    tablo_df = mw.tablo
    print(mw.tablo)
    tabloo.show(df=tablo_df ,refresh_df=mw.initialize_realtime_tablo)



    
    # hyperlink = '<a href="{link}">{text}</a>'
    # urls =[hyperlink.format(link=globals.SYMBOL_INFO_URL.format(symbols_data.get_ticker_index(symbol)), text='tse') for symbol in mw._tablo['symbol']]
    # urls =[globals.SYMBOL_INFO_URL.format(symbols_data.get_ticker_index(symbol)) for symbol in mw._tablo['symbol']]
    # mw._tablo['urls'] = pd.Series(urls)

    
     

    # close_to_buy_queue = (po1)<= (tmax) && (po1)>= (tmax)-1 && (pd1)<(tmax);   
	# gathering_sell_queue = (tvol)>(bvol) && (pmin)== (tmin) && ((pl)-(pc))/(pl)*100>1.5 && (ct).Sell_CountI >= (ct).Buy_CountI && (tno)>5 && (tno)>20 ;
	# dumping_buy_queue = (tvol)>(bvol) && seenMaxPrice && stochOverBought && (downTrend7 || downTrend8) && DaysRatio(1,30) > 1;
   

