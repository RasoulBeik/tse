import pandas as pd
import numpy as np
import os
import re
import sys
from symbol import Symbol
import indicator
import math

#------------------------------------------------- Line Slope, direction -----------------------------------------
def series_line_slope(sr: pd.Series):
    if sr is None: return None

    sr = sr.dropna()
    if sr.empty: return 0

    x = list (range (0, len(sr)))
    model = np.polyfit(x = x, y= sr, deg=1)
    # return model[0]
    return math.degrees(math.atan(model[0]))

def line_slope(symbol:Symbol, mode = 'c', offset = -1, period = 17,tf = 'D'):
    if symbol is None or symbol.get_df() is None: return 0
    # print(symbol.get_name(), ":", symbol.get_rows_number())

    if ((period < 1 ) or (symbol.get_rows_number(tf) < -(offset - period))): return 0
    start_candle = offset-period+1
    end_candle = None if offset == -1 else offset
    sr = symbol.column_values(mode,tf)[start_candle:end_candle]

    # if len(sr) == 0 : return None
    return series_line_slope(sr)

def cross_slope(symbol:Symbol, mode1='c' , mode2='v', offset = -1, period = 17,tf = 'D'):
    slope1 = line_slope(symbol, mode1, offset, period, tf)
    slope2 = line_slope(symbol, mode2, offset, period, tf)
    return abs(slope1 - slope2)

def are_parllel(symbol:Symbol, mode1='c' , mode2='v', epsilon=5, offset = -1, period = 5,tf = 'D'):
    return cross_slope(symbol, mode1, mode2, offset, period, tf) < epsilon

def are_perpendicular(symbol:Symbol, mode1='c' , mode2='v', gamma=83, offset = -1, period = 5,tf = 'D'):
    return cross_slope(symbol, mode1, mode2, offset, period, tf) > gamma

def is_horizental(symbol:Symbol, mode = 'c', epsilon=5, offset = -1, period = 5,tf = 'D'):
    line_slope(symbol, mode, offset, period, tf) < epsilon

def is_vertical(symbol:Symbol, mode = 'c', gamma=83, offset = -1, period = 5,tf = 'D'):
    line_slope(symbol, mode, offset, period, tf) > gamma

def is_ascending(symbol: Symbol, mode = 'c',gamma = 10, offset= -1, period=3, tf = 'D'):
    if symbol.get_df() is None: return None

    return line_slope(symbol,mode, offset , period ,tf ) > gamma
    # start_candle = offset-period
    # end_candle = offset-1

    # for i in range(start_candle,end_candle):
    #     if (symbol.candle_value(mode,i,tf) is None) or (symbol.candle_value(mode,i+1,tf) is None):
    #         return False
    #     if symbol.candle_value(mode,i,tf) > symbol.candle_value(mode,i+1,tf):
    #         return False
    # return True

def is_descending(symbol: Symbol, mode = 'c',gamma = 10, offset= -1, period=3, tf = 'D'):
    if symbol.get_df() is None: return None

    return line_slope(symbol,mode, offset , period ,tf ) < -gamma

    # start_candle = offset-period
    # end_candle = offset -1 

    # for i in range(start_candle,end_candle):
    #     if (symbol.candle_value(mode,i,tf) is None) or (symbol.candle_value(mode,i+1,tf) is None):
    #         return False
    #     if symbol.candle_value(mode,i,tf) < symbol.candle_value(mode,i+1,tf):
    #         return False
    # return True

#------------------------------------------------------------ divergency -------------------------------------------------------
def are_pos_divergent(symbol:Symbol, mode1='c' , mode2='v', offset = -1, period = 26,tf = 'D'):
    slope1 = line_slope(symbol, mode1, offset, period, tf)
    slope2 = line_slope(symbol, mode2, offset, period, tf)
    return (slope1 < 0 and slope2 > 0) 

def are_neg_divergent(symbol:Symbol, mode1='c' , mode2='v', offset = -1, period = 26,tf = 'D'):
    slope1 = line_slope(symbol, mode1, offset, period, tf)
    slope2 = line_slope(symbol, mode2, offset, period, tf)
    return (slope1 > 0 and slope2 < 0)

