import pytse_client as tse
from pytse_client import config, symbols_data, tse_settings, download_client_types_records, Ticker
import pandas as pd

import numpy as np
import datetime

from jdatetime import jalali
import jdatetime
import globals
from dash import Dash
from symbol import Symbol, SymbolsDic, SymbolsBaseInfo
from dftable import DataFrameTable
import indicator
from indicator import *

from chart import SymbolChart
import plotly.graph_objects as go
import plotly.figure_factory as ff
import trendline
import sys
import tabloo
import symbol_repository as rep
import re
import market_view
from market_view import MarketView
import market_model
from market_model import Market, MarketModel

class Strategy:
    def __init__(self, ind, run, columns_map):
        self.ind = ind
        self.run = run
        self.columns_map = columns_map

class Filter():

    operators: dict = {
        
        'is_above':                 {'ops':4, 'func': lambda symbol,kwargs: trendline.is_above(symbol,**kwargs) , 'preced' :2, 'op_type':'bool'},
        'is_below':                 {'ops':4, 'func': lambda symbol,kwargs: trendline.is_below(symbol,**kwargs) , 'preced' :2, 'op_type':'bool'},
        'is_between':               {'ops':5, 'func': lambda symbol,kwargs: trendline.is_between(symbol,**kwargs) , 'preced' :2, 'op_type':'bool'},
        'is_crossing_above':        {'ops':4, 'func': lambda symbol,kwargs: trendline.is_crossing_above(symbol,**kwargs) , 'preced' :2, 'op_type':'bool'}, 
        'is_crossing_below':        {'ops':4, 'func': lambda symbol,kwargs: trendline.is_crossing_below(symbol,**kwargs) , 'preced' :2, 'op_type':'bool'}, 
        'is_closing':               {'ops':4, 'func': lambda symbol,kwargs: trendline.is_closing(symbol,**kwargs) , 'preced' :2, 'op_type':'bool'}, 
        'has_condition':            {'ops':3, 'func': lambda symbol,kwargs: symbol.has_condition(**kwargs) , 'preced' :2,'op_type':'bool'}, 
        'has_all_conditions':       {'ops':3, 'func': lambda symbol,kwargs: symbol.has_all_conditions(**kwargs) , 'preced' :2,'op_type':'bool'}, 
        'has_any_condition':        {'ops':3, 'func': lambda symbol,kwargs: symbol.has_any_condition(**kwargs) , 'preced' :2,'op_type':'bool'}, 
        'has_all_ind_conditions':    {'ops':2, 'func': lambda symbol,kwargs: symbol.has_all_ind_conditions(**kwargs) , 'preced' :2,'op_type':'bool'}, 
        'has_any_ind_condition':     {'ops':2, 'func': lambda symbol,kwargs: symbol.has_any_ind_condition(**kwargs) , 'preced' :2,'op_type':'bool'}, 

        'and_if':                   {'ops':2, 'func': lambda result1, result2: pd.merge(result1, result2, how='inner', on=list(result1.columns)) , 'preced' :1, 'op_type':'pd.DataFrame'},
        'or_if':                    {'ops':2, 'func': lambda result1, result2: pd.concat([result1,result2],ignore_index=True).drop_duplicates().reset_index(drop=True) , 'preced' :1, 'op_type':'pd.DataFrame'},

        'is_horizental':            {'ops':1, 'func': lambda symbol,kwargs: trendline.is_horizental(symbol,**kwargs) , 'preced' :2, 'op_type':'bool'},
        'is_vertical':              {'ops':1, 'func': lambda symbol,kwargs: trendline.is_vertical(symbol,**kwargs) , 'preced' :2, 'op_type':'bool'},
        'are_pos_divergent':        {'ops':2, 'func': lambda symbol,kwargs: trendline.are_pos_divergent(symbol,**kwargs) , 'preced' :2, 'op_type':'bool'}, 
        'are_neg_divergent':        {'ops':2, 'func': lambda symbol,kwargs: trendline.are_neg_divergent(symbol,**kwargs) , 'preced' :2, 'op_type':'bool'}, 
        'are_pos_hidden_divergent': {'ops':2, 'func': lambda symbol,kwargs: trendline.are_pos_hidden_divergent(symbol,**kwargs) , 'preced' :2, 'op_type':'bool'}, 
        'are_neg_hidden_divergent': {'ops':2, 'func': lambda symbol,kwargs: trendline.are_neg_hidden_divergent(symbol,**kwargs) , 'preced' :2, 'op_type':'bool'},
        'are_divergent':            {'ops':2, 'func': lambda symbol,kwargs: trendline.are_divergent(symbol,**kwargs) , 'preced' :2, 'op_type':'bool'}, 
        'are_close':                {'ops':2, 'func': lambda symbol,kwargs: trendline.are_close(symbol,**kwargs) , 'preced' :2, 'op_type':'bool'},
        'are_parllel':              {'ops':2, 'func': lambda symbol,kwargs: trendline.are_parllel(symbol,**kwargs) , 'preced' :2, 'op_type':'bool'},
        'are_perpendicular':        {'ops':2, 'func': lambda symbol,kwargs: trendline.are_perpendicular(symbol,**kwargs) , 'preced' :2, 'op_type':'bool'},
        'is_ascending':             {'ops':1, 'func': lambda symbol,kwargs: trendline.is_ascending(symbol,**kwargs) , 'preced' :2, 'op_type':'bool'},
        'is_descending':            {'ops':1, 'func': lambda symbol,kwargs: trendline.is_descending(symbol,**kwargs) , 'preced' :2, 'op_type':'bool'},
        'growth_ratio':             {'ops':2, 'func': lambda symbol,kwargs: trendline.growth_ratio(symbol,**kwargs) , 'preced' :2, 'op_type':'bool'},
        'avg':                      {'ops':1, 'func': lambda symbol,kwargs: indicator.tableau.TABLEAU.symbol_avg(symbol,**kwargs) , 'preced' :2, 'op_type':'bool'},
        'min':                      {'ops':1, 'func': lambda symbol,kwargs: trendline.symbol_min(symbol,**kwargs) , 'preced' :2, 'op_type':'bool'},
        'max':                      {'ops':1, 'func': lambda symbol,kwargs: trendline.symbol_max(symbol,**kwargs) , 'preced' :2, 'op_type':'bool'},
        'mid':                      {'ops':1, 'func': lambda symbol,kwargs: trendline.symbol_mid(symbol,**kwargs) , 'preced' :2, 'op_type':'bool'},
        'mid_price':                {'ops':2, 'func': lambda symbol,kwargs: trendline.mid_price(symbol,**kwargs) , 'preced' :2, 'op_type':'bool'},
        'get_avg_ratio':            {'ops':2, 'func': lambda symbol,kwargs: indicator.tableau.TABLEAU.symbol_avg_ratio(symbol,**kwargs) , 'preced' :2, 'op_type':'bool'},
        'get_growth':               {'ops':2, 'func': lambda symbol,kwargs: trendline.get_growth(symbol,**kwargs) , 'preced' :2, 'op_type':'bool'},
        'get_growth_ratio':         {'ops':2, 'func': lambda symbol,kwargs: trendline.get_growth_ratio(symbol,**kwargs) , 'preced' :2, 'op_type':'bool'}, 
        '(':                        {'ops':0, 'func': lambda symbol,kwargs: None , 'preced' :0, 'op_type':'('} 
    }

