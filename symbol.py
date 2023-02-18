import pytse_client as tse
from pytse_client import config, symbols_data, tse_settings, download_client_types_records, Ticker
from pytse_client.symbols_data import get_ticker_index
import pandas as pd
import numpy as np
import ta
import os
import re
from datetime import datetime, time, timedelta
from jdatetime import jalali
import jdatetime
import symbol_repository as rep
import globals



## Symbols is a global dictionary in module symbol
SymbolsDic: dict = dict()
SymbolsBaseInfo = pd.DataFrame()

class Symbol:
    Groups : dict = {
        10 :'استخراج زغال سنگ', 
        14 : 'استخراج ساير معادن',
        13 : 'استخراج کانه هاي فلزي',
        11 : 'استخراج نفت گاز و خدمات جنبي جز اکتشاف',
        73 : 'اطلاعات و ارتباطات',
        70 : 'انبوه سازي، املاك و مستغلات',
        22 : 'انتشار، چاپ و تکثير',
        69 : 'اوراق تامين مالي',
        59 : 'اوراق حق تقدم استفاده از تسهيلات مسكن',
        57 : 'بانكها و موسسات اعتباري',
        66 : 'بيمه وصندوق بازنشستگي به جزتامين اجتماعي',
        45 : 'پيمانكاري صنعتي',
        46 : 'تجارت عمده فروشي به جز وسايل نقليه موتور',
        26 : 'توليد محصولات كامپيوتري الكترونيكي ونوري',
        61 : 'حمل و نقل آبي',
        60 : 'حمل ونقل، انبارداري و ارتباطات',
        74 : 'خدمات فني و مهندسي',
        47 : 'خرده فروشي،باستثناي وسايل نقليه موتوري',
        34 : 'خودرو و ساخت قطعات',
        19 : 'دباغي، پرداخت چرم و ساخت انواع پاپوش',
        72 : 'رايانه و فعاليت‌هاي وابسته به آن',
        1  : 'زراعت و خدمات وابسته',
        32 : 'ساخت دستگاه‌ها و وسايل ارتباطي',
        28 : 'ساخت محصولات فلزي',
        54 : 'ساير محصولات كاني غيرفلزي',
        58 : 'ساير واسطه گريهاي مالي',
        56 : 'سرمايه گذاريها',
        53 : 'سيمان، آهك و گچ',
        39 : 'شرکتهاي چند رشته اي صنعتي',
        68 : 'صندوق سرمايه گذاري قابل معامله',
        40 : 'عرضه برق، گاز، بخاروآب گرم',
        23 : 'فراورده هاي نفتي، كك و سوخت هسته اي',
        90 : 'فعاليت هاي هنري، سرگرمي و خلاقانه',
        67 : 'فعاليتهاي كمكي به نهادهاي مالي واسط',
        27 :'فلزات اساسي',
        38 :'قند و شكر',
        49 :'كاشي و سراميك',
        25 :'لاستيك و پلاستيك',
        29 :'ماشين آلات و تجهيزات',
        31 :'ماشين آلات و دستگاه‌هاي برقي', 
        20 :'محصولات چوبي',
        44 : 'محصولات شيميايي',
        42 : 'محصولات غذايي و آشاميدني به جز قند و شكر',
        21 : 'محصولات كاغذي',
        64 : 'مخابرات',
        17 : 'منسوجات',
        43 : 'مواد و محصولات دارويي',
        55 : 'هتل و رستوران',
        65 : 'واسطه‌گري‌هاي مالي و پولي'
    }
    
    # symbols_ohlc_daily: dict = dict()
    jalali_calendar = False

