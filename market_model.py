import datetime
import re
import sys
from symbol import Symbol, SymbolsBaseInfo, SymbolsDic

import jdatetime
import numpy as np
import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objects as go
import pytse_client as tse
import tabloo
from dash import Dash
from jdatetime import jalali
from pytse_client import (Ticker, config, download_client_types_records,
                          symbols_data, tse_settings)

import globals
import indicator
import symbol_repository as rep
import trendline
from chart import SymbolChart
from dftable import DataFrameTable
from indicator import *


#-----------------------------------------------------------------------------------------------#
#-------------------------------------- Market class    ----------------------------------------#
#-----------------------------------------------------------------------------------------------#
class Market:
    @property
    def tablo(self):
        return self._tablo

    @property
    def daily_trades(self):
        return self._daily_trades

    on_time = datetime.time(8,45)
    off_time = datetime.time(12,35)
    close_days = [3,4]

    @staticmethod
    def is_open():
        timenow = datetime.datetime.now().time()
        weekday = datetime.datetime.today().weekday()
        return (Market.on_time <= timenow < Market.off_time) and (weekday not in Market.close_days)
    
    #------------------------------------------ load __init__ --------------------------------------#
    def __init__(self, by='', tf ='D',offset = -1, date = ''):
        self._by = ('realtime' if Market.is_open() else 'daily') if by == '' else by
        self._offset = offset
        self._date = datetime.datetime.now().strftime('%Y%self%d') if date == '' else date
        self._tf = tf

        # ---------------- load baseinfo ------------------
        self._base_info =  Symbol.load_base_info(date=self._date)
        # print(self._base_info)
        
        # ---------------- load shareholders ------------------
        self._shareholders = rep.load_shareholders_activities()
        date_shareholders = self._shareholders[self._shareholders['date'] == self._date]
        self._shareholders = self._get_recent_df(df=self._shareholders,column='date') if date_shareholders.empty else date_shareholders
        self._shareholders_changes = self._shareholders.groupby(by='symbol').sum('changed_shares')
        
        # ---------------- load market_watch or realtime and make watch ------------------
        self.init_daily_trades()
        self._tablo = self._daily_trades

    def init_daily_trades(self):
        if self._by == 'market_watch':
            self._daily_trades = rep.load_market_watch(date=self._date)
        elif self._by in ['realtime', 'daily']:
            self._daily_trades = rep.load_realtime_demands(date=self._date)
        return self._daily_trades

    def _get_recent_df(self, df, column='time'):
        if df is None : return None
        return df.loc[df[column] == df.iloc[-1][column]]

    def refresh(self):
        self.init_daily_trades()
        self._tablo = self._daily_trades
        return self._tablo

    #------------------------------------------ add columns ----------------------------------------#
    def add_regular_columns(self, df):
        df['close_percent'] = indicator.tableau.TABLEAU.close_growth(df=df)
        df['adjClose_percent'] = indicator.tableau.TABLEAU.close_growth(df=df)
        df['vol_1to30'] = df['volume']/ df['vol_month']
        df['growth_month_min'] = indicator.tableau.TABLEAU.monthmin_price_growth(df=df)
        df['ind_buyers_power'] =indicator.tableau.TABLEAU.ind_buyers_power(df=df)
        df['ind_ownership_change'] = indicator.tableau.TABLEAU.ind_ownership_change(df=df)
        
    def add_price_columns(self, df):
        df['asc_tick'] = pd.Series(indicator.tableau.TABLEAU.ascending_tick(df=df) )
        df['close_percent'] = indicator.tableau.TABLEAU.close_growth(df=df)
        df['adjClose_percent'] = indicator.tableau.TABLEAU.adjclose_growth(df=df)
        df['growth_month_min'] = indicator.tableau.TABLEAU.monthmin_price_growth(df=df)
        df['growth_week'] = trendline.growth_ratio(df['close'], df['low_week'])
        df['growth_year'] = trendline.growth_ratio(df['close'], df['low_year'])
        try:
            df['tmin'] = df['tmin'].astype('int')
        except :
            pass
        try:
            df['tmax'] = df['tmax'].astype('int')
        except :
            pass

    def add_volume_columns(self, df):
        df['vol_percent'] = pd.Series(indicator.tableau.TABLEAU.vol_percent(df=df,total_shares= df['total_shares']) )
        # df['vol_1to30'] = indicator.tableau.TABLEAU.vol_1to30(df=df)
        df['vol_1to30'] = df['volume']/ df['vol_month']
        df['vol_to_basevol'] = df['volume']/ df['base_vol']
        df['ind_ownership_change'] = indicator.tableau.TABLEAU.ind_ownership_change(df=df)

    def add_value_columns(self, df):
        df['market_value'] = df['adjClose'] * df['total_shares']

    def add_power_columns(self, df):
        df['ind_buyers_power'] =indicator.tableau.TABLEAU.ind_buyers_power(df=df)
        df['ind_buy_capita'] =indicator.tableau.TABLEAU.ind_buy_capita(df=df)
        df['ind_sell_capita'] =indicator.tableau.TABLEAU.ind_sell_capita(df=df)
        df['corp_buy_capita'] =indicator.tableau.TABLEAU.corp_buy_capita(df=df)
        df['corp_sell_capita'] =indicator.tableau.TABLEAU.corp_sell_capita(df=df)

    def add_queue_column(self, df):
        seen_max_price = df['high'] ==  df['tmax'] # df['demand_count_1'] >0
        seen_min_price = df['low'] ==  df['tmin'] # df['offer_count_1'] >0

        queue = pd.Series(['-'] * len(df['symbol']))
        buy_queue_cond = (df['demand_price_1']  == df['tmax']) & (df['demand_volume_1']!=0)
        sell_queue_cond = (df['offer_price_1']  == df['tmin']) & (df['offer_volume_1']!=0)
        queue[buy_queue_cond] = 'صف خرید'
        queue[sell_queue_cond] = 'صف فروش'

        queue_val = pd.Series([0] * len(df['symbol']))
        queue_val[buy_queue_cond] = df['demand_volume_1'] * df['demand_price_1']
        queue_val[sell_queue_cond] = df['offer_volume_1'] * df['offer_price_1'] * -1

        df['queue'] = queue
        df['queue_val'] = queue_val
        # close_to_buy_queue = (po1)<= (tmax) && (po1)>= (tmax)-1 && (pd1)<(tmax);   
        # gathering_sell_queue = (tvol)>(bvol) && (pmin)== (tmin) && ((pl)-(pc))/(pl)*100>1.5 && (ct).Sell_CountI >= (ct).Buy_CountI && (tno)>5 && (tno)>20 ;
        # dumping_buy_queue = (tvol)>(bvol) && seenMaxPrice && stochOverBought && (downTrend7 || downTrend8) && DaysRatio(1,30) > 1;
        return df