#-----------------------------------------------------------------------------------------------#
#------------------------------------------ load __init__ --------------------------------------#
#-----------------------------------------------------------------------------------------------#
   
    # def __init__(self, symbol_names = [], by='', tf ='D',offset = -1,date='', in_groups=[], except_groups=[59,68,69],in_markets=[],except_markets=[], watch_name = ''):
    #     super().__init__(symbol_names =symbol_names, by=by, tf =tf,offset = offset,date=date, in_groups=in_groups, except_groups=except_groups,in_markets=in_markets,except_markets=except_markets, watch_name = watch_name)
    #     self.initialize_state()

    def __init__(self, mw, tf=''):
        self.mw = mw
        self._tf = mw._tf if tf == '' else tf
        self.init_state()

    def refresh(self):
        self.init_state()
        return self.mw.refresh()

    def __call__(self):
        self.refresh()        
        return self

    def init_state(self):
        self._postfix: list = []
        self._op_stack : list = []
        return self

#-----------------------------------------------------------------------------------------------#
#--------------------------------------------- Output ------------------------------------------#
#-----------------------------------------------------------------------------------------------#
    def _start_web_output(self,df):
        # view_df = df[['symbol', 'date', 'open', 'high', 'low', 'close']]
        # headers = ['سهم', 'تاریخ', 'اولین', 'بیشترین', 'کمترین', 'پایانی']
        df_table: DataFrameTable = DataFrameTable(
            headers = df.columns,
            id='df-table',
            data = df.to_dict('records'),
            # columns=[{'name': i, 'id': i} for i in df.columns],
            # fixed_rows={'headers': True},
            fixed_columns={'headers': True, 'data': 1},
            page_size=100,
            # filter_action='native',
            # sort_action='native',
            # style_table={'height': '400px', 'minWidth':'100%', 'overflowY': 'auto'},
            style_cell={
                # all three widths are needed
                'minWidth': '50px', 'width': '100px', 'maxWidth': '180px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
            }
        )
        # df_table.set_cells_props(columns_id='ICHI_kijunsen', colors='#FFFFFF', background_colors='#22AA66', filters='{RSI} > 62')
        # max_rsi = result_df['ICHI_kijunsen'].max()
        # df_table.set_cells_props(colors='#FFFFFF', background_colors='#AA2266', filters='{{RSI}} = {}'.format(max_rsi))
        app = Dash(__name__)
        app.layout = df_table
        app.run_server(debug=True)

    def output(self, tinyframes = False, cols=0, plot_list=['plot_ichi'],secy_list=[], all_charts= False, start_web=False, tablo = True):
        # print(self.mw._tablo.loc[:, self.mw._tablo.columns != 'symlink'])
        print(self.mw._tabloview)

        if (self.mw._tabloview is not None and len(self.mw._tabloview) > 0):
            symbol_list = self.mw.get_symbol_list()
            candle_n = 150 if self._tf == 'D' else 100
            if len(self.mw._tabloview) < 100 and all_charts:
                SymbolChart.show_charts_for_symbols(symbol_list, tf=self._tf, last_n=candle_n, future_n=26,indicators=all_charts, volumes=all_charts,buys=False)
            if tinyframes:
                SymbolChart.show_tinyframes_for_symbols(symbols=symbol_list,cols=cols, tf=self._tf, last_n=candle_n, future_n=26,plot_list = plot_list,secy_list=secy_list)
            if start_web:
                self._start_web_output(df=self.mw._tabloview)
            if tablo:
                tabloo.show(df=self.mw._tabloview)
        return self

    def export(self, tinyframes = True, all_charts= False, tablo = True):
        if (self.mw._tabloview is not None):
            if len(self.mw._tabloview) < 100 :
                candle_n = 150 if self._tf == 'D' else 100
                SymbolChart.export_charts_for_symbols(self.mw.get_symbol_list(), tf=self._tf, last_n=candle_n, future_n=26,indicators=all_charts, volumes=all_charts,buys=False, tinyframe=tinyframes)
                if (tablo):
                    fig =  ff.create_table(self.mw._tabloview)
                    fig.update_layout(
                        autosize=False,
                        width=500,
                        height=200,
                    )
                    fig.write_image( globals.FIGURE_EXPORT_PATH + "table_plotly.png", scale=2)
                    fig.show()
        return self

#--------------------------------------------------------------------------------------------------#
#----------------------------------- Select columns, rows -----------------------------------------#
#--------------------------------------------------------------------------------------------------#
    def select(self, columns_map=None, add_columns=[], apply_format=False):
        self.run()
        return self.select_column(columns_map=columns_map,add_columns=add_columns,apply_format=apply_format)
 
    def select_column(self, columns_map=None, add_columns=[], apply_format=False):
        self.mw._tabloview = self.mw._view._map_columns(df=self.mw._tablo,columns_map=columns_map, add_columns = add_columns,apply_format=apply_format)
        return self

    def in_groups(self, grp_list):
        self.mw._tablo =  self.mw._tablo.loc[self.mw._tablo['sector_code'].isin(grp_list) ]
    
        return self
    
    def except_groups(self, grp_list):
        self.mw._tablo =  self.mw._tablo.loc[~self.mw._tablo['sector_code'].isin(grp_list) ]
        return self

    def query(self, query_str):
        self.mw._tablo.query(query_str, inplace=True) 
        return self

    def groupby(self, by, sort=None):
        self.mw._tablo.groupby(by=by,sort=sort)
        return self