#----------------------------------------- Init - Load ---------------------------------------------
    def __init__(self, symbol_name, read_csv=True, read_base_info=False):
        global SymbolsBaseInfo
        self._symbol_name_ = symbol_name
        self._symbol_id_ = get_ticker_index(self._symbol_name_)
        if read_csv:
            if Symbol.jalali_calendar:
                self._symbol_df_ = rep.read_data_file(symbol_name, timeframe='DJ')
                self._weekly_df_ = rep.read_data_file(symbol_name, timeframe='WJ')
                self._monthly_df_ = rep.read_data_file(symbol_name, timeframe='MJ')
            else:
                self._symbol_df_ = rep.read_data_file(symbol_name, timeframe='D')
                self._weekly_df_ = rep.read_data_file(symbol_name, timeframe='W')
                self._monthly_df_ = rep.read_data_file(symbol_name, timeframe='M')
        elif symbol_name in SymbolsDic.keys():
            self._symbol_df_ = SymbolsDic[symbol_name].daily_df
            self._weekly_df_ = SymbolsDic[symbol_name].weekly_df
            self._monthly_df_ = SymbolsDic[symbol_name].monthly_df
        else:
            self._symbol_df_ = None
            self._weekly_df_ = None
            self._monthly_df_ = None

        self._intraday_df_ = None
        self._intraday_ind_ : dict = dict()
        self._daily_ind_ : dict = dict()
        self._weekly_ind_ : dict = dict()
        self._monthly_ind_ : dict = dict()

        if read_base_info: Symbol.load_base_info()
        self.init_base_info()

        return

    def init_base_info(self):
        symbol_base_info = SymbolsBaseInfo.loc[SymbolsBaseInfo['symbol'] == self._symbol_name_] if len(SymbolsBaseInfo) > 0 else None
        if (symbol_base_info is not None) and (not symbol_base_info.empty) :
            # print(self._symbol_name_, ":", symbol_base_info)
            self._eps_ = symbol_base_info['eps'].values[0]
            self._total_shares_ = symbol_base_info['total_shares'].values[0]
            self._float_shares_ = symbol_base_info['float_shares'].values[0]
            self._sector_ = symbol_base_info['sector'].values[0]
            self._sector_code_ = symbol_base_info['sector_code'].values[0]
            self._market = symbol_base_info['market'].values[0]
            self._submarket = symbol_base_info['submarket'].values[0]
        else:
            self._eps_ = 0
            self._total_shares_ = 0
            self._float_shares_ = 0
            self._sector_ = ''
            self._sector_code_ = 0
            self._market = ''
            self._submarket = ''
    
    def init_intraday_trades(self, daily_trades):
        self._intraday_df_ = daily_trades[daily_trades['symbol'] == self.get_name()].copy()

    @staticmethod
    def load_base_info(date=None, forced_load= False):
        global SymbolsBaseInfo
        try:
            if forced_load or SymbolsBaseInfo.empty:
                SymbolsBaseInfo = rep.load_base_info(date=date)
            return SymbolsBaseInfo
        except:
            return None

    @staticmethod
    def load_symbols_ohlc_daily(symbol_names, forced_load= False):
        if symbol_names is None: symbol_names = sorted(list(symbols_data.all_symbols()))
        if forced_load:
            for symbol_name in symbol_names:
                symbol = Symbol(symbol_name, read_csv=True)
                SymbolsDic[symbol_name] = symbol
        else:
            for symbol_name in symbol_names:
                if symbol_name not in SymbolsDic:
                    symbol = Symbol(symbol_name, read_csv=True)
                    SymbolsDic[symbol_name] = symbol
        return

    @staticmethod
    def load_symbol_groups_info():
        try:
            return pd.read_csv(globals.SYMBOLS_GROUPS_INFO_FILE)
        except:
            pass
  
#--------------------------------------- symbol Properties ----------------------------------------
    @property
    def symbol_id(self):
        return self._symbol_id_
        
    @property
    def eps(self):
        return self._eps_

    @property
    def total_shares(self):
        return self._total_shares_

    @property
    def float_shares(self):
        return self._float_shares_

    @property
    def sector(self):
        return self._sector_

    @property
    def sector_code(self):
        return self._sector_code_

    @property
    def market(self):
        return self._market

    @property
    def submarket(self):
        return self._submarket

    def get_name(self):
        return self._symbol_name_

#------------------------------------------ DF ----------------------------------------------
    @property
    def intraday_df(self):
        return self._intraday_df_

    @property
    def daily_df(self):
        return self._symbol_df_

    @property
    def weekly_df(self):
        return self._weekly_df_

    @property
    def monthly_df(self):
        return self._monthly_df_

    @property
    def price_df(self):
        return {'M': self._monthly_df_, 'W': self._weekly_df_, 'D': self._symbol_df_, 'm': self._intraday_df_}

    def get_df(self, tf='D'):
        return self.price_df[tf]
    
#------------------------------------------ Indicators --------------------------------------------
    @property
    def indicators(self):
        return {'M': self._monthly_ind_, 'W': self._weekly_ind_, 'D': self._daily_ind_, 'm': self._intraday_ind_}

    def add_indicator(self, ind_name, ind_obj, tf='D'):
        # print ("add: " , self.get_name(),":", tf ,":", ind_name)
        if self.indicators[tf] is not None: 
            self.indicators[tf][ind_name] = ind_obj
        return
    
    def get_indicator(self, ind_name, tf='D'):
        try:
            return self.indicators[tf][ind_name]
        except KeyError:
            # print ("No key: ", self.get_name(),":", tf ,":", ind_name)
            return None
        
#-------------------------------------------- Column ----------------------------------------------
    def get_columns_number(self, tf='D'):
        return len(self.price_df[tf].columns)

    def get_column(self, col_name, tf='D'):
        if self.price_df[tf] is not None: 
            return self.price_df[tf][col_name]
        return None
    
    def add_column(self, col_name, col_value, tf='D'):
        if self.price_df[tf] is not None: 
            self.price_df[tf][col_name] = col_value
        return
    
    def column_values(self, mode='c', tf='D'):
        if self.price_df[tf] is None:
            return None
        
        df = self.price_df[tf]
        # try:
        if mode == 'c':
            t = df['close']
        elif mode == 'h':
            t = df['high']
        elif mode == 'l':
            t = df['low']
        elif mode == 'o':
            t = df['open']
        elif mode == 'v':
            t = df['volume']
        else:
            t = df[mode]
        return t
        # except KeyError:
        #      print("Error: Access to symbol=" ,self._symbol_name_, " column=", mode)
        #      return None
 