def are_pos_hidden_divergent(symbol:Symbol, mode1='c' , mode2='v', offset = -1, period = 104,tf = 'D'):
    return are_neg_divergent(symbol, mode1 , mode2, offset, period,tf)

def are_neg_hidden_divergent(symbol:Symbol, mode1='c' , mode2='v', offset = -1, period = 104,tf = 'D'):
    return are_pos_divergent(symbol, mode1 , mode2, offset, period,tf)

def are_divergent(symbol:Symbol, mode1='c' , mode2='v', offset = -1, period = 26,tf = 'D'):
    slope1 = line_slope(symbol, mode1, offset, period, tf)
    slope2 = line_slope(symbol, mode2, offset, period, tf)
    return (slope1 < 0 and slope2 > 0) or (slope1 > 0 and slope2 < 0)

#------------------------------------------------- close, cross, above, between -----------------------------------------
def are_close(a,b, epsilon = 0.05):
    return abs(a-b) < abs(min(a,b) * epsilon)

def is_closing(symbol: Symbol, mode1 , mode2, epsilon=0.05, offset=-1, tf = 'D', tablo_df=None):
    if symbol.get_df() is None: return False

    t1 = symbol.candle_value (mode1, offset, tf)
    if t1 is None and tablo_df is not None: t1 = tablo_df.loc[tablo_df['symbol'] == symbol.get_name()][mode1].values[0]
    t2 = symbol.candle_value (mode2, offset, tf)
    if t2 is None and tablo_df is not None: t2 = tablo_df.loc[tablo_df['symbol'] == symbol.get_name()][mode2].values[0]

    if (t1 is None) or (t2 is None):
        return False
    return are_close(t1 , t2, epsilon)

def is_above(symbol: Symbol, mode1, mode2, offset=-1, tf = 'D', tablo_df=None):
    if symbol.price_df[tf] is None: return None
    
    t1 = symbol.candle_value(mode1, offset, tf)
    if t1 is None and tablo_df is not None: t1 = tablo_df.loc[tablo_df['symbol'] == symbol.get_name()][mode1].values[0]
    t2 = symbol.candle_value(mode2, offset, tf)
    if t2 is None and tablo_df is not None: t2 = tablo_df.loc[tablo_df['symbol'] == symbol.get_name()][mode2].values[0]

    if (t1 is None) or (t2 is None):
        return False
    return t1 > t2

def is_below(symbol: Symbol, mode1, mode2, offset=-1, tf = 'D', tablo_df=None):
    return is_above(symbol, mode2, mode1, offset, tf, tablo_df)

def is_between(symbol: Symbol, mode1, mode2, mode3, offset=-1, tf = 'D', tablo_df=None):
    if symbol.price_df[tf] is None: return None

    t = symbol.candle_value(mode1, offset, tf)
    if t is None and tablo_df is not None: t = tablo_df.loc[tablo_df['symbol'] == symbol.get_name()][mode1].values[0]
    t_l = symbol.candle_value(mode2, offset, tf)
    if t_l is None and tablo_df is not None: t_l = tablo_df.loc[tablo_df['symbol'] == symbol.get_name()][mode2].values[0]
    t_h = symbol.candle_value(mode3, offset, tf)
    if t_h is None and tablo_df is not None: t_h = tablo_df.loc[tablo_df['symbol'] == symbol.get_name()][mode3].values[0]

    if (t is None) or (t_l is None) or (t_h is None):
        return False
    return (symbol_min(t_l,t_h) <= t <= symbol_max(t_l,t_h))

def is_crossing_above(symbol: Symbol, mode1, mode2, offset=-1, prev_days=1, tf = 'D', tablo_df=None):
    if symbol.get_df() is None: return None
   
    if not is_above(symbol, mode1, mode2, offset, tf ,tablo_df ):
        return False
    for i in range(prev_days):
        if is_above(symbol, mode1, mode2, offset-i-1, tf ,tablo_df):
            return False
    return True