#-----------------------------------------------------------------------------------------------#
#------------------------------------- set operators,arguments ---------------------------------#
#-----------------------------------------------------------------------------------------------#
    def _insert_arg(self,nam,val,idx=0):
        self._postfix.insert(idx,{'typ':'arg','nam':nam,'val':val})
        return

    def _set_arg(self,nam,val):
        self._postfix.append({'typ':'arg','nam':nam,'val':val})
        return

    def _last_token(self):
        if not self._postfix: return {'typ':None,'nam':None,'val':None}
        return self._postfix[-1]

    def _is_arg_already_inserted(self,arg_name):
        for token in self._postfix[::-1]:
            if token['typ'] != 'arg': 
                return False
            elif token['nam'] == arg_name:
                return True
        return False

    def _is_op_lessorequal_lastop(self, op): 
        if not self._op_stack:
            return False
        try: 
            op_preced = Filter.operators[op]['preced'] 
            last_op_preced = self._op_stack[-1]['preced']
            return op_preced  <= last_op_preced 
        except KeyError:  
            return False
        except IndexError:
            return False

    def _set_op(self,op):
        while(self._op_stack and self._is_op_lessorequal_lastop(op)): 
            self._postfix.append(self._op_stack.pop()) 
        operator = Filter.operators[op] 
        self._op_stack.append({'typ':'op','val':op, 'func':operator['func'], 'ops':operator['ops'], 'preced':operator['preced'], 'op_type':operator['op_type']})
        return

#-----------------------------------------------------------------------------------------------#
#--------------------------------------- exec postfix         ----------------------------------#
#-----------------------------------------------------------------------------------------------#
    def run(self):
        while self._op_stack: 
            self._postfix.append(self._op_stack.pop()) 

        if (self._postfix):
            self.mw._tablo = self._execute_postfix()
        return self

    def _postfix_args_to_kwargs(self, arg_list):
        kwargs = dict()
        while arg_list:
            arg = arg_list[0]
            a_list = [a for a in arg_list if a['nam'] == arg['nam']]
            alen = len (a_list)
            if alen > 1:
                for i in range(alen):
                    kwargs[arg['nam']+str(i+1)] = a_list[i]['val']
            else:
                kwargs[arg['nam']]= arg['val']
            arg_list = [a for a in arg_list if a['nam'] != arg['nam']]  
        return kwargs

    def _execute_postfix(self):
        # i = 0 
        # for tok in self._postfix:            
        #     print(i,tok)
        #     i += 1
        i = 0
        while len(self._postfix) > 1:
            # print(i)
            token = self._postfix[i]
            # print(token)
            if token['typ'] == 'op':
                ops = token['ops']
                op_func = token['func']
                kwargs = self._postfix_args_to_kwargs(self._postfix[i-ops:i].copy())
                if token['op_type'] == 'bool':
                    kwargs['tf'] = self._tf
                    filtered_list = self.mw._tablo['symlink'].apply(lambda symbol:op_func(symbol, kwargs)) 
                    # print(filtered_list)
                    if filtered_list.empty:
                        result =  self.mw._tablo.iloc[0:0]
                    else:
                        result = self.mw._tablo.loc[filtered_list]
                elif token['op_type'] == 'pd.DataFrame':
                    result = op_func(kwargs)
             
                self._postfix.pop(i)
                self._insert_arg('result',result,i)
                del self._postfix[i-ops:i]
                i = i-ops
            i += 1
        result =self._postfix.pop(0)
        return result['val']

#-----------------------------------------------------------------------------------------------#
#------------------------------------------- arguments -------------------------------------#
#-----------------------------------------------------------------------------------------------#
    def on_row(self, offset=-1):
        self._set_arg('offset',offset)
        return self

    def during_prev_rows(self, prev_days=1):
        self._set_arg('prev_days',prev_days)
        return self

    def set_epsilon(self, epsilon=0.05):
        self._set_arg('epsilon',epsilon)
        return self
       
    def on_column(self,column='c'):
        self._set_arg('column',column)
        return self

    def during(self, period=1):
        self._set_arg('period',period)
        return self
    
    def val(self, mode = 'c', nam='mode'):
        if mode == '(':
            self._set_op('(')
        elif mode == ')':
            while self._op_stack and self._op_stack[-1]['val'] != '(': 
                self._postfix.append(self._op_stack.pop())
            if not self._op_stack: 
                print("SYNTAX ERROR: number of paranthesis are not match")
                return self
            else: 
                self._op_stack.pop() 
        else:
            self._set_arg(nam,mode)
        return self

#-----------------------------------------------------------------------------------------------#
#------------------------------------- Logical operators ---------------------------------------#
#-----------------------------------------------------------------------------------------------#
    def and_if(self):
        self._set_op('and_if')
        return self
    
    def or_if(self):
        self._set_op('or_if')
        return self

#-----------------------------------------------------------------------------------------------#
#---------------------------------- Comparator operators ---------------------------------------#
#-----------------------------------------------------------------------------------------------#
    def is_above(self, offset=-1):
        if not self._is_arg_already_inserted('offset'):
            self._set_arg('offset',offset)
        self._set_arg('tablo_df', self.mw._tablo)
        self._set_op('is_above')
        return self

    def is_below(self, offset=-1):
        if not self._is_arg_already_inserted('offset'):
            self._set_arg('offset',offset)
        self._set_arg('tablo_df', self.mw._tablo)
        self._set_op('is_below')
        return self
     
    def is_between(self, offset=-1):
        if not self._is_arg_already_inserted('offset'):
            self._set_arg('offset',offset)
        self._set_arg('tablo_df', self.mw._tablo)
        self._set_op('is_between')
        return self
   
    def is_crossing_above(self, offset=-1):
        if not self._is_arg_already_inserted('offset'):
            self._set_arg('offset',offset)
        self._set_arg('tablo_df', self.mw._tablo)
        self._set_op('is_crossing_above')
        return self
  
    def is_crossing_below(self, offset=-1):
        if not self._is_arg_already_inserted('offset'):
            self._set_arg('offset',offset)
        self._set_arg('tablo_df', self.mw._tablo)
        self._set_op('is_crossing_below')
        return self

    def is_closing(self, offset=-1, epsilon=0.05):
        if not self._is_arg_already_inserted('offset'):
            self._set_arg('offset',offset)
        self._set_arg('tablo_df', self.mw._tablo)
        self._set_op('is_closing')
        return self

