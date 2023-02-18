import datetime
import re
from symbol import Symbol

import pandas as pd
import tabloo
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import globals
from chart import SymbolChart
from dftable import DataFrameTable
import market_view
from market_view import MarketView
import market_model
from market_model import Market
from market_control import MarketControl
from filter import Filter

class MarketWatch(MarketControl):
   
    def get_symbol_names(self):
        return list(self._tablo['symbol'])

    def get_symbol_list(self):
        return list(self._tablo['symlink'])

    def __init__(self, symbol_names = [], by='', tf ='D',offset = -1,date='', in_groups=[], except_groups=[59,68,69],in_markets=[],except_markets=[], watch_name = ''):
        super().__init__( by=by, tf =tf,offset = offset, date=date)
        self._orig_symbol_names = symbol_names
        self._watch_name = 'DEFAULT_WATCH' if watch_name == '' else watch_name
        self._filter = self.filter()

        # ---------- new view, model ------------
        self._watch = MarketControl.watches[self._watch_name] 
        self._view = self._watch.view()
        self._model = self._watch.model(self._orig_symbol_names, self._by, self._tf,offset, self._date,in_groups, except_groups,in_markets,except_markets)
        # ---------- set tablo , tabloview ------------
        self._origin_tablo = self._tablo = self._model.tablo
        self.apply_filter()
        self._tabloview = self._view._map_columns(self._tablo)

    def filter(self, tf=''):
        return Filter(mw=self,tf=tf)

    def apply_filter(self):
        pass

        #---------------------------------------- atr ---------------------------------------
        # self._filter.filter_by_strategy('ATR_CROSSING_ABOVE_ATRSMA5')

        #---------------------------------------- adx ---------------------------------------
        # self._filter.filter_by_strategy('ADX_VERY_STRONG_BUY_SIGNAL')
        # self._filter.filter_by_strategy('ADXNEG_CROSSING_ABOVE_ADXPOS')
        # self._filter.adx().has_condition('ADX',cnd='STRONG_SELL_SIGNAL').select().output(tinyframes=True,plot_list=['plot_ichi','plot_adx'])
        # self._filter.adx().has_condition('ADX',cnd='ADXNEG_CROSSING_ABOVE_ADXPOS_ADX_DESCENDING').select().output(tinyframes=True,plot_list=['plot_ichi','plot_adx'])
        # self._filter.adx().has_condition('ADX',cnd='ADX_CROSSING_ABOVE_ADXPOS_ABOVE_ADXNEG').select().output(tinyframes=True,plot_list=['plot_ichi','plot_adx'])
        # self._filter.adx().has_condition('ADX',cnd='MILDLY_STRONG_BUY_SIGNAL').select().output(tinyframes=True,plot_list=['plot_ichi','plot_adx'])
        # self._filter.adx().has_condition('ADX',cnd='MILDLY_STRONG_SELL_SIGNAL').select().output(tinyframes=True,plot_list=['plot_ichi','plot_adx'])
        # self._filter.adx().has_condition('ADX',cnd='VERY_STRONG_BUY_SIGNAL').select().output(tinyframes=True,plot_list=['plot_ichi','plot_adx'])
        # self._filter.adx().has_condition('ADX',cnd='VERY_STRONG_SELL_SIGNAL').select().output(tinyframes=True,plot_list=['plot_ichi','plot_adx'])

        #---------------------------------------- bb ---------------------------------------
        # self._filter.filter_by_strategy('BB18_PRICE_CROSSING_ABOVE_LBAND')
        # self._filter.filter_by_strategy('BB200_PRICE_CROSSING_ABOVE_HBAND')
        # self._filter.by_strategy('BB200_PRICE_CROSSING_ABOVE_L1236').select().output(tinyframes=True,plot_list=['plot_bb_in_bb','plot_bb_with_levels' ,'plot_ichi'])
        # self._filter.by_strategy('BB200_PRICE_CROSSING_ABOVE_MAVG').select()
        # .export()

        #---------------------------------------- divergence ---------------------------------------
        # self._filter.filter_by_strategy('PRICE_VOLUME_DIVERGENCE')

        #---------------------------------------- ema  ---------------------------------------
        # self._filter.filter_by_strategy('PRICE_CLOSING_EMA34')

        #---------------------------------------- ichi ---------------------------------------
                                    #----------- tenkan , kijun ----------
        # self._filter.filter_by_strategy('TENKANSEN_CROSSING_PERPENDICULAR_ABOVE_KIJUNSEN')
        # self._filter.filter_by_strategy('PRICE_CROSSING_ABOVE_KIJUNSEN')
        # self._filter.filter_by_strategy('PRICE_CROSSING_ABOVE_TENKANSEN')
        # self._filter.filter_by_strategy('PRICE_CROSSING_ABOVE_TENKANSEN_AND_KIJUNSEN')
        # self._filter.filter_by_strategy('PRICE_CROSSING_ABOVE_TENKANSEN_ABOVE_KIJUNSEN')
        # self._filter.filter_by_strategy('TENKANSEN_CROSSING_ABOVE_KIJUNSEN_ABOVE_KIKO1')
        # self._filter.filter_by_strategy('TENKANSEN_MATCHING_KIJUNSEN_ASCENDING')

                                    #------------- kiko ----------------
        # self._filter.filter_by_strategy('KIJUNSEN_MATCHING_KIKO1')
        # self._filter.filter_by_strategy('TENKANSEN_CROSSING_ABOVE_KIKO1')
        # self._filter.filter_by_strategy('KIJUNSEN_CROSSING_ABOVE_KIKO1')
        # self._filter.filter_by_strategy('PRICE_CROSSING_ABOVE_KIKO1')
        # self._filter.filter_by_strategy('PRICE_CROSSING_ABOVE_KIKO2')
        # self._filter.filter_by_strategy('KIKO1_CROSSING_ABOVE_KIKO2')
        # self._filter.filter_by_strategy('KIKO1_CROSSING_BELOW_KIKO2')

                                    #------------- chikou ----------------
        # self._filter.filter_by_strategy('CHIKOU_CROSSING_ABOVE_KIJUNSEN_AND_PRICE_ABOVE_KUMO')
        # self._filter.filter_by_strategy('CHIKOU_CROSSING_ABOVE_PRICE')
        # self._filter.filter_by_strategy('CHIKOU_CROSSING_ABOVE_KIJUNSEN')
        # self._filter.filter_by_strategy('CHIKOU_CROSSING_ABOVE_KIKO1')
        # self._filter.filter_by_strategy('CHIKOU_CROSSING_ABOVE_KIKO2')

                                    #------------- kumo ----------------
        # self._filter.filter_by_strategy('FUTURE_KUMO_SWITCHING_ASCENDING')
        # self._filter.filter_by_strategy('PRICE_CLOSING_SPANB')
        # self._filter.filter_by_strategy('CHIKOU_CROSSING_ABOVE_KIJUNSEN_ABOVE_KUMO')
        # self._filter.filter_by_strategy('ICHI_GOLDEN_SIGNAL')

        #---------------------------------------- macd ---------------------------------------
        # self._filter.filter_by_strategy('MACD_CROSSING_NEG_TO_POS')
        # self._filter.filter_by_strategy('MACD_NEG_TO_POS')

        #---------------------------------------- mmid ---------------------------------------
        # self._filter.filter_by_strategy('PRICE_CLOSING_MMID416')

        #---------------------------------------- rsi ---------------------------------------
        # self._filter.filter_by_strategy('RSI_ESCAPING_OVERSOLD')
        # self._filter.filter_by_strategy('RSI_ESCAPING_OVERBOUGHT')
        # self._filter.filter_by_strategy('RSI_IN_OVERSOLD')
        # self._filter.filter_by_strategy('RSI_IN_OVERBOUGHT')
        # self._filter.filter_by_strategy('RSI_ASCENDING')
        # self._filter.filter_by_strategy('RSI_DESCENDING')
        # self._filter.filter_by_strategy('RSI_CROSSING_ABOVE_RSISMA5')
        # self._filter.filter_by_strategy('RSI_CHANGING_TO_ASCENDING')
        # self._filter.filter_by_strategy('RSI_CHANGING_TO_DESCENDING')

        #---------------------------------------- stoch ---------------------------------------
        # self._filter.by_strategy('STOCH_CROSSING_POS_IN_OVERSOLD').select().output(tinyframes=True, plot_list=['plot_stoch','plot_ichi'])
        # self._filter.by_strategy('STOCH_CROSSING_POS_IN_LOWERHALF').select().output(tinyframes=True, plot_list=['plot_stoch','plot_ichi'])
        # self._filter.by_strategy('STOCH_ESCAPING_OVERSOLD').select().output(tinyframes=True, plot_list=['plot_stoch','plot_ichi'])

        #---------------------------------------- tableau ---------------------------------------
        # self._filter.filter_by_strategy('CORP_BUY_17D_ABOVE_5PERCENT')
        # self._filter.by_strategy('VOL_1D_ABOVE_MONTH').select().output(tinyframes=True,plot_list=['plot_1to30_volume','plot_ichi','plot_volume'])
        # self._filter.filter_by_strategy('INDBUYCAPITA_ABOVE_MONTH')
        # self._filter.filter_by_strategy('CLOSE_PERCENT_BELOW_2')
        # self._filter.filter_by_strategy('ADJCLOSE_PERCENT_BELOW_2')
        # self._filter.filter_by_strategy('ADJCLOSE_PERCENT_ABOVE_2')
        # self._filter.filter_by_strategy('ASCENDING_TICK' )
        # self._filter.filter_by_strategy('DESCENDING_TICK')
        # self._filter.by_strategy('CORP_OWNERSHIP_CHANGE_POS_IN9D').select().output(tinyframes=True,plot_list=['plot_corp_ownership_change','plot_ichi'])
        # self._filter.by_strategy('IND_OWNERSHIP_CHANGE_POS_IN9D' ).select().output(tinyframes=True,plot_list=['plot_ind_ownership_change','plot_ichi'],secy_list=[True,False])
        # self._filter.filter_by_strategy('IND_BUYCAPITA_ABOVE_100000000')


        #---------------------------------------- ma cross ---------------------------------------
        # self._filter.by_strategy('SMA18_ABOVE_SMA54').select().output(tinyframes=True,plot_list=['plot_rainbow_ema','plot_ichi','plot_bb_in_bb'])
        # self._filter.by_strategy('EMA2_CROSSING_BELOW_EMA5').select().output(tinyframes=True,plot_list=['plot_rainbow_ema','plot_ichi','plot_bb_in_bb'])
        # self._filter.by_strategy('EMA2_CROSSING_ABOVE_EMA3').select().output(tinyframes=True,plot_list=['plot_rainbow_ema','plot_ichi','plot_bb_in_bb'])
        # self._filter.by_strategy('EMA2_CROSSING_ABOVE_EMA5').select().output(tinyframes=True,plot_list=['plot_rainbow_ema','plot_ichi','plot_bb_in_bb'])


        #---------------------------------------- combination ---------------------------------------
        # ---- bb - rsi ----
        # self._filter.filter_by_strategy('RSI_OVERSOLD_BB18_LBAND')
        
        # ---- capita - rsi ----
        # self._filter.filter_by_strategy('RSI_OVERSOLD_INDBUYCAPTIA_ABOVE_MONTH')

        # ---- power - rsi ----
        # self._filter.filter_by_strategy('RSI_OVERSOLD_INDBUYERPOWER')

        # ---- power - stoch ----
        # self._filter.filter_by_strategy('STOCh_OVERSOLD_INDBUYERPOWER')

        #---- power - volume ----
        # self._filter.filter_by_strategy('VOL_ABOVE_MONTH_INDBUYERPOWER')


    def show_charts(self, tinyframes = False, cols=0, plot_list=['plot_ichi'],secy_list=[], all_charts= False):
        # print(self._tablo.loc[:, self._tablo.columns != 'symlink'])
        df = self._tablo
        symbol_list = self.get_symbol_list()
        print(df)

        if (df is not None and len(df) > 0):
            candle_n = 150 if self._tf == 'D' else 100
            if len(df) < 100 and all_charts:
                SymbolChart.show_charts_for_symbols(symbol_list, tf=self._tf, last_n=candle_n, future_n=26,indicators=all_charts, volumes=all_charts,buys=False)
            if tinyframes:
                SymbolChart.show_tinyframes_for_symbols(symbols=symbol_list,cols=cols, tf=self._tf, last_n=candle_n, future_n=26,plot_list = plot_list,secy_list=secy_list)
            
        return self

    def export_charts(self, tinyframes = True, all_charts= False):
        df = self._tablo
        symbol_list = self._model.get_symbol_list()
        if (df is not None):
            if len(df) < 100 :
                candle_n = 150 if self._tf == 'D' else 100
                SymbolChart.export_charts_for_symbols(symbol_list, tf=self._tf, last_n=candle_n, future_n=26,indicators=all_charts, volumes=all_charts,buys=False, tinyframe=tinyframes)
        return self
        