def is_crossing_below(symbol: Symbol, mode1, mode2, offset=-1, prev_days=1, tf = 'D', tablo_df=None):
    return is_crossing_above(symbol, mode2, mode1, offset, prev_days, tf,tablo_df)

#------------------------------------------------- last n days -----------------------------------------
def is_in_last_n_days(last_n_days, method, **args):
    if 'symbol' in args:
        if args['symbol'].get_df() is None:
            return None
    # print(last_n_days, args)
   
    for i in range(last_n_days):
        if 'offset' in args:
            args['offset'] = args['offset'] - i
        
        if method(**args):
            return True
    return False


#--------------------------------------------------- sum --------------------------------------------------
def series_sum(sr: pd.Series, period = 0, offset=-1):
    if (sr is None): return None
    if (period < 1 and period != 0 ): return None
    start_candle = None if period == 0 else offset-period+1
    end_candle = None if offset == -1 else offset + 1
    return sr[start_candle:end_candle].sum()
        
def symbol_sum(symbol: Symbol, mode ='v', period = 0, offset=-1, tf = 'D'):
    return series_sum(sr=symbol.column_values(mode,tf),period=period, offset=offset)

#------------------------------------------------- min -----------------------------------------
def series_min(sr: pd.Series, period = 0, offset=-1):
    if (sr is None): return None
    # if(period == -1):
    #     return symbol.column_values(mode,tf).min()    
    if (period < 1 and period != 0): return sys.float_info.max
    start_candle = None if period == 0 else offset-period+1
    end_candle = None if offset == -1 else offset + 1
    return sr[start_candle:end_candle].min()
    
def symbol_min(symbol: Symbol, mode ='c', period = 0, offset=-1, tf = 'D'):
    return series_min(symbol.column_values(mode,tf), period, offset)
        
#------------------------------------------------- max -----------------------------------------
def symbol_max(symbol: Symbol, mode ='c', period = -1, offset=-1, tf = 'D'):
    # if(period == -1):
    #     return symbol.column_values(mode,tf).max()    
    if (period < 1 and period != -1): return sys.float_info.min
    start_candle = None if period == -1 else offset-period+1
    end_candle = None if offset == -1 else offset + 1
    return symbol.column_values(mode,tf)[start_candle:end_candle].max()
        
#------------------------------------------------- mid -----------------------------------------
def symbol_mid(symbol: Symbol, mode ='c', period = 0, offset=-1, tf = 'D'):
    return (symbol_min(symbol,mode,period,offset,tf) + symbol_max(symbol,mode,period,offset,tf))/2

def mid_price(symbol: Symbol, period = 0, offset=-1, tf = 'D'):
    return (symbol_min(symbol,'l',period,offset,tf) + symbol_max(symbol,'h',period,offset,tf))/2

#------------------------------------------------------ growth ------------------------------------------------
def growth_ratio(a,b):
    if a is None or b is None: return 0 
    return 100 * (a-b)/b

def get_growth(symbol: Symbol, mode1='c' , mode2='o', offset=-1, tf='D'):
    return symbol.candle_value(mode1, offset, tf) - symbol.candle_value(mode2, offset, tf)

def get_growth_ratio(symbol: Symbol, mode1='c' , mode2='o', offset=-1, tf='D'):
    return growth_ratio( symbol.candle_value(mode1,offset, tf) , symbol.candle_value(mode2, offset, tf))


#------------------------------------------------------ filter , symbol lists, dfs  ------------------------------------------------
def list_intersect(data1, data2):
    return list(set(data1).intersection(data2))

def list_union(data1, data2):
    return list(set(data1).union(data2))

def df_intersect(data1, data2, on_column_list=None):
    if on_column_list is None: on_column_list = list(data1.columns)
    return pd.merge(data1, data2, how='inner', on=on_column_list)

def df_union(data1, data2):
    return pd.concat([data1,data2],ignore_index=True).drop_duplicates().reset_index(drop=True)
    
    