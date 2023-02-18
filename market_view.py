import pandas as pd
import datetime
import tabloo
from dash import Dash
from dftable import DataFrameTable

import globals

from symbol import Symbol
from chart import SymbolChart
import re 


#-----------------------------------------------------------------------------------------------#
#------------------------------------------ ColumnsMap --------------------------------------#
#-----------------------------------------------------------------------------------------------#
def format_number(number):
    if isinstance(number, int):
        result = '{:,}'.format(number)
    # elif isinstance(number, float)
    else:
        result = '{:,.2f}'.format(number)
    if result[0] == '-':
        result = '({})'.format(result[1:])
    return result

class MarketView:
    def __init__(self):
        self._columns_map = MarketView.all_columns_map

    all_columns_map = {
        '*' : {'src' : '*'}
    }

    regular_columns_map = {
        'no': {'src' : 'no'}
        ,'symbol': {'src' : 'symbol'}
        ,'date': {'src' : 'date'}
        ,'open': {'src' : 'open'}
        ,'high': {'src' : 'high'}
        ,'low': {'src' : 'low'}
        ,'close': {'src' : 'close'}
        ,'close_percent': {'src':'close_percent'}
        ,'adjClose': {'src' : 'adjClose'}
        ,'adjclose_percent': {'src':'adjclose_percent'}
        ,'vol_1to30' : {'src': 'vol_1to30'}
        ,'growth_month_min' : {'src': 'growth_month_min'}
        ,'ind_buyers_power' : {'src': 'ind_buyers_power'}
    }

    regular_farsi_columns_map = {
        'ردیف': {'src' : 'no'}
        ,'نماد': {'src' : 'symbol'}
        ,'تاریخ': {'src' : 'date'}
        ,'اولین': {'src' : 'open', 'form' : format_number}
        ,'بیشترین': {'src' : 'high', 'form' : format_number}
        ,'کمترین': {'src' : 'low', 'form' : format_number}
        ,'آخرین': {'src' : 'close', 'form' : format_number}
        ,'رشد آخرین': {'src':'close_percent', 'form' : format_number}
        ,'پایانی': {'src' : 'adjClose', 'form' : format_number}
        ,'رشد پایانی': {'src':'adjClose_percent', 'form' : format_number}
        ,'حجم به ماه' : {'src':'vol_1to30', 'form' : format_number}
        ,'تا کف ماهانه' : {'src': 'growth_month_min', 'form' : format_number}
        ,'قدرت خریدار' : {'src': 'ind_buyers_power', 'form' : format_number}
    }

    default_columns_map = {
        'ردیف': {'src' : 'no'}
        ,'نماد': {'src' : 'symbol'}
        ,'تاریخ': {'src' : 'date'}
        ,'زمان': {'src' : 'time'}
        ,'آخرین': {'src' : 'close', 'form' : format_number}
        ,'رشد آخرین': {'src':'close_percent', 'form' : format_number}
        ,'پایانی': {'src' : 'adjClose', 'form' : format_number}
        ,'رشد پایانی': {'src':'adjClose_percent', 'form' : format_number}
        ,'حجم به ماه' : {'src':'vol_1to30', 'form' : format_number}
        ,'تا کف ماهانه' : {'src': 'growth_month_min', 'form' : format_number}
        ,'قدرت خریدار' : {'src': 'ind_buyers_power', 'form' : format_number}
        ,'تغییر سهامدار عمده' : {'src': 'changed_shares', 'form' : format_number}
        ,'تیک صعودی' : {'src': 'asc_tick'}
        ,'درصد حجم معامله' : {'src': 'vol_percent', 'form' : format_number}
        ,'حجم/حجم مبنا' : {'src':'vol_to_basevol', 'form' : format_number}
        ,'رشد هفتگی': {'src' : 'growth_week' , 'form' : format_number}
        ,'رشد سالانه': {'src' : 'growth_year' , 'form' : format_number}
        ,'سرانه خرید حقیقی': {'src' : 'ind_buy_capita', 'form' : format_number}
        ,'سرانه فروش حقیقی': {'src' : 'ind_sell_capita', 'form' : format_number}
        ,'سرانه خرید حقوقی': {'src' : 'corp_buy_capita', 'form' : format_number}
        ,'سرانه فروش حقوقی': {'src' : 'corp_sell_capita', 'form' : format_number}
        ,'خ حقیقی': {'src' : 'individual_buy_vol', 'form' : format_number}
        ,'ف حقیقی': {'src' : 'individual_sell_vol', 'form' : format_number}
        ,'خ حقوقی': {'src' : 'corporate_buy_vol', 'form' : format_number}
        ,'ف حقوقی': {'src' : 'corporate_sell_vol', 'form' : format_number}
        ,'مالکیت حقیقی': {'src' : 'ind_ownership_change', 'form' : format_number}
    
        ,'بازار': {'src' : 'market'}
        ,'زیربازار': {'src' : 'submarket'}
        ,'نام': {'src' : 'corp_name'}
        ,'گروه': {'src' : 'sector'}
        ,'تعداد سهام': {'src' : 'total_shares', 'form' : format_number}
        ,'ارزش بازار': {'src' : 'market_value', 'form' : format_number}
        ,'درصد شناور': {'src' : 'float_shares', 'form' : format_number}
        ,'تعداد': {'src' : 'count', 'form' : format_number}
        ,'حجم': {'src' : 'volume', 'form' : format_number}
        ,'ارزش': {'src' : 'value', 'form' : format_number}
        ,'تعداد ف': {'src' : 'offer_count_1', 'form' : format_number}
        ,'حجم ف': {'src' : 'offer_volume_1', 'form' : format_number}
        ,'قیمت ف': {'src' : 'offer_price_1', 'form' : format_number}
        ,'قیمت خ': {'src' : 'demand_price_1', 'form' : format_number}
        ,'حجم خ': {'src' : 'demand_volume_1', 'form' : format_number}
        ,'تعداد خ': {'src' : 'demand_count_1', 'form' : format_number}
        ,'صف': {'src' : 'queue'}
        ,'ارزش صف': {'src' : 'queue_val', 'form' : format_number}
        ,'کمترین مجاز': {'src' : 'tmin', 'form' : format_number} #, 'typ': 'int'}
        ,'بیشترین مجاز': {'src' : 'tmax', 'form' : format_number} #, 'typ': 'int'}
        ,'RSI': {'src' : 'RSI'} 
        # ,'لینک': {'src' : 'urls'}
    }

    ma_columns_map = {
        'ردیف': {'src' : 'no'}
        ,'نماد': {'src' : 'symbol'}
        ,'تاریخ': {'src' : 'date'}
        ,'اولین': {'src' : 'open', 'form' : format_number}
        ,'بیشترین': {'src' : 'high', 'form' : format_number}
        ,'کمترین': {'src' : 'low', 'form' : format_number}
        ,'آخرین': {'src' : 'close', 'form' : format_number}
        ,'رشد آخرین': {'src':'close_percent', 'form' : format_number}
        ,'پایانی': {'src' : 'adjClose', 'form' : format_number}
        ,'رشد پایانی': {'src':'adjClose_percent', 'form' : format_number}
        ,'حجم به ماه' : {'src':'vol_1to30', 'form' : format_number}
        ,'تا کف ماهانه' : {'src': 'growth_month_min', 'form' : format_number}
        ,'قدرت خریدار' : {'src': 'ind_buyers_power', 'form' : format_number}
        ,'میانگین صعودی' : {'src': 'ma_ascending'}
    }

    symbolwatch_columns_map = {
        'ردیف': {'src' : 'no'}
        ,'نماد': {'src' : 'symbol'}
        ,'تاریخ': {'src' : 'date'}
        ,'زمان': {'src' : 'time'}
        ,'آخرین': {'src' : 'close', 'form' : format_number}
        ,'رشد آخرین': {'src':'close_percent', 'form' : format_number}
        ,'پایانی': {'src' : 'adjClose', 'form' : format_number}
        ,'رشد پایانی': {'src':'adjClose_percent', 'form' : format_number}
        ,'حجم به ماه' : {'src':'vol_1to30', 'form' : format_number}
        ,'تا کف ماهانه' : {'src': 'growth_month_min', 'form' : format_number}
        ,'قدرت خریدار' : {'src': 'ind_buyers_power', 'form' : format_number}
        ,'تغییر سهامدار عمده' : {'src': 'changed_shares', 'form' : format_number}
        ,'تیک صعودی' : {'src': 'asc_tick'}
        ,'درصد حجم معامله' : {'src': 'vol_percent', 'form' : format_number}
        ,'حجم/حجم مبنا' : {'src':'vol_to_basevol', 'form' : format_number}
        ,'رشد هفتگی': {'src' : 'growth_week' , 'form' : format_number}
        ,'رشد سالانه': {'src' : 'growth_year' , 'form' : format_number}
        ,'سرانه خرید حقیقی': {'src' : 'ind_buy_capita', 'form' : format_number}
        ,'سرانه فروش حقیقی': {'src' : 'ind_sell_capita', 'form' : format_number}
        ,'سرانه خرید حقوقی': {'src' : 'corp_buy_capita', 'form' : format_number}
        ,'سرانه فروش حقوقی': {'src' : 'corp_sell_capita', 'form' : format_number}
        ,'خ حقیقی': {'src' : 'individual_buy_vol', 'form' : format_number}
        ,'ف حقیقی': {'src' : 'individual_sell_vol', 'form' : format_number}
        ,'خ حقوقی': {'src' : 'corporate_buy_vol', 'form' : format_number}
        ,'ف حقوقی': {'src' : 'corporate_sell_vol', 'form' : format_number}
        ,'مالکیت حقیقی': {'src' : 'ind_ownership_change', 'form' : format_number}
    
        ,'بازار': {'src' : 'market'}
        ,'زیربازار': {'src' : 'submarket'}
        ,'نام': {'src' : 'corp_name'}
        ,'گروه': {'src' : 'sector'}
        ,'درصد شناور': {'src' : 'float_shares', 'form' : format_number}
        ,'تعداد': {'src' : 'count', 'form' : format_number}
        ,'حجم': {'src' : 'volume', 'form' : format_number}
        ,'ارزش': {'src' : 'value', 'form' : format_number}
        ,'تعداد ف': {'src' : 'offer_count_1', 'form' : format_number}
        ,'حجم ف': {'src' : 'offer_volume_1', 'form' : format_number}
        ,'قیمت ف': {'src' : 'offer_price_1', 'form' : format_number}
        ,'قیمت خ': {'src' : 'demand_price_1', 'form' : format_number}
        ,'حجم خ': {'src' : 'demand_volume_1', 'form' : format_number}
        ,'تعداد خ': {'src' : 'demand_count_1', 'form' : format_number}
        ,'صف': {'src' : 'queue'}
        ,'ارزش صف': {'src' : 'queue_val', 'form' : format_number}
        ,'کمترین مجاز': {'src' : 'tmin', 'form' : format_number} #, 'typ': 'int'}
        ,'بیشترین مجاز': {'src' : 'tmax', 'form' : format_number} #, 'typ': 'int'}
        # ,'لینک': {'src' : 'urls'}
    }


    @staticmethod
    def apply_view_format(df, columns_map= regular_farsi_columns_map):
        for col_name, col_map in columns_map.items():
            col_name = col_name.strip()
            if 'form' in col_map and callable(col_map['form']):
                df[col_name] = df[col_name].apply(lambda num: col_map['form'](num))
            if 'typ' in col_map:
                # print(col_map['typ'])
                df[col_name] = df[col_name].astype(col_map['typ'])
        return df

    def _apply_view_format(self, df, columns_map= None):
        if columns_map is None: columns_map = self._columns_map
        return MarketView.apply_view_format(df, columns_map)
            
    @staticmethod
    def map_columns(df, columns_map = regular_farsi_columns_map, add_columns=None, apply_format = False):
        if df is None: return None
        result_df = pd.DataFrame()
        for col_name, col_map in columns_map.items():
            col_name = col_name.strip()
            if col_name == '*':
                result_df = df.copy()
            elif col_name.startswith('-'):
                col_name = col_name[1:].strip()
                result_df.drop(col_name, axis=1, inplace=True)
            elif 'val' in col_map:
                result_df[col_name] = col_map['val'](df) if callable(col_map['val']) else col_map['val']
            else:
                result_df[col_name] = df[col_map['src']]
            if apply_format:
                MarketView.apply_view_format(df = result_df)
            
        if add_columns is not None:
            for col_name in add_columns:
                if col_name not in result_df:
                    result_df[col_name] = df[col_name]
        return result_df

    def _map_columns(self, df, columns_map = None, add_columns=None, apply_format = False):
        if columns_map is None: columns_map = self._columns_map
        return MarketView.map_columns(df,columns_map,add_columns, apply_format)

class RegularView(MarketView):
    def __init__(self):
        super().__init__()
        self._columns_map = MarketView.regular_columns_map

class RegularFarsiView(MarketView):
    def __init__(self):
        super().__init__()
        self._columns_map = MarketView.regular_farsi_columns_map

class DefaultView(MarketView):
    def __init__(self):
        super().__init__()
        self._columns_map = MarketView.default_columns_map

class MAView(MarketView):
    def __init__(self):
        super().__init__()
        self._columns_map = MarketView.ma_columns_map

class SymbolWatchView(MarketView):
    def __init__(self):
        super().__init__()
        self._columns_map = MarketView.symbolwatch_columns_map