#-----------------------------------------------------------------------------------------------#
#-------------------------------------- Market Model classes  ---------------------------------#
#-----------------------------------------------------------------------------------------------#
class MarketModel(Market):
   
    @property
    def symbol_names(self):
        return self._symbol_names
    
    # @property
    # def tabloview(self):
    #     return self._tabloview

    @staticmethod
    def get_symbol_list(df):
        if (df is None) or ('symlink' not in df): 
            return None
        return list(df['symlink'])

    @staticmethod
    def get_tf(df):
        if (df is None) or ('tf' not in df): 
            return None
        return df.iloc[0]['tf']

    #------------------------------------------ load __init__ --------------------------------------#
    @staticmethod
    def filter_symbols_df(df: pd.DataFrame, in_groups=[], except_groups=[],in_markets=[],except_markets=[]):       
        try:
            if in_markets:
                df = df.loc[df['market'].isin(in_markets) ]
            if except_markets:
                df = df.loc[~df['market'].isin(except_markets) ]
            if in_groups:
                df = df.loc[df['sector_code'].isin(in_groups) ]
            if except_groups:
                df = df.loc[~df['sector_code'].isin(except_groups) ]

            return df

        except:
            return None

    def filter_symbols(self, symbol_names= [], date='', in_groups=[], except_groups=[],in_markets=[],except_markets=[]):
        if (not symbol_names):
                symbol_names = sorted(list(symbols_data.all_symbols()))
        self._base_info = self._base_info [self._base_info['symbol'].isin(symbol_names)]
        self._base_info = MarketModel.filter_symbols_df(self._base_info)
       
        return list(self._base_info['symbol']) if self._base_info is not None else None

    def __init__(self, symbol_names = [], by='', tf ='D',offset = -1, date = '', in_groups=[], except_groups=[59,68,69],in_markets=[],except_markets=[]):
        super().__init__(by=by, tf = tf,offset=offset, date=date)
        self._in_groups = in_groups
        self._except_groups = except_groups
        self._in_markets = in_markets
        self._except_markets = except_markets

        self._orig_symbol_names = symbol_names
        # ---------------- filter symbols   ------------------
        self._symbol_names = self.filter_symbols(symbol_names=self._orig_symbol_names, date=self._date, in_groups=self._in_groups, except_groups=self._except_groups,in_markets=self._in_markets,except_markets=self._except_markets)
        # ---------------- load symbols and make tablo ------------------
        self.init_tablo()
        self.add_computational_columns(df=self._tablo)
        self.init_symbol_intraday_trades()

    def init_symbol_intraday_trades(self):
        df=self._tablo
        symbol_list = MarketModel.get_symbol_list(df)
        tf= MarketModel.get_tf(df)
        if symbol_list is None or tf is None: return df
        for symbol in symbol_list:
            symbol.init_intraday_trades(self._daily_trades)
        return self._daily_trades
  
    def __call__(self):
        self.init_daily_trades()
        self.init_tablo()
        return self

    def init_tablo(self):
        # ---------------- load global symbols  ------------------  
        Symbol.load_symbols_ohlc_daily(symbol_names=self._symbol_names)
        # ---------------- make tablo ------------------
        if self._by == 'daily':
            # ---------------- make watch and tablo by loading symbols ohlc data by date or line ------------------
            self._tablo = MarketModel.symbol_date_to_df(symbol_list=list(SymbolsDic.values()),date=self._date,tf=self._tf)
            # if self._tablo.empty: self._tablo = Market.symbol_line_to_df(symbol_list=list(SymbolsDic.values()),tf=self._tf)
            # ---------------- merge daily trades ------------------
            recent_daily_trades = self._get_recent_df(df=self._daily_trades, column='fetch_time')[["symbol","time", "demand_price_1","demand_volume_1","demand_count_1","offer_price_1","offer_volume_1","offer_count_1"]]
            self._tablo = pd.merge(self._tablo , recent_daily_trades, how='left', on='symbol')
        else:
            if self._by == 'market_watch':
                self._tablo = self._get_recent_df(df=self._daily_trades, column='time')
            elif self._by == 'realtime':
                self._tablo = self._get_recent_df(df=self._daily_trades, column='fetch_time')
            self._tablo = self._tablo[self._tablo['symbol'].isin(self._symbol_names)]
        
        # ---------------- merge baseinfo ------------------
        self._tablo = pd.merge(self._tablo , self._base_info, how='left', on='symbol')
        # ---------------- merge shareholders stoch change ------------------
        self._tablo = pd.merge(self._tablo, self._shareholders_changes, how='left', on='symbol' )
        # ---------------- add timeframe and symbol object link ------------------        
        self._tablo['no'] = [i for i in range(len(self._tablo))]    
        self._tablo['symlink'] = [SymbolsDic[symbolname] for symbolname in self._tablo['symbol']]
        self._tablo['tf'] = pd.Series([self._tf]* len(self._tablo))

        # ---------------- copy result as tablo  ------------------  
        return self._tablo  

    @staticmethod
    def symbol_line_to_df(symbol_list,offset=-1, tf='D'):
        convert_result = []
        for symbol in symbol_list: 
            row = symbol.get_row(offset, tf)
            if row is not None: 
                row = row.copy()
                convert_result.append(row)
        return pd.DataFrame(convert_result) if len(convert_result) > 0 else None

    @staticmethod
    def symbol_date_to_df(symbol_list,date=None, tf='D'):
        convert_result = []
        for symbol in symbol_list: 
            row = symbol.get_row_bydate(date=date, tf=tf)
            if row is None: row = symbol.get_row(-1, tf)
            if row is not None: 
                row = row.copy()
                convert_result.append(row)
        return pd.DataFrame(convert_result) if len(convert_result) > 0 else None

    @staticmethod
    def add_symbol_column_to_df(df, column_name,offset = -1,tf='D', symbol_list=[], forced_implement= True):
        if (column_name in df.columns) and not forced_implement: return None
        if not symbol_list: 
            if 'symlink' in df.columns: 
                symbol_list = list(df['symlink'])
            else:
                return None
        column_result = []
        for symbol in symbol_list: 
            column_result.append(symbol.candle_value(column_name,offset, tf))

        df[column_name] = column_result
        return column_result 

    @staticmethod
    def add_symbol_columns_to_df(df, column_names=[],offset = -1,tf='D', symbol_list=[], forced_implement= True):
        for column_name in column_names:
            MarketModel.add_symbol_column_to_df(df=df,column_name=column_name,tf=tf)

    def add_computational_columns(self, df):
        return df

    def refresh(self):
        self.init_daily_trades()
        self.init_tablo()
        self.add_computational_columns(self._tablo)
        return self._tablo

    #------------------------------------------ add columns ----------------------------------------#
    def add_ma_column(self, df):
        ema_labels = ['EMA3','EMA5','EMA8','EMA13','EMA21','EMA34','EMA55','EMA89','EMA144','EMA233','EMA377','EMA610','EMA987','EMA1597','EMA2584']
        ema2 = 'EMA2'
        self.ma_crossing(df=df)
        ma_column = []
        for symbol in self.get_symbol_list(df=self._tablo):
            # indicator.ma_crossing.MACROSSING(symbol,mode=mode,func1=func1, n1=n1,func2=func2, n2=n2,label=label,as_standard=as_standard, tf=self._tf).setup_for_conditions()
            ma_result = ""
            for ema in ema_labels[1:]:
                if trendline.is_crossing_above(symbol=symbol,mode1= ema2, mode2=ema ,offset=self._offset, tf = self._tf):
                    ma_result += re.search('\d+$', ema).group() + ','
            ma_column.append(ma_result)
        print(ma_column)
        df['ma_ascending'] = pd.Series(ma_column)
        return df
   