#--------------------------------------------- Row ------------------------------------------------
    def get_rows_number(self, tf='D'):
        return len(self.price_df[tf])

    def get_row(self, row_number=-1, tf='D'):
        if self.price_df[tf] is not None: 
            try:
                return self.price_df[tf].iloc[row_number]
            except IndexError:
                pass
        return None

    def get_row_bydate(self, date=None, tf='D'):
        # print(tf)
        if date is None: date = datetime.now().strftime('%Y%m%d')
        df = self.price_df[tf]
        if df is not None: 
            try:
                return df.loc[df['date'].isin([date])].iloc[-1]
            except IndexError:
                pass
        return None

    def get_rows(self, start, end, step, tf='D'):
        if self.price_df[tf] is not None: 
            try:
                return self.price_df[tf].iloc[start:end:step]
            except IndexError:
                pass
        return None

#------------------------------------------- Sorting ----------------------------------------------
    def sort_ascending(self, tf='D'):
        if tf == 'D':
            if self._symbol_df_ is not None and 'date' in self._symbol_df_.columns:
                self._symbol_df_ = self._symbol_df_.sort_values(['date'], ascending=True)
        elif tf == 'W':
            if self._weekly_df_ is not None and 'date' in self._weekly_df_.columns:
                self._weekly_df_ = self._weekly_df_.sort_values(['date'], ascending=True)
        elif tf == 'M':
            if self._monthly_df_ is not None and 'date' in self._monthly_df_.columns:
                self._monthly_df_ = self._monthly_df_.sort_values(['date'], ascending=True)
        return self
    
    def sort_descending(self, tf='D'):
        if tf == 'D':
            if self._symbol_df_ is not None and 'date' in self._symbol_df_.columns:
                self._symbol_df_ = self._symbol_df_.sort_values(['date'], ascending=False)
        elif tf == 'W':
            if self._weekly_df_ is not None and 'date' in self._weekly_df_.columns:
                self._weekly_df_ = self._weekly_df_.sort_values(['date'], ascending=False)
        elif tf == 'M':
            if self._monthly_df_ is not None and 'date' in self._monthly_df_.columns:
                self._monthly_df_ = self._monthly_df_.sort_values(['date'], ascending=False)
        return self
    
#-------------------------------------------- cell -----------------------------------------------
    
    def inter_day_value(self, mode='c', idx=-1, tf='D'):
        if (self.price_df[tf] is None) or (idx < -len(self.price_df[tf])) or  (idx > len(self.price_df[tf])):
            return None
        
        try:
            rec = self.price_df[tf].iloc[idx]
            if str(mode).replace('-', '').replace('.', '').isnumeric():
                t = mode
            elif mode == 'c':
                t = rec['close']
            elif mode == 'h':
                t = rec['high']
            elif mode == 'l':
                t = rec['low']
            elif mode == 'o':
                t = rec['open']
            elif mode == 'v':
                t = rec['volume']
            else:
                t = rec[mode]
            return t      
        except IndexError:
            print("Error: Access to symbol=" ,self._symbol_name_, " idx=", idx)
            return None
        except KeyError:
             print("Error: Access to symbol=" ,self._symbol_name_, " column=", mode)
             return None
  
    def candle_value(self, mode='c', idx=-1, tf='D'):
        return self.inter_day_value(mode, idx, tf)

#------------------------------------------------------ has condition ------------------------------------------------
    def has_condition(self, tf, ind, offset, cnd):
        if self.get_df(tf) is None:
            return False
        ind = self.get_indicator(ind,tf)
        return ind.has_condition(cnd=cnd,offset= offset,prev_days=1) if ind else False

    def has_all_conditions(self, tf, ind, offset, cnds):
        if self.get_df(tf) is None:
            return False
        ind = self.get_indicator(ind,tf)
        return ind.has_all_conditions(cnds=cnds,offset= offset,prev_days=1) if ind else False

    def has_any_condition(self, tf, ind, offset, cnds):
        if self.get_df(tf) is None:
            return False
        ind = self.get_indicator(ind,tf)
        return ind.has_any_conditions(cnds=cnds,offset= offset,prev_days=1) if ind else False

    def has_all_ind_conditions(self, tf, offset, cnd_dic):
        if self.get_df(tf) is None:
            return False
        for ind,cnd in cnd_dic.items():
            if not self.has_condition(tf, ind, offset,cnd): return False
        return True

    def has_any_ind_condition(self, tf, offset, cnd_dic):
        if self.get_df(tf) is None:
            return False
        for ind,cnd in cnd_dic.items():
            if self.has_condition(tf, ind, offset,cnd): return True
        return False

    def indicator_method(self,tf, ind, method_name, **argv):
        if self.get_df(tf) is None:
            return None
        ind = self.get_indicator(ind,tf)
        return getattr(ind, method_name)(**argv) if ind else None