#-----------------------------------------------------------------------------------------------#
#------------------------------------------ has Condition ---------------------------------------#
#-----------------------------------------------------------------------------------------------#
    def has_condition(self, ind, cnd = 'ESCAPING_OVERSOLD', offset=-1):
        if self._last_token()['typ'] != 'arg' or self._last_token()['nam'] != 'offset':
            self._set_arg('offset',offset)
        self._set_arg('ind',ind)
        self._set_op('has_condition')
        self._set_arg('cnd',cnd)
        
        return self

    def has_all_conditions(self, ind, cnds, offset=-1):
        if self._last_token()['typ'] != 'arg' or self._last_token()['nam'] != 'offset':
            self._set_arg('offset',offset)
        self._set_arg('ind',ind)
        self._set_op('has_all_conditions')
        self._set_arg('cnds',cnds)

        return self

    def has_any_condition(self, ind, cnds, offset=-1):
        if self._last_token()['typ'] != 'arg' or self._last_token()['nam'] != 'offset':
            self._set_arg('offset',offset)
        self._set_arg('ind',ind)
        self._set_op('has_any_condition')
        self._set_arg('cnds',cnds)

    def has_all_ind_conditions(self, cnd_dic, offset=-1):
        if self._last_token()['typ'] != 'arg' or self._last_token()['nam'] != 'offset':
            self._set_arg('offset',offset)
        self._set_op('has_all_ind_conditions')
        self._set_arg('cnd_dic',cnd_dic)

        return self

    def has_any_ind_condition(self, cnd_dic, offset=-1):
        if self._last_token()['typ'] != 'arg' or self._last_token()['nam'] != 'offset':
            self._set_arg('offset',offset)
        self._set_op('has_any_ind_condition')
        self._set_arg('cnd_dic',cnd_dic)

        return self