#------------------------------------------- Indicators ----------------------------------------#
    @staticmethod 
    def adx(df, n=14, mode_l='l',mode_h='h',mode='c', label="", as_standard = True, tf ='D'):
        symbol_list = MarketModel.get_symbol_list(df)
        if symbol_list is None or tf is None: return df
        label = indicator.adx.ADX.default_label(label,n,mode,as_standard)
        line_labels = indicator.adx.ADX.default_line_labels(label)
        for symbol in symbol_list:
            indicator.adx.ADX(symbol,n,mode,mode_h, mode_l,label,as_standard, tf=tf).setup_for_conditions()
        MarketModel.add_symbol_columns_to_df(df=df,column_names=line_labels,tf=tf)
        return df
   
    @staticmethod 
    def bb(df, n=200,ndev=2,mode='c',label='', as_standard = True, tf ='D'):
        symbol_list = MarketModel.get_symbol_list(df)
        if symbol_list is None or tf is None: return df
        label = indicator.bolinger.BB.default_label(label,n,ndev,mode,as_standard)
        line_labels = indicator.bolinger.BB.default_line_labels(label)
        for symbol in symbol_list:
            indicator.bolinger.BB(symbol,n=n,ndev=ndev,mode=mode,label=label,as_standard=as_standard, tf=tf).setup_for_conditions()
        MarketModel.add_symbol_columns_to_df(df=df,column_names=line_labels,tf=tf)
        return df

    @staticmethod 
    def divergence(df, mode = 'c', divergence_period=26,label='', tf ='D'):
        symbol_list = MarketModel.get_symbol_list(df)
        if symbol_list is None or tf is None: return df
        for symbol in symbol_list:
            indicator.divergence.DIVERGENCE(symbol,mode=mode,divergence_period=divergence_period,tf=tf).setup_for_conditions()
        return df

    @staticmethod 
    def ema(df, n=34,mode='c',label='', as_standard = False, tf ='D'):
        symbol_list = MarketModel.get_symbol_list(df)
        if symbol_list is None or tf is None: return df
        label = indicator.ema.EMA.default_label(label,n,mode,as_standard)
        for symbol in symbol_list:
            indicator.ema.EMA(symbol,n=n,mode=mode,label=label, tf=tf).setup_for_conditions()
        MarketModel.add_symbol_column_to_df(df=df,column_name=label,tf=tf)
        return df

    @staticmethod 
    def ichi(df,ten=9,kij=26,spanb=52, mode_l='l',mode_h='h',mode='c',label='', as_standard = True, tf ='D'):
        symbol_list = MarketModel.get_symbol_list(df)
        if symbol_list is None or tf is None: return df
        label = indicator.ichimoku.ICHI.default_label(label,ten_n=ten,kij_n=kij,spanb_n=spanb,as_standard=as_standard)
        line_labels = indicator.ichimoku.ICHI.default_line_labels(label)
        for symbol in symbol_list:
            indicator.ichimoku.ICHI(symbol,ten_n=ten,kij_n=kij,spanb_n=spanb,mode_l=mode_l,mode_h=mode_h,mode=mode,label=label,as_standard=as_standard, tf=tf).setup_for_conditions()
        MarketModel.add_symbol_columns_to_df(df=df,column_names=line_labels,tf=tf)
        return df

    @staticmethod 
    def rsi(df, n=14, mode = 'c', label='', as_standard = True, tf ='D'):
        symbol_list = MarketModel.get_symbol_list(df)
        if symbol_list is None or tf is None: return df
        label = indicator.rsi.RSI.default_label(label,n,mode,as_standard)
        for symbol in symbol_list:
            indicator.rsi.RSI(symbol,n,mode,label,as_standard, tf=tf).setup_for_conditions()
        MarketModel.add_symbol_column_to_df(df=df,column_name=label,tf=tf)
        return df
   
    @staticmethod 
    def stoch(df, k=18 ,d=5,s=2, mode='c',mode_l='l',mode_h='h', label="", as_standard=True, tf ='D'):
        symbol_list = MarketModel.get_symbol_list(df)
        if symbol_list is None or tf is None: return df
        label = indicator.stoch.STOCH.default_label(label,k,d,s,as_standard)
        line_labels = indicator.stoch.STOCH.default_line_labels(label)
        for symbol in symbol_list:
            indicator.stoch.STOCH(symbol,k_period=k,d_period=d,slowing=s, mode=mode,mode_l=mode_l,mode_h=mode_h, label="", as_standard=as_standard, tf=tf).setup_for_conditions()
        MarketModel.add_symbol_columns_to_df(df=df,column_names=line_labels,tf=tf)
        return df

    @staticmethod 
    def macd(df, slow=26, fast=12, signal=9,  mode='c', label="", as_standard = True, tf ='D'):
        symbol_list = MarketModel.get_symbol_list(df)
        if symbol_list is None or tf is None: return df
        label = indicator.macd.MACD.default_label(label,slow,fast,signal,mode,as_standard)
        line_labels = indicator.macd.MACD.default_line_labels(label)
        for symbol in symbol_list:
            indicator.macd.MACD(symbol,slow_ema=slow,fast_ema=fast,signal_ema=signal, mode=mode, label="", as_standard=as_standard, tf=tf).setup_for_conditions()
        MarketModel.add_symbol_columns_to_df(df=df,column_names=line_labels,tf=tf)
        return df

    @staticmethod 
    def mmid(df, n=18,mode='c', mode_h='h',mode_l='l', label='', as_standard = False, tf ='D'):
        symbol_list = MarketModel.get_symbol_list(df)
        if symbol_list is None or tf is None: return df
        label = indicator.mmid.MMID.default_label(label=label,n=n,mode_h= mode_h,mode_l=mode_l,as_standard= as_standard)
        for symbol in symbol_list:
            indicator.mmid.MMID(symbol,n=n,mode=mode,mode_l=mode_l, mode_h=mode_h, label=label,as_standard=as_standard, tf=tf).setup_for_conditions()
        MarketModel.add_symbol_column_to_df(df=df,column_name=label,tf=tf)
        return df

    @staticmethod 
    def ma_crossing(df, mode='c',func1='ema', n1=10,func2='ema', n2=25,label='', as_standard = True, tf ='D'):
        symbol_list = MarketModel.get_symbol_list(df)
        if symbol_list is None or tf is None: return df
        label = indicator.ma_crossing.MACROSSING.default_label(label,n1,n2,mode,as_standard)
        for symbol in symbol_list:
            indicator.ma_crossing.MACROSSING(symbol,mode=mode,func1=func1, n1=n1,func2=func2, n2=n2,label=label,as_standard=as_standard, tf=tf).setup_for_conditions()
        return df

    @staticmethod 
    def rsi_crossing(df,n1=10,n2=25, mode='c',label='', as_standard = True, tf ='D'):
        symbol_list = MarketModel.get_symbol_list(df)
        if symbol_list is None or tf is None: return df
        label = indicator.rsi_crossing.RSICROSSING.default_label(label,n1,n2,mode,as_standard)
        for symbol in symbol_list:
            indicator.rsi_crossing.RSICROSSING(symbol,n1=n1,n2=n2,mode=mode,label=label,as_standard=as_standard, tf=tf).setup_for_conditions()
        return df

    @staticmethod 
    def sma(df, n=18,mode='c',label='', as_standard = False, tf ='D'):
        symbol_list = MarketModel.get_symbol_list(df)
        if symbol_list is None or tf is None: return df
        label = indicator.sma.SMA.default_label(label,n,mode,as_standard)
        for symbol in symbol_list:
            indicator.sma.SMA(symbol,n=n,mode=mode,label=label, tf=tf).setup_for_conditions()
        MarketModel.add_symbol_column_to_df(df=df,column_name=label,tf=tf)
        return df

    @staticmethod 
    def tableau(df, label='', as_standard = True, tf ='D'):
        symbol_list = MarketModel.get_symbol_list(df)
        if symbol_list is None or tf is None: return df
        label = indicator.tableau.TABLEAU.default_label(label,as_standard)
        line_labels = indicator.tableau.TABLEAU.default_line_labels()
        for symbol in symbol_list:
            indicator.tableau.TABLEAU(symbol=symbol,label=label,as_standard=as_standard,tf= tf).setup_for_conditions()
        MarketModel.add_symbol_columns_to_df(df=df,column_names=line_labels,tf=tf)
        indicator.ind.Ind.add_func_column(tablo_df=df,column_name='close_percent',func=indicator.tableau.TABLEAU.close_growth,df=df)
        indicator.ind.Ind.add_func_column(tablo_df=df,column_name='adjclose_percent',func=indicator.tableau.TABLEAU.adjclose_growth,df=df)
        indicator.ind.Ind.add_func_column(tablo_df=df,column_name='vol_1to30',func=indicator.tableau.TABLEAU.vol_1to30,df=df)
        indicator.ind.Ind.add_func_column(tablo_df=df,column_name='growth_month_min',func=indicator.tableau.TABLEAU.monthmin_price_growth,df=df)
        # df['close_percent'] =  indicator.tableau.TABLEAU.close_growth(df=df)
        # df['adjclose_percent'] =  indicator.tableau.TABLEAU.adjclose_growth(df=df)
        # df['vol_1to30'] = indicator.tableau.TABLEAU.vol_1to30(tabloo_df=df)
        # df['growth_month_min'] = indicator.tableau.TABLEAU.monthmin_price_growth(df=df)
        return df

