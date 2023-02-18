import pandas as pd
import datetime
import re
from dash import Dash
import tabloo

import globals
from symbol import Symbol
from market_watch import MarketWatch
import market_model
from market_model import Market
import market_view
from chart import SymbolChart
from dftable import DataFrameTable
from market_control import MarketControl

class SymbolWatch(MarketControl):
    def __init__(self,symbol_name, by='', tf ='D',offset = -1, date='', watch_name = ''):
        super().__init__( by=by, tf =tf,offset = offset, date=date)
        self._symbol_name = symbol_name
        self._symbol = Symbol(symbol_name, read_csv=True)
        self._watch_name = 'SYMBOL_WATCH' if watch_name == '' else watch_name
     
        # ---------- new view, model ------------
        self._watch = MarketControl.watches[self._watch_name] 
        self._view = self._watch.view()
        self._model = self._watch.model(self._symbol, self._by, self._tf,self._offset, self._date)
        # ---------- set tablo , tabloview ------------
        self._tablo = self._model.tablo
        self._tabloview = self._view._map_columns(self._tablo)

    def show_charts(self, all_tf_charts = True, vol_indicators = True):
        if self._symbol is None:
            print('Could not show symbol')
            return

        if vol_indicators:
            SymbolChart(symbol=self._symbol, last_n=200, future_n=26).fig_indicators_for_mode(mode='v', mode_l='v', mode_h='v',mode_o='v').show()
        if all_tf_charts:
            SymbolChart.show_all_tf_charts(symbol=self._symbol, last_n=56, future_n=26,indicators=True,volumes=True,buys=True)
        return self
            
    def export_charts(self, all_charts= False):
        candle_n = 150 if self._tf == 'D' else 100
        SymbolChart.export_charts(symbol=self._symbol, tf=self._tf, last_n=candle_n, future_n=26,indicators=all_charts, volumes=all_charts,buys=False)
        return self        
    
#--------------------- main ------------------------
if __name__ == "__main__":
    TIMEFRAME = 'D'
    symbol_name = 'خودکفا'
    by='daily'
    
    sw = SymbolWatch(symbol_name=symbol_name,by=by,tf=TIMEFRAME)
    sw.show_charts()
    sw.show_tablo()

    