#-----------------------------------------------------------------------------------------------#
#------------------------------------------ strategy ---------------------------------------#
#-----------------------------------------------------------------------------------------------#
    def filter_by_strategy(self, strategy_name,  offset= -1, prev_days=1):
        strategy = self.strategies[strategy_name]
        strategy.run(self,offset).select(columns_map= strategy.columns_map ).output()
        return self

    def by_strategy(self, strategy,  offset= -1, prev_days=1):
        self.val('(').strategies[strategy].run(self, offset).val(')')
        return self
   
    def by_all_strategies(self, strategies, offset= -1, prev_days=1):
        for strategy in strategies:
            self.by_strategy(self, strategy, offset).and_if()
        return self

    def by_any_strategies(self, strategies,  offset= -1, prev_days=1):
        for strategy in strategies:
            self.by_strategy(self, strategy, offset).or_if()
        return self

    strategies = {
        'ATR_CROSSING_ABOVE_ATRSMA5' : Strategy(ind='ICHI', run= lambda self, offset: self.ichi().has_all_conditions(ind='ICHI',cnds=['TENKANSEN_PERPENDICULAR_KIJUNSEN','TENKANSEN_CROSSING_ABOVE_KIJUNSEN'],offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'ADX_VERY_STRONG_BUY_SIGNAL' : Strategy(ind='ADX', run = lambda self, offset: self.adx().has_condition(ind="ADX",cnd= "VERY_STRONG_BUY_SIGNAL", offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'ADXNEG_CROSSING_ABOVE_ADXPOS' : Strategy(ind='ADX', run = lambda self, offset: self.adx().has_condition(ind="ADX",cnd= "ADXNEG_CROSSING_ABOVE_ADXPOS", offset=offset), columns_map=MarketView.regular_farsi_columns_map)

        ,'BB18_PRICE_CROSSING_ABOVE_LBAND' : Strategy(ind='BB', run = lambda self, offset: self.bb(n=18).has_condition(ind='BB',cnd='PRICE_CROSSING_ABOVE_LBAND',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'BB200_PRICE_CROSSING_ABOVE_HBAND' : Strategy(ind='BB', run = lambda self, offset: self.bb(n=200).has_condition(ind='BB',cnd='PRICE_CROSSING_ABOVE_HBAND',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'BB200_PRICE_CROSSING_ABOVE_L1236' : Strategy(ind='BB', run = lambda self, offset: self.bb(n=200).has_condition(ind='BB',cnd='PRICE_CROSSING_ABOVE_L1236',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'BB200_PRICE_CROSSING_ABOVE_MAVG' : Strategy(ind='BB', run = lambda self, offset: self.bb(n=200).has_condition(ind='BB',cnd='PRICE_CROSSING_ABOVE_MAVG',offset=offset), columns_map=MarketView.regular_farsi_columns_map)

        ,'PRICE_VOLUME_DIVERGENCE' : Strategy(ind='DIVERGENCE', run = lambda self, offset: self.divergence().has_condition(ind='DIVERGENCE',cnd='PRICE_VOLUME_DIVERGENCE',offset=offset), columns_map=MarketView.regular_farsi_columns_map)

        ,'PRICE_CLOSING_EMA34' : Strategy(ind='EMA', run= lambda self, offset: self.ema().has_condition(ind='EMA',cnd='PRICE_CLOSING_EMA34',offset=offset), columns_map=MarketView.regular_farsi_columns_map)

        ,'TENKANSEN_CROSSING_PERPENDICULAR_ABOVE_KIJUNSEN' : Strategy(ind='ICHI', run= lambda self, offset: self.ichi().has_all_conditions(ind='ICHI',cnds=['TENKANSEN_PERPENDICULAR_KIJUNSEN','TENKANSEN_CROSSING_ABOVE_KIJUNSEN'],offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'PRICE_CROSSING_ABOVE_KIJUNSEN': Strategy(ind='ICHI', run = lambda self, offset: self.ichi().has_condition('ICHI', 'PRICE_CROSSING_ABOVE_KIJUNSEN',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'PRICE_CROSSING_ABOVE_TENKANSEN': Strategy(ind='ICHI', run = lambda self, offset: self.ichi().has_condition('ICHI', 'PRICE_CROSSING_ABOVE_TENKANSEN',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'PRICE_CROSSING_ABOVE_TENKANSEN_AND_KIJUNSEN': Strategy(ind='ICHI', run = lambda self, offset: self.ichi().has_condition('ICHI', 'PRICE_CROSSING_ABOVE_TENKANSEN_AND_KIJUNSEN',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'PRICE_CROSSING_ABOVE_TENKANSEN_ABOVE_KIJUNSEN': Strategy(ind='ICHI', run = lambda self, offset: self.ichi().has_condition('ICHI', 'PRICE_CROSSING_ABOVE_TENKANSEN_ABOVE_KIJUNSEN',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'TENKANSEN_CROSSING_ABOVE_KIJUNSEN_ABOVE_KIKO1': Strategy(ind='ICHI', run = lambda self, offset: self.ichi().has_condition('ICHI', 'TENKANSEN_CROSSING_ABOVE_KIJUNSEN_ABOVE_KIKO1',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'TENKANSEN_MATCHING_KIJUNSEN_ASCENDING': Strategy(ind='ICHI', run = lambda self, offset: self.ichi().has_all_conditions(ind='ICHI',cnds=['TENKANSEN_MATCHING_KIJUNSEN','TENKANSEN_ASCENDING'],offset=offset), columns_map=MarketView.regular_farsi_columns_map)

        ,'FUTURE_KUMO_SWITCHING_ASCENDING': Strategy(ind = 'ICHI' , run = lambda self, offset: self.ichi().has_condition(ind='ICHI',cnd='FUTURE_KUMO_SWITCHING_ASCENDING',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'PRICE_CLOSING_SPANB': Strategy(ind = 'ICHI' , run = lambda self, offset: self.ichi().has_condition('ICHI', 'PRICE_CLOSING_SPANB',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'CHIKOU_CROSSING_ABOVE_KIJUNSEN_ABOVE_KUMO': Strategy(ind = 'ICHI' , run = lambda self, offset: self.ichi().has_condition(ind='ICHI',cnd='PRICE_ABOVE_KUMO').and_if().has_condition(ind='ICHI',cnd='CHIKOU_CROSSING_ABOVE_KIJUNSEN',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'ICHI_GOLDEN_SIGNAL': Strategy(ind = 'ICHI' , run = lambda self, offset: self.ichi().has_condition(ind='ICHI',cnd='GOLDEN_SIGNAL',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
    
        ,'KIJUNSEN_MATCHING_KIKO1' : Strategy(ind='ICHI', run = lambda self, offset: self.ichi().has_condition(ind='ICHI',cnd='KIJUNSEN_MATCHING_KIKO1',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'TENKANSEN_CROSSING_ABOVE_KIKO1' : Strategy(ind='ICHI', run = lambda self, offset: self.ichi().has_condition(ind='ICHI',cnd='TENKANSEN_CROSSING_ABOVE_KIKO1',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'KIJUNSEN_CROSSING_ABOVE_KIKO1' : Strategy(ind='ICHI', run = lambda self, offset: self.ichi().has_condition(ind='ICHI',cnd='KIJUNSEN_CROSSING_ABOVE_KIKO1',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'PRICE_CROSSING_ABOVE_KIKO1' : Strategy(ind='ICHI', run = lambda self, offset: self.ichi().has_condition(ind='ICHI',cnd='PRICE_CROSSING_ABOVE_KIKO1',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'PRICE_CROSSING_ABOVE_KIKO2' : Strategy(ind='ICHI', run = lambda self, offset: self.ichi().has_condition(ind='ICHI',cnd='PRICE_CROSSING_ABOVE_KIKO2',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'KIKO1_CROSSING_ABOVE_KIKO2' : Strategy(ind='ICHI', run = lambda self, offset: self.ichi().has_condition(ind='ICHI',cnd='KIKO1_CROSSING_ABOVE_KIKO2',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'KIKO1_CROSSING_BELOW_KIKO2' : Strategy(ind='ICHI', run = lambda self, offset: self.ichi().has_condition(ind='ICHI',cnd='KIKO1_CROSSING_BELOW_KIKO2',offset=offset), columns_map=MarketView.regular_farsi_columns_map)

        ,'CHIKOU_CROSSING_ABOVE_KIJUNSEN_AND_PRICE_ABOVE_KUMO' : Strategy(ind='ICHI', run = lambda self, offset: self.ichi().has_all_conditions(ind='ICHI',cnds=['CHIKOU_CROSSING_ABOVE_KIJUNSEN','PRICE_ABOVE_KUMO'],offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'CHIKOU_CROSSING_ABOVE_PRICE' : Strategy(ind='ICHI', run = lambda self, offset: self.ichi().has_condition(ind='ICHI',cnd='CHIKOU_CROSSING_ABOVE_PRICE',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'CHIKOU_CROSSING_ABOVE_KIJUNSEN' : Strategy(ind='ICHI', run = lambda self, offset: self.ichi().has_condition(ind='ICHI',cnd='CHIKOU_CROSSING_ABOVE_KIJUNSEN',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'CHIKOU_CROSSING_ABOVE_KIKO1' : Strategy(ind='ICHI', run = lambda self, offset: self.ichi().has_condition(ind='ICHI',cnd='CHIKOU_CROSSING_ABOVE_KIKO1',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'CHIKOU_CROSSING_ABOVE_KIKO2' : Strategy(ind='ICHI', run = lambda self, offset: self.ichi().has_condition(ind='ICHI',cnd='CHIKOU_CROSSING_ABOVE_KIKO2',offset=offset), columns_map=MarketView.regular_farsi_columns_map)

        ,'MACD_CROSSING_NEG_TO_POS' : Strategy(ind='MACD', run = lambda self, offset: self.macd().has_condition('MACD','CROSSING_NEG_TO_POS',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'MACD_NEG_TO_POS' : Strategy(ind='MACD', run = lambda self, offset: self.macd().has_condition('MACD','NEG_TO_POS',offset=offset), columns_map=MarketView.regular_farsi_columns_map)

        ,'EMA2_CROSSING_BELOW_EMA5' : Strategy(ind='MACROSSING', run = lambda self, offset: self.ma_crossing().has_condition(ind='MACROSSING',cnd='EMA2_CROSSING_BELOW_EMA5',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'EMA2_CROSSING_ABOVE_EMA3' : Strategy(ind='MACROSSING', run = lambda self, offset: self.ma_crossing().has_condition(ind='MACROSSING',cnd='EMA2_CROSSING_ABOVE_EMA3',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'EMA2_CROSSING_ABOVE_EMA5' : Strategy(ind='MACROSSING', run = lambda self, offset: self.ma_crossing().has_condition(ind='MACROSSING',cnd='EMA2_CROSSING_ABOVE_EMA5',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'SMA18_ABOVE_SMA54' : Strategy(ind='MACROSSING', run = lambda self, offset: self.ma_crossing().has_condition(ind='MACROSSING',cnd='SMA18_ABOVE_SMA54',offset=offset), columns_map=MarketView.regular_farsi_columns_map)

        ,'PRICE_CLOSING_MMID416' : Strategy(ind='MMID', run = lambda self, offset: self.mmid().has_condition(ind='MMID',cnd='PRICE_CLOSING_MMID416',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        
        ,'RSI_ESCAPING_OVERBOUGHT' : Strategy(ind='RSI', run= lambda self, offset: self.rsi().has_condition(ind='RSI',cnd='ESCAPING_OVERBOUGHT',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'RSI_ESCAPING_OVERSOLD' : Strategy(ind='RSI', run= lambda self, offset: self.rsi().has_condition(ind='RSI',cnd='ESCAPING_OVERSOLD',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'RSI_IN_OVERSOLD' : Strategy(ind='RSI', run= lambda self, offset: self.rsi().has_condition(ind='RSI',cnd='IN_OVERSOLD',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'RSI_IN_OVERBOUGHT' : Strategy(ind='RSI', run= lambda self, offset: self.rsi().has_condition(ind='RSI',cnd='IN_OVERBOUGHT',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'RSI_ASCENDING' : Strategy(ind='RSI', run= lambda self, offset: self.rsi().has_condition(ind='RSI',cnd='ASCENDING',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'RSI_DESCENDING' : Strategy(ind='RSI', run= lambda self, offset: self.rsi().has_condition(ind='RSI',cnd='DESCENDING',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'RSI_CROSSING_ABOVE_RSISMA5' : Strategy(ind='RSI', run= lambda self, offset: self.rsi().has_condition(ind='RSI',cnd='CROSSING_ABOVE_RSISMA5',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'RSI_CHANGING_TO_ASCENDING' : Strategy(ind='RSI', run= lambda self, offset: self.rsi().has_condition(ind='RSI',cnd='CHANGING_TO_ASCENDING',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'RSI_CHANGING_TO_DESCENDING' : Strategy(ind='RSI', run= lambda self, offset: self.rsi().has_condition(ind='RSI',cnd='CHANGING_TO_DESCENDING',offset=offset), columns_map=MarketView.regular_farsi_columns_map)

        ,'STOCH_CROSSING_POS_IN_OVERSOLD' : Strategy(ind='STOCH', run= lambda self, offset: self.stoch().has_condition(ind="STOCH",cnd="CROSSING_POS_IN_OVERSOLD", offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'STOCH_CROSSING_POS_IN_LOWERHALF' : Strategy(ind='STOCH', run= lambda self, offset: self.stoch().has_all_conditions(ind="STOCH",cnds=["CROSSING_POS","IN_LOWERHALF"],offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'STOCH_ESCAPING_OVERSOLD' : Strategy(ind='STOCH', run= lambda self, offset: self.stoch().has_condition(ind="STOCH",cnd="ESCAPING_OVERSOLD", offset=offset), columns_map=MarketView.regular_farsi_columns_map)

        ,'IND_BUYCAPITA_ABOVE_100000000' : Strategy(ind='TABLOUE', run= lambda self, offset: self.tableau().val('ind_buy_capita').is_above(offset=offset).val(1000000000), columns_map=MarketView.regular_farsi_columns_map)
        ,'CORP_BUY_17D_ABOVE_5PERCENT' : Strategy(ind = 'TABLEAU', run = lambda self, offset: self.tableau().has_condition(ind='TABLEAU',cnd='CORP_BUY_17D_ABOVE_5PERCENT',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'VOL_1D_ABOVE_MONTH' : Strategy(ind = 'TABLEAU', run = lambda self, offset: self.tableau().has_condition(ind='TABLEAU',cnd='VOL_1D_ABOVE_MONTH',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'INDBUYCAPITA_ABOVE_MONTH' : Strategy(ind = 'TABLEAU', run = lambda self, offset: self.tableau().has_condition(ind='TABLEAU',cnd='INDBUYCAPITA_ABOVE_MONTH',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'CLOSE_PERCENT_BELOW_2' : Strategy(ind = 'TABLEAU', run = lambda self, offset: self.tableau().val('close_percent').is_below(offset=offset).val(2), columns_map=MarketView.regular_farsi_columns_map)
        ,'ADJCLOSE_PERCENT_BELOW_2' : Strategy(ind = 'TABLEAU', run = lambda self, offset: self.tableau().val('adjclose_percent').is_below(offset=offset).val(2), columns_map=MarketView.regular_farsi_columns_map)
        ,'CLOSE_PERCENT_ABOVE_2' : Strategy(ind = 'TABLEAU', run = lambda self, offset: self.tableau().val('close_percent').is_above(offset=offset).val(2), columns_map=MarketView.regular_farsi_columns_map)
        ,'ADJCLOSE_PERCENT_ABOVE_2' : Strategy(ind = 'TABLEAU', run = lambda self, offset: self.tableau().val('adjclose_percent').is_above(offset=offset).val(2), columns_map=MarketView.regular_farsi_columns_map)
        ,'ASCENDING_TICK' : Strategy(ind = 'TABLEAU', run = lambda self, offset: self.tableau().has_condition(ind='TABLEAU',cnd='ASCENDING_TICK',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'DESCENDING_TICK': Strategy(ind = 'TABLEAU', run = lambda self, offset: self.tableau().has_condition(ind='TABLEAU',cnd='DESCENDING_TICK',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'CORP_OWNERSHIP_CHANGE_POS_IN9D' : Strategy(ind = 'TABLEAU', run = lambda self, offset: self.tableau().has_condition(ind='TABLEAU',cnd='CORP_OWNERSHIP_CHANGE_POS_IN9D',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'IND_OWNERSHIP_CHANGE_POS_IN9D' : Strategy(ind = 'TABLEAU', run = lambda self, offset: self.tableau().has_condition(ind='TABLEAU',cnd='IND_OWNERSHIP_CHANGE_POS_IN9D',offset=offset), columns_map=MarketView.regular_farsi_columns_map)


        ,'RSI_OVERSOLD_BB18_LBAND' : Strategy(ind='RSI,BB', run= lambda self, offset: self.bb(n=18).rsi().has_condition(ind='BB',cnd='PRICE_CROSSING_ABOVE_LBAND').and_if().has_condition(ind='RSI',cnd='IN_OVERSOLD',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'RSI_OVERSOLD_INDBUYCAPTIA_ABOVE_MONTH' : Strategy(ind='RSI,TABLEAU', run= lambda self, offset: self.tableau().rsi().has_condition(ind='TABLEAU',cnd='INDBUYCAPITA_ABOVE_MONTH').and_if().has_condition(ind='RSI',cnd='IN_OVERSOLD',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'RSI_OVERSOLD_INDBUYERPOWER' : Strategy(ind='RSI,TABLEAU', run= lambda self, offset: self.tableau().rsi().has_condition(ind='TABLEAU',cnd='INDBUYERSPOWER_ABOVE_INDSELLERSPOWER').and_if().has_condition(ind='RSI',cnd='IN_OVERSOLD',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'STOCH_OVERSOLD_INDBUYERPOWER' : Strategy(ind='STOCH,TABLEAU', run= lambda self, offset: self.tableau().stoch().has_condition(ind='TABLEAU',cnd='INDBUYERSPOWER_ABOVE_INDSELLERSPOWER').and_if().has_condition(ind='STOCH',cnd='IN_OVERSOLD',offset=offset), columns_map=MarketView.regular_farsi_columns_map)
        ,'VOL_ABOVE_MONTH_INDBUYERPOWER' : Strategy(ind='TABLEAU', run= lambda self, offset: self.tableau().has_all_conditions(ind='TABLEAU',cnds=['INDBUYERSPOWER_ABOVE_INDSELLERSPOWER','VOL_1D_ABOVE_MONTH'],offset=offset), columns_map=MarketView.regular_farsi_columns_map)
    }

#-----------------------------------------------------------------------------------------------#
#------------------------------------------- Indicators ----------------------------------------#
#-----------------------------------------------------------------------------------------------#
    def adx(self, n=14, mode_l='l',mode_h='h',mode='c', label="", as_standard = True):
        self.mw._tablo = MarketModel.adx(df=self.mw._tablo, n=n, mode_l=mode_l,mode_h=mode_h,mode=mode, label=label, as_standard = as_standard, tf = self._tf)
        return self
   
    def bb(self, n=200,ndev=2,mode='c',label='', as_standard = True):
        self.mw._tablo = MarketModel.bb(df=self.mw._tablo, n=n,ndev=ndev,mode=mode,label=label, as_standard = as_standard, tf = self._tf)
        return self

    def divergence(self, mode = 'c', divergence_period=26,label=''):
        self.mw._tablo = MarketModel.divergence(df=self.mw._tablo, mode = mode, divergence_period=divergence_period,label=label, tf = self._tf)
        return self

    def ema(self, n=34,mode='c',label='', as_standard = False):
        self.mw._tablo = MarketModel.ema(df=self.mw._tablo, n=n,mode=mode,label=label, as_standard = as_standard, tf = self._tf)
        return self

    def ichi(self,ten=9,kij=26,spanb=52, mode_l='l',mode_h='h',mode='c',label='', as_standard = True):
        self.mw._tablo = MarketModel.ichi(df=self.mw._tablo,ten=ten,kij=kij,spanb=spanb, mode_l=mode_l,mode_h=mode_h,mode=mode,label=label, as_standard = as_standard, tf = self._tf)
        return self

    def rsi(self, n=14, mode = 'c', label='', as_standard = True):
        self.mw._tablo = MarketModel.rsi(df=self.mw._tablo, n=n, mode = mode, label=label, as_standard = as_standard, tf = self._tf)
        return self
   
    def stoch(self, k=18 ,d=5,s=2, mode='c',mode_l='l',mode_h='h', label="", as_standard=True):
        self.mw._tablo = MarketModel.stoch(df=self.mw._tablo, k=k ,d=d,s=s, mode=mode,mode_l=mode_l,mode_h=mode_h, label=label, as_standard=as_standard, tf = self._tf)
        return self

    def macd(self, slow=26, fast=12, signal=9,  mode='c', label="", as_standard = True):
        self.mw._tablo = MarketModel.macd(df=self.mw._tablo, slow=slow, fast=fast, signal=signal,  mode=mode, label=label, as_standard = as_standard, tf = self._tf)
        return self

    def mmid(self, n=18,mode='c', mode_h='h',mode_l='l', label='', as_standard = False):
        self.mw._tablo = MarketModel.mmid(df=self.mw._tablo, n=n,mode=mode, mode_h=mode_h,mode_l=mode_l, label=label, as_standard = as_standard, tf = self._tf)
        return self

    def ma_crossing(self, mode='c',func1='ema', n1=10,func2='ema', n2=25,label='', as_standard = True):
        self.mw._tablo = MarketModel.ma_crossing(df=self.mw._tablo, mode=mode,func1=func1, n1=n1,func2=func2, n2=n2,label=label, as_standard = as_standard, tf = self._tf)
        return self

    def rsi_crossing(self,n1=10,n2=25, mode='c',label='', as_standard = True):
        self.mw._tablo = MarketModel.rsi_crossing(df=self.mw._tablo,n1=n1,n2=n2, mode=mode,label=label, as_standard = as_standard, tf = self._tf)
        return self

    def sma(self, n=18,mode='c',label='', as_standard = False):
        self.mw._tablo = MarketModel.sma(df=self.mw._tablo, n=n,mode=mode,label=label, as_standard = as_standard, tf = self._tf)
        return self

    def tableau(self, label='', as_standard = True):
        self.mw._tablo = MarketModel.tableau(df=self.mw._tablo, label=label, as_standard = as_standard, tf = self._tf)
        return self
   
#-----------------------------------------------------------------------------------------------#
#------------------------------------------- Tabloo ----------------------------------------#
#-----------------------------------------------------------------------------------------------#
   
#-----------------------------------------------------------------------------------------------#
#------------------------------------------- aggregation ----------------------------------------#
#-----------------------------------------------------------------------------------------------#
    def avg(self, label="AVG", mode ='v', n = 0, offset=-1):
        loc_result = [indicator.tableau.TABLEAU.symbol_avg(symbol , mode, n, offset, self._tf) for symbol in self.mw.get_symbol_list()]
        self.mw._tablo[label] = pd.Series(loc_result)
        return self

    # def sum(self, label="SUM", mode ='v', n = 0, offset=-1):
    #     loc_result = [trendline.sum(symbol , mode, n, offset, self._tf) for symbol in self.symbol_list]
    #     self._result[label] = pd.Series(loc_result)
    #     return self
        
    def sum(self):
        self.mw._tablo.sum()
        return self

    def mean(self):
        self.mw._tablo.mean()
        return self


    def min(self, label="MIN", mode ='c', n = 0, offset=-1):
        loc_result = [trendline.symbol_min(symbol , mode, n, offset, self._tf) for symbol in self.mw.get_symbol_list()]
        self.mw._tablo[label] = pd.Series(loc_result)
        return self

    def max(self, label="MAX", mode ='c', n = 0, offset=-1):
        loc_result = [trendline.symbol_max(symbol , mode, n, offset, self._tf) for symbol in self.mw.get_symbol_list()]
        self.mw._tablo[label] = pd.Series(loc_result)
        return self
            
    def mid(self, label="MID", mode ='c', n = 0, offset=-1):
        loc_result = [trendline.symbol_mid(symbol , mode, n, offset, self._tf) for symbol in self.mw.get_symbol_list()]
        self.mw._tablo[label] = pd.Series(loc_result)
        return self

    def mid_price(self, label="MID_PRICE", n = 0, offset=-1):
        loc_result = [trendline.mid_price(symbol ,n, offset, self._tf) for symbol in self.mw.get_symbol_list()]
        self.mw._tablo[label] = pd.Series(loc_result)
        return self

#-----------------------------------------------------------------------------------------------#
#------------------------------------------- other future ----------------------------------------#
#-----------------------------------------------------------------------------------------------#

    # def is_horizental(symbol:Symbol, mode = 'c', epsilon=0.05, offset = -1, period = 5,tf = 'D'):
    #     line_slope(symbol, mode, offset, period, tf) < epsilon
    
    # def is_vertical(symbol:Symbol, mode = 'c', gamma=6, offset = -1, period = 5,tf = 'D'):
    #     line_slope(symbol, mode, offset, period, tf) > gamma

    # def are_pos_divergent(symbol:Symbol, mode1='c' , mode2='v', offset = -1, period = 26,tf = 'D'):
    #     slope1 = line_slope(symbol, mode1, offset, period, tf)
    #     slope2 = line_slope(symbol, mode2, offset, period, tf)
    #     return (slope1 < 0 and slope2 > 0) 

    # def are_neg_divergent(symbol:Symbol, mode1='c' , mode2='v', offset = -1, period = 26,tf = 'D'):
    #     slope1 = line_slope(symbol, mode1, offset, period, tf)
    #     slope2 = line_slope(symbol, mode2, offset, period, tf)
    #     return (slope1 > 0 and slope2 < 0)

    # def are_pos_hidden_divergent(symbol:Symbol, mode1='c' , mode2='v', offset = -1, period = 104,tf = 'D'):
    #     return are_neg_divergent(symbol, mode1 , mode2, offset, period,tf)

    # def are_neg_hidden_divergent(symbol:Symbol, mode1='c' , mode2='v', offset = -1, period = 104,tf = 'D'):
    #     return are_pos_divergent(symbol, mode1 , mode2, offset, period,tf)
    
    # def are_divergent(symbol:Symbol, mode1='c' , mode2='v', offset = -1, period = 26,tf = 'D'):
    #     slope1 = line_slope(symbol, mode1, offset, period, tf)
    #     slope2 = line_slope(symbol, mode2, offset, period, tf)
    #     return (slope1 < 0 and slope2 > 0) or (slope1 > 0 and slope2 < 0)

    # def are_close(a,b, epsilon = 0.05):
    #     return abs(a-b) < abs(b * epsilon)

    # def cross_slope(symbol:Symbol, mode1='c' , mode2='v', offset = -1, period = 9,tf = 'D'):
    #     slope1 = line_slope(symbol, mode1, offset, period, tf)
    #     slope2 = line_slope(symbol, mode2, offset, period, tf)
    #     return abs(slope1 - slope2)

    # def are_parllel(symbol:Symbol, mode1='c' , mode2='v', epsilon=0.05, offset = -1, period = 5,tf = 'D'):
    #     return cross_slope(symbol, mode1, mode2, offset, period, tf) < epsilon

    # def are_perpendicular(symbol:Symbol, mode1='c' , mode2='v', gamma=6, offset = -1, period = 5,tf = 'D'):
    #     return cross_slope(symbol, mode1, mode2, offset, period, tf) > gamma


    # def is_ascending(symbol: Symbol, mode = 'c',min_slop = 0, offset= -1, period=3, tf = 'D'):
    #     if symbol.get_df() is None: return None

    #     return line_slope(symbol,mode, offset , period ,tf ) > min_slop


    # def is_descending(symbol: Symbol, mode = 'c',min_slop = 0, offset= -1, period=3, tf = 'D'):
    #     if symbol.get_df() is None: return None

    #     return line_slope(symbol,mode, offset , period ,tf ) < - min_slop

    # def is_in_last_n_days(last_n_days, method, **args):
    #     if 'symbol' in args:
    #         if args['symbol'].get_df() is None:
    #             return None
        
    #     for i in range(last_n_days):
    #         if 'offset' in args:
    #             args['offset'] = args['offset'] - i
    #         if method(**args):
    #             return i
    #     return -1

    # def growth_ratio(a,b):
    #     return 100 * (a-b)/b

    # def avg(symbol: Symbol, mode ='v', period = -1, offset=-1, tf = 'D'):
    #     # if(period == -1):
    #     #     return symbol.column_values(mode,tf).mean()    
    #     if (period < 1 and period != -1 ): return None
    #     start_candle = None if period == -1 else offset-period+1
    #     end_candle = None if offset == -1 else offset
    #     return symbol.column_values(mode,tf)[start_candle:end_candle].mean()
            
    # def min(symbol: Symbol, mode ='c', period = -1, offset=-1, tf = 'D'):
    #     # if(period == -1):
    #     #     return symbol.column_values(mode,tf).min()    
    #     if (period < 1 and period != -1): return sys.float_info.max
    #     start_candle = None if period == -1 else offset-period+1
    #     end_candle = None if offset == -1 else offset
    #     return symbol.column_values(mode,tf)[start_candle:end_candle].min()
            
    # def max(symbol: Symbol, mode ='c', period = -1, offset=-1, tf = 'D'):
    #     # if(period == -1):
    #     #     return symbol.column_values(mode,tf).max()    
    #     if (period < 1 and period != -1): return sys.float_info.min
    #     start_candle = None if period == -1 else offset-period+1
    #     end_candle = None if offset == -1 else offset
    #     return symbol.column_values(mode,tf)[start_candle:end_candle].max()
            
    # def mid(symbol: Symbol, mode ='c', period = -1, offset=-1, tf = 'D'):
    #     return (min(symbol,mode,period,offset,tf) + max(symbol,mode,period,offset,tf))/2

    # def mid_price(symbol: Symbol, period = -1, offset=-1, tf = 'D'):
    #     return (min(symbol,'l',period,offset,tf) + max(symbol,'h',period,offset,tf))/2

    # def get_avg_ratio(symbol: Symbol, mode = 'v', p1=1, p2=30, offset=-1, tf='D'):
    #     return avg(symbol,mode,p1, offset, tf) / avg(symbol,mode,p2, offset, tf)

    # def get_growth(symbol: Symbol, mode1='c' , mode2='o', offset=-1, tf='D'):
    #     return symbol.candle_value(mode1, offset, tf) - symbol.candle_value(mode2, offset, tf)

    # def get_growth_ratio(symbol: Symbol, mode1='c' , mode2='o', offset=-1, tf='D'):
    #     return growth_ratio( symbol.candle_value(mode1,offset, tf) , symbol.candle_value(mode2, offset, tf))


#--------------------- main ------------------------
# if __name__ == "__main__":