#--------------------- main ------------------------
if __name__ == "__main__":
    TIMEFRAME = 'D'
    by = 'realtime'
    
    mw = MarketWatch(tf=TIMEFRAME,by=by)
    
    # mw.show_charts(tinyframes=True,plot_list=['plot_bb_in_bb','plot_bb_with_levels' ,'plot_ichi'])
    mw.show_tablo()
    
    # mw._view.output(tinyframes=True, all_charts=False)

    # symbol_names = ['خودرو', 'وبملت', 'فولاد', 'فملی', 'پترول', 'خساپا', 'وتجارت', 'وبصادر', 'شبندر', 'برکت']
    # SymbolChart.fig_tinyframe(symbol_names=symbol_names,cols=2,method="plot_ichi", last_n=150, future_n=26, tf=TIMEFRAME).show()
    
    # chart = SymbolChart(symbol_name, last_n=200, future_n=26, tf=TIMEFRAME)
    # chart.show_plots(plot1="plot_ichi", plot2 = 'plot_rsi_ichi', plot3 = 'plot_macd_')

#--------------------- filter ------------------------

    #---------------------------------------- atr ---------------------------------------
    # mw.filter.filter_by_strategy('ATR_CROSSING_ABOVE_ATRSMA5')

    #---------------------------------------- adx ---------------------------------------
    # mw.filter.filter_by_strategy('ADX_VERY_STRONG_BUY_SIGNAL')
    # mw.filter.filter_by_strategy('ADXNEG_CROSSING_ABOVE_ADXPOS')
    # mw.filter.adx().has_condition('ADX',cnd='STRONG_SELL_SIGNAL').select().output(tinyframes=True,plot_list=['plot_ichi','plot_adx'])
    # mw.filter.adx().has_condition('ADX',cnd='ADXNEG_CROSSING_ABOVE_ADXPOS_ADX_DESCENDING').select().output(tinyframes=True,plot_list=['plot_ichi','plot_adx'])
    # mw.filter.adx().has_condition('ADX',cnd='ADX_CROSSING_ABOVE_ADXPOS_ABOVE_ADXNEG').select().output(tinyframes=True,plot_list=['plot_ichi','plot_adx'])
    # mw.filter.adx().has_condition('ADX',cnd='MILDLY_STRONG_BUY_SIGNAL').select().output(tinyframes=True,plot_list=['plot_ichi','plot_adx'])
    # mw.filter.adx().has_condition('ADX',cnd='MILDLY_STRONG_SELL_SIGNAL').select().output(tinyframes=True,plot_list=['plot_ichi','plot_adx'])
    # mw.filter.adx().has_condition('ADX',cnd='VERY_STRONG_BUY_SIGNAL').select().output(tinyframes=True,plot_list=['plot_ichi','plot_adx'])
    # mw.filter.adx().has_condition('ADX',cnd='VERY_STRONG_SELL_SIGNAL').select().output(tinyframes=True,plot_list=['plot_ichi','plot_adx'])

    #---------------------------------------- bb ---------------------------------------
    # mw.filter.filter_by_strategy('BB18_PRICE_CROSSING_ABOVE_LBAND')
    # mw.filter.filter_by_strategy('BB200_PRICE_CROSSING_ABOVE_HBAND')
    # mw.filter.by_strategy('BB200_PRICE_CROSSING_ABOVE_L1236').select().output(tinyframes=True,plot_list=['plot_bb_in_bb','plot_bb_with_levels' ,'plot_ichi'])
    # mw.filter.by_strategy('BB200_PRICE_CROSSING_ABOVE_MAVG').select().output(tinyframes=True,plot_list=['plot_bb_in_bb','plot_bb_with_levels' ,'plot_ichi'])
    # .export()

    #---------------------------------------- divergence ---------------------------------------
    # mw.filter.filter_by_strategy('PRICE_VOLUME_DIVERGENCE')

    #---------------------------------------- ema  ---------------------------------------
    # mw.filter.filter_by_strategy('PRICE_CLOSING_EMA34')

    #---------------------------------------- ichi ---------------------------------------
                                #----------- tenkan , kijun ----------
    # mw.filter.filter_by_strategy('TENKANSEN_CROSSING_PERPENDICULAR_ABOVE_KIJUNSEN')
    # mw.filter.filter_by_strategy('PRICE_CROSSING_ABOVE_KIJUNSEN')
    # mw.filter.filter_by_strategy('PRICE_CROSSING_ABOVE_TENKANSEN')
    # mw.filter.filter_by_strategy('PRICE_CROSSING_ABOVE_TENKANSEN_AND_KIJUNSEN')
    # mw.filter.filter_by_strategy('PRICE_CROSSING_ABOVE_TENKANSEN_ABOVE_KIJUNSEN')
    # mw.filter.filter_by_strategy('TENKANSEN_CROSSING_ABOVE_KIJUNSEN_ABOVE_KIKO1')
    # mw.filter.filter_by_strategy('TENKANSEN_MATCHING_KIJUNSEN_ASCENDING')

                                #------------- kiko ----------------
    # mw.filter.filter_by_strategy('KIJUNSEN_MATCHING_KIKO1')
    # mw.filter.filter_by_strategy('TENKANSEN_CROSSING_ABOVE_KIKO1')
    # mw.filter.filter_by_strategy('KIJUNSEN_CROSSING_ABOVE_KIKO1')
    # mw.filter.filter_by_strategy('PRICE_CROSSING_ABOVE_KIKO1')
    # mw.filter.filter_by_strategy('PRICE_CROSSING_ABOVE_KIKO2')
    # mw.filter.filter_by_strategy('KIKO1_CROSSING_ABOVE_KIKO2')
    # mw.filter.filter_by_strategy('KIKO1_CROSSING_BELOW_KIKO2')

                                #------------- chikou ----------------
    # mw.filter.filter_by_strategy('CHIKOU_CROSSING_ABOVE_KIJUNSEN_AND_PRICE_ABOVE_KUMO')
    # mw.filter.filter_by_strategy('CHIKOU_CROSSING_ABOVE_PRICE')
    # mw.filter.filter_by_strategy('CHIKOU_CROSSING_ABOVE_KIJUNSEN')
    # mw.filter.filter_by_strategy('CHIKOU_CROSSING_ABOVE_KIKO1')
    # mw.filter.filter_by_strategy('CHIKOU_CROSSING_ABOVE_KIKO2')

                                #------------- kumo ----------------
    # mw.filter.filter_by_strategy('FUTURE_KUMO_SWITCHING_ASCENDING')
    # mw.filter.filter_by_strategy('PRICE_CLOSING_SPANB')
    # mw.filter.filter_by_strategy('CHIKOU_CROSSING_ABOVE_KIJUNSEN_ABOVE_KUMO')
    # mw.filter.filter_by_strategy('ICHI_GOLDEN_SIGNAL')

    #---------------------------------------- macd ---------------------------------------
    # mw.filter.filter_by_strategy('MACD_CROSSING_NEG_TO_POS')
    # mw.filter.filter_by_strategy('MACD_NEG_TO_POS')

    #---------------------------------------- mmid ---------------------------------------
    # mw.filter.filter_by_strategy('PRICE_CLOSING_MMID416')

    #---------------------------------------- rsi ---------------------------------------
    # mw.filter.filter_by_strategy('RSI_ESCAPING_OVERSOLD')
    # mw.filter.filter_by_strategy('RSI_ESCAPING_OVERBOUGHT')
    # mw.filter.filter_by_strategy('RSI_IN_OVERSOLD')
    # mw.filter.filter_by_strategy('RSI_IN_OVERBOUGHT')
    # mw.filter.filter_by_strategy('RSI_ASCENDING')
    # mw.filter.filter_by_strategy('RSI_DESCENDING')
    # mw.filter.filter_by_strategy('RSI_CROSSING_ABOVE_RSISMA5')
    # mw.filter.filter_by_strategy('RSI_CHANGING_TO_ASCENDING')
    # mw.filter.filter_by_strategy('RSI_CHANGING_TO_DESCENDING')

    #---------------------------------------- stoch ---------------------------------------
    # mw.filter.by_strategy('STOCH_CROSSING_POS_IN_OVERSOLD').select().output(tinyframes=True, plot_list=['plot_stoch','plot_ichi'])
    # mw.filter.by_strategy('STOCH_CROSSING_POS_IN_LOWERHALF').select().output(tinyframes=True, plot_list=['plot_stoch','plot_ichi'])
    # mw.filter.by_strategy('STOCH_ESCAPING_OVERSOLD').select().output(tinyframes=True, plot_list=['plot_stoch','plot_ichi'])

    #---------------------------------------- tableau ---------------------------------------
    # mw.filter.filter_by_strategy('CORP_BUY_17D_ABOVE_5PERCENT')
    # mw.filter.by_strategy('VOL_1D_ABOVE_MONTH').select().output(tinyframes=True,plot_list=['plot_1to30_volume','plot_ichi','plot_volume'])
    # mw.filter.filter_by_strategy('INDBUYCAPITA_ABOVE_MONTH')
    # mw.filter.filter_by_strategy('CLOSE_PERCENT_BELOW_2')
    # mw.filter.filter_by_strategy('ADJCLOSE_PERCENT_BELOW_2')
    # mw.filter.filter_by_strategy('ADJCLOSE_PERCENT_ABOVE_2')
    # mw.filter.filter_by_strategy('ASCENDING_TICK' )
    # mw.filter.filter_by_strategy('DESCENDING_TICK')
    # mw.filter.by_strategy('CORP_OWNERSHIP_CHANGE_POS_IN9D').select().output(tinyframes=True,plot_list=['plot_corp_ownership_change','plot_ichi'])
    # mw.filter.by_strategy('IND_OWNERSHIP_CHANGE_POS_IN9D' ).select().output(tinyframes=True,plot_list=['plot_ind_ownership_change','plot_ichi'],secy_list=[True,False])
    # mw.filter.filter_by_strategy('IND_BUYCAPITA_ABOVE_100000000')


    #---------------------------------------- ma cross ---------------------------------------
    # mw.filter.by_strategy('SMA18_ABOVE_SMA54').select().output(tinyframes=True,plot_list=['plot_rainbow_ema','plot_ichi','plot_bb_in_bb'])
    # mw.filter.by_strategy('EMA2_CROSSING_BELOW_EMA5').select().output(tinyframes=True,plot_list=['plot_rainbow_ema','plot_ichi','plot_bb_in_bb'])
    # mw.filter.by_strategy('EMA2_CROSSING_ABOVE_EMA3').select().output(tinyframes=True,plot_list=['plot_rainbow_ema','plot_ichi','plot_bb_in_bb'])
    # mw.filter.by_strategy('EMA2_CROSSING_ABOVE_EMA5').select().output(tinyframes=True,plot_list=['plot_rainbow_ema','plot_ichi','plot_bb_in_bb'])


    #---------------------------------------- combination ---------------------------------------
    # ---- bb - rsi ----
    # mw.filter.filter_by_strategy('RSI_OVERSOLD_BB18_LBAND')
    
    # ---- capita - rsi ----
    # mw.filter.filter_by_strategy('RSI_OVERSOLD_INDBUYCAPTIA_ABOVE_MONTH')

    # ---- power - rsi ----
    # mw.filter.filter_by_strategy('RSI_OVERSOLD_INDBUYERPOWER')

    # ---- power - stoch ----
    # mw.filter.filter_by_strategy('STOCh_OVERSOLD_INDBUYERPOWER')

    #---- power - volume ----
    # mw.filter.filter_by_strategy('VOL_ABOVE_MONTH_INDBUYERPOWER')






    #---------------------------------------- test agg ---------------------------------------
    # Market(tf=TIMEFRAME).in_groups([34]).avg(label='VOL_AVG',n=30).select(ColumnsMap.all).output()
    # Market(tf=TIMEFRAME).avg(label='VOL_AVG',n=30).select(ColumnsMap.all).output()

    #---------------------------------------- test query ---------------------------------------
    # Market(tf=TIMEFRAME).except_groups([59,68,69]).groupby('sector_code').mean().output()

    # Market(tf=TIMEFRAME).in_groups([34]).output(tinyframes=True).export()
    # a = Market(tf=TIMEFRAME).query('sector_code == 34').output()
    # print (len(a.symbol_list))

    # Market(tf=TIMEFRAME).in_groups([34]).select(ColumnsMap.regular).output()
    # Market(tf=TIMEFRAME).in_groups([34]).rsi().on_row(-1).has_condition(ind='RSI',cnd='ESCAPING_OVERSOLD').select(ColumnsMap.regular).output()
    
    # new_lst = [s for s in symbol_lst if s.indicators['D']['RSI'].is_escaping_oversold()]
    # print(trendline.symbol_list_to_df(new_lst))
    # for s in symbol_lst:
    #      print(s.get_name(), s.indicators['D'])
    # Market(new_lst).output()