class DefaultModel(MarketModel):
    def __init__(self, symbol_names = [], by='', tf ='D',offset = -1, date = '', in_groups=[], except_groups=[59,68,69],in_markets=[],except_markets=[]):       
         super().__init__(symbol_names=symbol_names, by=by, tf = tf,offset=offset, date=date,in_groups=in_groups, except_groups=except_groups,in_markets=in_markets,except_markets=except_markets)

    def add_computational_columns(self, df):        
        self.add_price_columns(df)
        self.add_volume_columns(df)
        self.add_value_columns(df)
        self.add_power_columns(df)
      
        #--- add queue
        self.add_queue_column(df)
        self.rsi(df=df)

            # hyperlink = '<a href="{link}">{text}</a>'
            # urls =[hyperlink.format(link=globals.SYMBOL_INFO_URL.format(symbols_data.get_ticker_index(symbol)), text='tse') for symbol in mw._tablo['symbol']]
            # urls =[globals.SYMBOL_INFO_URL.format(symbols_data.get_ticker_index(symbol)) for symbol in mw._tablo['symbol']]
            # mw._tablo['urls'] = pd.Series(urls)

        return df

class RegularModel(MarketModel):
    def __init__(self, symbol_names = [], by='', tf ='D',offset = -1, date = '', in_groups=[], except_groups=[59,68,69],in_markets=[],except_markets=[]):       
         super().__init__(symbol_names=symbol_names, by=by, tf = tf,offset=offset, date=date,in_groups=in_groups, except_groups=except_groups,in_markets=in_markets,except_markets=except_markets)

    def add_computational_columns(self, df):
        self.add_regular_columns(df)
        return df

class MAModel(MarketModel):
    def __init__(self, symbol_names = [], by='', tf ='D',offset = -1, date = '', in_groups=[], except_groups=[59,68,69],in_markets=[],except_markets=[]):       
         super().__init__(symbol_names=symbol_names, by=by, tf = tf,offset=offset, date=date,in_groups=in_groups, except_groups=except_groups,in_markets=in_markets,except_markets=except_markets)

    def add_computational_columns(self, df):
        self.add_regular_columns(df)
        self.add_ma_column(df)
        
        return df

#-----------------------------------------------------------------------------------------------#
#-------------------------------------- ُSymbol Model  ------------------------------------------#
#-----------------------------------------------------------------------------------------------#
class SymbolModel(Market):
    def __init__(self, symbol:Symbol, by='', tf ='D',offset = -1, date = ''):       
        super().__init__(by=by, tf = tf,offset=offset,date=date)
        self._symbol = symbol
        self.init_tablo()
        self.add_computational_columns(self._tablo)

    def init_tablo(self):
        symbol = self._symbol
        if self._by == 'daily' :
            symbol_df = symbol.get_df(tf=self._tf)
            # print('symbol df:', len(symbol_df))
            # symbol_df['date'] = pd.to_datetime(symbol_df['date'], format='%Y%m%d', errors='ignore')
            # ---------------- merge daily trades ------------------
            dailytrades = self._daily_trades[self._daily_trades['symbol'] == symbol.get_name()]
            lastdailytrades = self._get_recent_df(df=dailytrades, column='fetch_time')[["symbol","time", "demand_price_1","demand_volume_1","demand_count_1","offer_price_1","offer_volume_1","offer_count_1"]]
            # print('recent watch:', len(recent_watch))
            self._tablo = pd.merge(symbol_df , lastdailytrades, how='left', on='symbol')
            # print('after merge with watch:', len(self._symbol_watch))
        else:
            self._tablo = self._daily_trades[self._daily_trades['symbol'] == symbol.get_name()]
       
        # ---------------- merge baseinfo ------------------
        self._tablo = pd.merge(self._tablo , self._base_info, how='left', on='symbol')
        # ---------------- merge shareholders stoch change ------------------
        self._tablo = pd.merge(self._tablo, self._shareholders_changes, how='left', on='symbol' )
         # ---------------- add timeframe and symbol object link ------------------   
        self._tablo['no'] = [i for i in range(len(self._tablo))]    
        self._tablo['symlink'] = symbol
        self._tablo['tf'] = self._tf
        return self._tablo

    def refresh(self):
        self.init_daily_trades()
        self.init_tablo()
        self.add_computational_columns(self._daily_trades)
        return self._tablo

    def add_computational_columns(self, df):        
        self.add_price_columns(df)
        self.add_volume_columns(df)
        self.add_power_columns(df)
        
        #--- add queue
        self.add_queue_column(df)
            # hyperlink = '<a href="{link}">{text}</a>'
            # urls =[hyperlink.format(link=globals.SYMBOL_INFO_URL.format(symbols_data.get_ticker_index(symbol)), text='tse') for symbol in mw._tablo['symbol']]
            # urls =[globals.SYMBOL_INFO_URL.format(symbols_data.get_ticker_index(symbol)) for symbol in mw._tablo['symbol']]
            # mw._tablo['urls'] = pd.Series(urls)

        return df

  