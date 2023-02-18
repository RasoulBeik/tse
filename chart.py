from os import name
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff

from kaleido.scopes.plotly import PlotlyScope
import pandas as pd
import numpy as np
from symbol import Symbol
import indicator
# from indicator import * 
import math
import globals
import plotly.io as pio

class SymbolChart:
    plots : dict= {
        'plot_ind_buy_capita': {'func': lambda self :self.plot_ind_buy_capita(), 'secy':False }
        ,'plot_ind_sell_capita': {'func': lambda self :self.plot_ind_sell_capita(), 'secy':False }
        ,'plot_ind_trade_capita': {'func': lambda self :self.plot_ind_trade_capita(), 'secy':False }
        ,'plot_corp_buy_capita': {'func': lambda self :self.plot_corp_buy_capita(), 'secy':False }
        ,'plot_ind_buyers_power': {'func': lambda self :self.plot_ind_buyers_power(), 'secy':False }
        ,'plot_trades_value': {'func': lambda self :self.plot_trades_value(), 'secy':False }
        ,'plot_ind_ownership_change': {'func': lambda self :self.plot_ind_ownership_change(), 'secy':True }
        ,'plot_corp_ownership_change': {'func': lambda self :self.plot_corp_ownership_change(), 'secy':True }
        ,'plot_close': {'func': lambda self :self.plot_close(), 'secy':False }
        ,'plot_candlestick': {'func': lambda self :self.plot_candlestick(), 'secy':False }
        ,'plot_ichi': {'func': lambda self :self.plot_ichi(), 'secy':False }
    }

    tf_names = {'D': 'روزانه', 'W': 'هفتگی', 'M': 'ماهانه', 'm':'بین روز'}

    """
    last_n: number of prices of dataframe in charts. 0 means all prices.
    future_n: number of future prices in charts. it is specially used in ichimoko indicator.
    so real numbers of prices in each chart is: (last_n - future_n)
    the expression: last_n = self._last_n_ - self._future_n_ in plot_... methods aligns x axes of all charts.
    """

#-------------------------- __init__ ---------------------------------
    def __init__(self, symbol: Symbol, last_n=0, future_n=0, tf='D'):
        self._symbol = symbol
        self._last_n = last_n
        self._future_n = future_n
        self._tf = tf
        return
        
#-------------------------- capita ---------------------------------
    # سرانه خرید حقیقی
    def plot_ind_buy_capita(self):
        last_n = self._last_n - self._future_n
        tf = self._tf
        df = self._symbol.price_df[tf]
        ind_buy_capita = indicator.tableau.TABLEAU(symbol = self._symbol,tf = tf)._ind_buy_capita()
        text = df['date'][-last_n:]
        trace = go.Scatter(y=ind_buy_capita[-last_n:], text=text, mode='lines', name='سرانه خرید حقیقی')
        return [trace]

 # سرانه فروش حقیقی
    def plot_ind_sell_capita(self):
        last_n = self._last_n - self._future_n
        tf = self._tf
        df = self._symbol.price_df[tf]
        ind_sell_capita = indicator.tableau.TABLEAU(symbol = self._symbol,tf = tf)._ind_sell_capita()
        text = df['date'][-last_n:]
        trace = go.Scatter(y=ind_sell_capita[-last_n:], text=text, mode='lines', name='سرانه فروش حقیقی')
        return [trace]

    # سرانه معامله حقیقی
    def plot_ind_trade_capita(self):
        last_n = self._last_n - self._future_n
        tf = self._tf
        df = self._symbol.price_df[tf]
        ind_trade_capita = indicator.tableau.TABLEAU(symbol = self._symbol,tf = tf)._ind_trade_capita()
        text = df['date'][-last_n:]
        trace = go.Scatter(y=ind_trade_capita[-last_n:], text=text, mode='lines', name='سرانه معامله حقیقی')
        return [trace]

    # سرانه خرید حقوقی
    def plot_corp_buy_capita(self):
        last_n = self._last_n - self._future_n
        tf = self._tf
        df = self._symbol.price_df[tf]
        corporate_buy_capita = indicator.tableau.TABLEAU(symbol = self._symbol,tf = tf)._corp_buy_capita()
        text = df['date'][-last_n:]
        trace = go.Scatter(y=corporate_buy_capita[-last_n:], text=text, mode='lines', name='سرانه خرید حقوقی')
        return [trace]

    # سرانه فروش حقوقی
    def plot_corp_sell_capita(self):
        last_n = self._last_n - self._future_n
        tf = self._tf
        df = self._symbol.price_df[tf]
        corp_sell_capita = indicator.tableau.TABLEAU(symbol = self._symbol,tf = tf)._corp_sell_capita()
        text = df['date'][-last_n:]
        trace = go.Scatter(y=corp_sell_capita[-last_n:], text=text, mode='lines', name='سرانه فروش حقیقی')
        return [trace]

    # سرانه معامله حقوقی
    def plot_corp_trade_capita(self):
        last_n = self._last_n - self._future_n
        tf = self._tf
        df = self._symbol.price_df[tf]
        corp_trade_capita = indicator.tableau.TABLEAU(symbol = self._symbol,tf = tf)._corp_trade_capita()
        text = df['date'][-last_n:]
        trace = go.Scatter(y=corp_trade_capita[-last_n:], text=text, mode='lines', name='سرانه معامله حقیقی')
        return [trace]

    # قدرت خریداران حقیقی
    def plot_ind_buyers_power(self):
        last_n = self._last_n - self._future_n
        tf = self._tf
        df = self._symbol.price_df[tf]
        ind_buyers_power = indicator.tableau.TABLEAU(symbol = self._symbol,tf = tf)._ind_buyers_power()
        # individual_buy_capita = df['individual_buy_vol'] / df['individual_buy_count']
        # individual_sell_capita = df['individual_sell_vol'] / df['individual_sell_count']
        # individual_buyers_power = individual_buy_capita / individual_sell_capita
        text = df['date'][-last_n:]
        trace = go.Scatter(y=ind_buyers_power[-last_n:], text=text, mode='lines', name='قدرت خریداران حقیقی')
        return [trace]

#-------------------------- trade value ---------------------------------
    # ارزش معاملات
    def plot_trades_value(self):
        last_n = self._last_n - self._future_n
        tf = self._tf
        df = self._symbol.price_df[tf]
        trades_value = indicator.tableau.TABLEAU(symbol = self._symbol,tf = tf)._trade_value()
        # trades_value = df['volume'] * df['adjClose']
        text = df['date'][-last_n:]
        trace = go.Scatter(y=trades_value[-last_n:], text=text, mode='lines', name='ارزش معاملات')
        return [trace]

#-------------------------- money i/o ---------------------------------
    # ورود و خروج پول حقیقی
    def plot_ind_ownership_change(self):
        last_n = self._last_n - self._future_n
        tf = self._tf
        df = self._symbol.price_df[tf]
        individual_money = indicator.tableau.TABLEAU(symbol = self._symbol, tf = tf)._ind_ownership_change()
        text = df['date'][-last_n:]
        trace1 = go.Bar(y=individual_money[-last_n:], text=text, name='ورود و خروج پول حقیقی', marker_color='#000099')
        trace2 = go.Scatter(y=df['adjClose'][-last_n:], text=text, mode='lines', line={'color':'#770044', 'width':3}, name='قیمت پایانی')
        return [trace1, trace2]

    # ورود و خروج پول حقوقی
    def plot_corp_ownership_change(self):
        last_n = self._last_n - self._future_n
        tf = self._tf
        df = self._symbol.price_df[tf]
        corporate_money = indicator.tableau.TABLEAU(symbol = self._symbol, tf = tf)._corp_ownership_change() 
        text = df['date'][-last_n:]
        trace1 = go.Bar(y=corporate_money[-last_n:], text=text, name='ورود و خروج پول حقوقی', marker_color='#000099')
        trace2 = go.Scatter(y=df['adjClose'][-last_n:], text=text, mode='lines', line={'color':'#770044', 'width':1}, name='قیمت پایانی')
        return [trace1, trace2]

#-------------------------- price ---------------------------------
    def plot_close(self):
        last_n = self._last_n - self._future_n
        tf = self._tf
        text = self._symbol.column_values('date',tf = tf)[-last_n:]
        column = self._symbol.column_values('c',tf = tf)
        trace = go.Scatter(y=column[-last_n:], text=text, mode='lines', line={'color':'#770044', 'width':3}, name='قیمت پایانی')
        return [trace]

    def plot_candlestick(self, mode_o='open', mode_l='low', mode_h='high', mode='close'):
        last_n = self._last_n - self._future_n

        txt = self._symbol.column_values(mode='date',tf=self._tf)[-last_n:]
        op = self._symbol.column_values(mode=mode_o,tf=self._tf)[-last_n:]
        hi = self._symbol.column_values(mode=mode_h,tf=self._tf)[-last_n:]
        lo = self._symbol.column_values(mode=mode_l,tf=self._tf)[-last_n:]
        close = self._symbol.column_values(mode=mode,tf=self._tf)[-last_n:]
        
        trace = go.Candlestick(open=op, high=hi,low=lo, close=close, text=txt, name='کندل')
        return [trace]                        

#-------------------------- ichi ---------------------------------
    def plot_ichi(self,mode_o= 'o', mode_l = 'l', mode_h = 'h', mode='c', draw_mode = 'candlestick'):
        last_n = self._last_n - self._future_n
        tf = self._tf
        df = self._symbol.price_df[tf]
        text = df['date'][-last_n:]
       
        if draw_mode == 'candlestick':
            trace = self.plot_candlestick()
        elif draw_mode == 'linechart':
            trace = self.plot_column(mode=mode)

        # if future_n is 0, ichimoko will not show.
        if self._future_n < 0:
            return trace
        ichi_last_n = self._last_n
        ten, kij, spana, spanb, chikou , kiko1 , kiko2 = \
            indicator.ichimoku.ICHI(symbol=self._symbol,mode_l=mode_l, mode_h=mode_h, mode= mode, as_standard=True, tf=tf).ichi()
        chikou = chikou.apply(lambda x: np.nan if x == 0 else x)

        # there are no future prices for tenkensen and kijunsen, so they are displayed as candle chart.
        trace_ten = go.Scatter(y=ten[-last_n:], text=text, line={'color':'red', 'width':2}, name='tenknsen')
        trace_kij = go.Scatter(y=kij[-last_n:], text=text, line={'color':'blue', 'width':2}, name='kijunsen')
        trace_chikou = go.Scatter(y=chikou[-last_n:], text=text, line={'color':'green', 'width':4}, name='chikouspan')

        # spana and spanb have future prices (future_n like 26), so they have extra prices in their charts.
        trace_spana = go.Scatter(y=spana[-ichi_last_n:], text=text, line={'color':'green', 'width':2}, name='spana')
        trace_spanb = go.Scatter(y=spanb[-ichi_last_n:], text=text, fill='tonexty',
                                    line={'color':'brown', 'width':2}, name='spanb')
        trace_kiko1 = go.Scatter(y=kiko1[-last_n:], text=text, line={'color':'brown', 'width':2}, name='kiko1')
        trace_kiko2 = go.Scatter(y=kiko2[-last_n:], text=text, line={'color':'navy', 'width':2}, name='kiko2')
        return trace + [trace_ten, trace_kij, trace_chikou, trace_spana, trace_spanb, trace_kiko1, trace_kiko2]

#-------------------------- ma ---------------------------------
    def plot_rainbow_ema(self, mode ='c', draw_mode = 'candlestick'):
        last_n = self._last_n - self._future_n
        tf = self._tf
        df = self._symbol.price_df[tf]
        text = df['date'][-last_n:]
        
        if draw_mode == 'candlestick':
            trace = self.plot_candlestick()
        elif draw_mode == 'linechart':
            trace = self.plot_column(mode=mode)

        ema2 = indicator.ema.EMA(symbol=self._symbol,n=2,mode=mode,tf=tf).ema()
        ema5 = indicator.ema.EMA(symbol=self._symbol,n=5,mode=mode,tf=tf).ema()
        ema13 = indicator.ema.EMA(symbol=self._symbol,n=13,mode=mode,tf=tf).ema()
        ema21 = indicator.ema.EMA(symbol=self._symbol,n=21,mode=mode,tf=tf).ema()
        ema34 = indicator.ema.EMA(symbol=self._symbol,n=34,mode=mode,tf=tf).ema()
        ema55 = indicator.ema.EMA(symbol=self._symbol,n=55,mode=mode,tf=tf).ema()
        ema89 = indicator.ema.EMA(symbol=self._symbol,n=89,mode=mode,tf=tf).ema()
        ema144 = indicator.ema.EMA(symbol=self._symbol,n=144,mode=mode,tf=tf).ema()
        ema233 = indicator.ema.EMA(symbol=self._symbol,n=233,mode=mode,tf=tf).ema()
        ema377 = indicator.ema.EMA(symbol=self._symbol,n=377,mode=mode,tf=tf).ema()
        ema610 = indicator.ema.EMA(symbol=self._symbol,n=610,mode=mode,tf=tf).ema()
        ema987 = indicator.ema.EMA(symbol=self._symbol,n=987,mode=mode,tf=tf).ema()
        ema1597 = indicator.ema.EMA(symbol=self._symbol,n=1597,mode=mode,tf=tf).ema()

        trace_ema2 = go.Scatter(y=ema2[-last_n:], text=text, mode='lines', line={'color':'red', 'width':2}, name='ema2')
        trace_ema5 = go.Scatter(y=ema5[-last_n:], text=text, mode='lines', line={'color':'orange', 'width':2}, name='ema5')
        trace_ema13 = go.Scatter(y=ema13[-last_n:], text=text, mode='lines', line={'color':'blue', 'width':2}, name='ema13')
        trace_ema21 = go.Scatter(y=ema21[-last_n:], text=text, mode='lines', line={'color':'lightgreen', 'width':2}, name='ema21')
        trace_ema34 = go.Scatter(y=ema34[-last_n:], text=text, mode='lines', line={'color':'violet', 'width':2}, name='ema34')
        trace_ema55 = go.Scatter(y=ema55[-last_n:], text=text, mode='lines', line={'color':'yellow', 'width':2}, name='ema55')
        trace_ema89 = go.Scatter(y=ema89[-last_n:], text=text, mode='lines', line={'color':'green', 'width':2}, name='ema89')
        trace_ema144 = go.Scatter(y=ema144[-last_n:], text=text, mode='lines', line={'color':'orange', 'width':2}, name='ema144')
        trace_ema233 = go.Scatter(y=ema233[-last_n:], text=text, mode='lines', line={'color':'magenta', 'width':2}, name='ema233')
        trace_ema377 = go.Scatter(y=ema377[-last_n:], text=text, mode='lines', line={'color':'gray', 'width':2}, name='ema377')
        trace_ema610 = go.Scatter(y=ema610[-last_n:], text=text, mode='lines', line={'color':'red', 'width':3}, name='ema610')
        trace_ema987 = go.Scatter(y=ema987[-last_n:], text=text, mode='lines', line={'color':'lightgreen', 'width':3}, name='ema987')
        trace_ema1597 = go.Scatter(y=ema1597[-last_n:], text=text, mode='lines', line={'color':'purple', 'width':3}, name='ema1597')
        return trace + [trace_ema2,trace_ema5,trace_ema13,trace_ema21,trace_ema34,trace_ema55,trace_ema89,trace_ema144,trace_ema233,
        trace_ema377,trace_ema610,trace_ema987,trace_ema1597 ]

    def plot_sma_2_18_54(self, mode='c', draw_mode = 'candlestick'):
        last_n = self._last_n - self._future_n
        tf = self._tf
        df = self._symbol.price_df[tf]
        text = df['date'][-last_n:]
        
        if draw_mode == 'candlestick':
            trace = self.plot_candlestick()
        elif draw_mode == 'linechart':
            trace = self.plot_column(mode=mode)


        sma2 = indicator.sma.SMA(symbol=self._symbol,n=2,mode=mode,tf=tf).sma()
        # sma5 = indicator.sma.SMA(symbol=self._symbol,n=5,mode=mode,tf=tf).sma()
        sma9 = indicator.sma.SMA(symbol=self._symbol,n=9,mode=mode,tf=tf).sma()
        # ema13 = indicator.ema.EMA(symbol=self._symbol,n=13,mode=mode,tf=tf).ema()
        sma18 = indicator.ema.EMA(symbol=self._symbol,n=18,mode=mode,tf=tf).ema()
        sma27 = indicator.ema.EMA(symbol=self._symbol,n=27,mode=mode,tf=tf).ema()
        # ema34 = indicator.ema.EMA(symbol=self._symbol,n=34,mode=mode,tf=tf).ema()
        # ema49 = indicator.ema.EMA(symbol=self._symbol,n=49,mode=mode,tf=tf).ema()
        sma54 = indicator.sma.SMA(symbol=self._symbol,n=55,mode=mode,tf=tf).sma()
        sma108 = indicator.sma.SMA(symbol=self._symbol,n=108,mode=mode,tf=tf).sma()
        sma216 = indicator.sma.SMA(symbol=self._symbol,n=216,mode=mode,tf=tf).sma()
        sma324 = indicator.sma.SMA(symbol=self._symbol,n=324,mode=mode,tf=tf).sma()
        sma432 = indicator.sma.SMA(symbol=self._symbol,n=432,mode=mode,tf=tf).sma()

        trace_sma2 = go.Scatter(y=sma2[-last_n:], text=text, mode='lines', line={'color':'orange', 'width':2}, name='sma2')
        # trace_sma5 = go.Scatter(y=sma5[-last_n:], text=text, mode='lines', line={'color':'orange', 'width':2}, name='sma5')
        trace_sma9 = go.Scatter(y=sma9[-last_n:], text=text, mode='lines', line={'color':'red', 'width':2}, name='sma9')
        # trace_ema13 = go.Scatter(y=ema13[-last_n:], text=text, mode='lines', line={'color':'cyan', 'width':2}, name='ema13')
        trace_sma18 = go.Scatter(y=sma18[-last_n:], text=text, mode='lines', line={'color':'blue', 'width':2}, name='sma18')
        trace_sma27 = go.Scatter(y=sma18[-last_n:], text=text, mode='lines', line={'color':'purple', 'width':2}, name='sma27')
        # trace_ema34 = go.Scatter(y=ema34[-last_n:], text=text, mode='lines', line={'color':'violet', 'width':2}, name='ema34')
        # trace_ema49 = go.Scatter(y=ema49[-last_n:], text=text, mode='lines', line={'color':'gray', 'width':2}, name='ema49')
        trace_sma54 = go.Scatter(y=sma54[-last_n:], text=text, mode='lines', line={'color':'green', 'width':2}, name='sma54')
        trace_sma108 = go.Scatter(y=sma108[-last_n:], text=text, mode='lines', line={'color':'orange', 'width':4}, name='sma108')
        trace_sma216 = go.Scatter(y=sma216[-last_n:], text=text, mode='lines', line={'color':'magenta', 'width':4}, name='sma216')
        trace_sma324 = go.Scatter(y=sma324[-last_n:], text=text, mode='lines', line={'color':'gray', 'width':4}, name='sma324')
        trace_sma432 = go.Scatter(y=sma432[-last_n:], text=text, mode='lines', line={'color':'purple', 'width':4}, name='sma432')
        return trace + [trace_sma2,trace_sma9, trace_sma27,trace_sma54,trace_sma108,trace_sma216,trace_sma324,trace_sma432] 

#-------------------------- rsi ---------------------------------
    def plot_rsi(self, mode='c'):
        last_n = self._last_n - self._future_n
        tf = self._tf
        df = self._symbol.price_df[tf]
        trades_value = indicator.rsi.RSI(symbol = self._symbol,mode=mode, tf=tf).rsi()
        text = df['date'][-last_n:]
        trace1 = go.Scatter(y=trades_value[-last_n:], text=text, mode='lines', name='RSI')
        trace2 = go.Scatter(y=[30]*last_n, text=text, mode='lines', line={'color': '#505050', 'width': 1}, name='')
        trace3 = go.Scatter(y=[50]*last_n, text=text, mode='lines', line={'color': '#505050', 'width': 1}, name='')
        trace4 = go.Scatter(y=[70]*last_n, text=text, mode='lines', line={'color': '#505050', 'width': 1}, name='')
        return [trace1, trace2, trace3, trace4]

    def plot_rsi_ichi(self):
        last_n = self._last_n - self._future_n
        tf = self._tf
        df = self._symbol.price_df[tf]
        text = df['date'][-last_n:]
       
        rsi_values = indicator.rsi.RSI(symbol = self._symbol, tf=tf).rsi()
        trace = go.Scatter(y=rsi_values[-last_n:], text=text, mode='lines', line={'color':'navy', 'width':4}, name='RSI')

        if self._future_n < 0:
            return [trace]
        ichi_last_n = self._last_n
       
        ten, kij, spana, spanb, chikou , kiko1 , kiko2 = \
            indicator.ichimoku.ICHI.ichi_series(sr_c= rsi_values)
        chikou = chikou.apply(lambda x: np.nan if x == 0 else x)

        # there are no future prices for tenkensen and kijunsen, so they are displayed as candle chart.
        trace_ten = go.Scatter(y=ten[-last_n:], text=text, line={'color':'red', 'width':2}, name='tenknsen')
        trace_kij = go.Scatter(y=kij[-last_n:], text=text, line={'color':'blue', 'width':2}, name='kijunsen')
        trace_chikou = go.Scatter(y=chikou[-last_n:], text=text, line={'color':'green', 'width':4}, name='chikouspan')

        # spana and spanb have future prices (future_n like 26), so they have extra prices in their charts.
        trace_spana = go.Scatter(y=spana[-ichi_last_n:], text=text, line={'color':'green', 'width':2}, name='spana')
        trace_spanb = go.Scatter(y=spanb[-ichi_last_n:], text=text, fill='tonexty',
                                    line={'color':'brown', 'width':2}, name='spanb')
        trace_kiko1 = go.Scatter(y=kiko1[-last_n:], text=text, line={'color':'brown', 'width':2}, name='kiko1')
        trace_kiko2 = go.Scatter(y=kiko2[-last_n:], text=text, line={'color':'navy', 'width':2}, name='kiko2')
        return [trace , trace_ten, trace_kij, trace_chikou, trace_spana, trace_spanb, trace_kiko1, trace_kiko2]

#-------------------------- macd ---------------------------------
    def plot_macd(self,mode='c'):
        last_n = self._last_n - self._future_n
        tf = self._tf
        df = self._symbol.price_df[tf]
        # line, histogram, signal = indicator.macd.MACD(symbol = self._symbol_, add_column=False, as_standard=True, tf=tf)
        line, histogram, signal = indicator.macd.MACD(symbol = self._symbol,mode=mode,tf=tf,as_standard=True).macd()
        text = df['date'][-last_n:]
        trace1 = go.Bar(y=histogram[-last_n:], text=text, name='', marker_color='green')
        trace2 = go.Scatter(y=line[-last_n:], text=text, mode='lines', line={'color':'blue', 'width':3}, name='')
        trace3 = go.Scatter(y=signal[-last_n:], text=text, mode='lines', line={'color':'red', 'width':3}, name='Signal')
        trace4 = go.Scatter(y=[0]*last_n, text=text, mode='lines', line={'color': '#505050', 'width': 1}, name='')
        return [trace1, trace2, trace3, trace4]

    def plot_vol_macd(self):
        last_n = self._last_n - self._future_n
        tf = self._tf
        df = self._symbol.price_df[tf]
        # line, histogram, signal = indicator.macd.MACD(symbol = self._symbol_, add_column=False, as_standard=True, tf=tf)
        line, histogram, signal = indicator.macd.MACD(symbol = self._symbol,tf=tf,mode='v',as_standard=True).macd()
        text = df['date'][-last_n:]
        trace1 = go.Bar(y=histogram[-last_n:], text=text, name='', marker_color='green')
        trace2 = go.Scatter(y=line[-last_n:], text=text, mode='lines', line={'color':'blue', 'width':3}, name='')
        trace3 = go.Scatter(y=signal[-last_n:], text=text, mode='lines', line={'color':'red', 'width':3}, name='Signal')
        trace4 = go.Scatter(y=[0]*last_n, text=text, mode='lines', line={'color': '#505050', 'width': 1}, name='')
        return [trace1, trace2, trace3, trace4]

#-------------------------- bb ---------------------------------
    def plot_bb(self, mode='c', draw_mode='candlestick'):
        last_n = self._last_n - self._future_n
        tf = self._tf
        df = self._symbol.price_df[tf]
        if draw_mode == 'candlestick':
            trace = self.plot_candlestick()
        elif draw_mode == 'linechart':
            trace = self.plot_column(mode=mode)

        mavg,lband,hband,wband,pband = indicator.bolinger.BB(symbol = self._symbol, n=18,ndev= 2, mode=mode, as_standard=True, tf=tf)._bb()
        text = df['date'][-last_n:]
        trace1 = go.Scatter(y=mavg[-last_n:], text=text, mode='lines', line={'color':'magenta', 'width':3}, name='')
        trace2 = go.Scatter(y=lband[-last_n:], text=text, mode='lines', line={'color':'magenta', 'width':3}, name='Signal')
        trace3 = go.Scatter(y=hband[-last_n:], text=text, mode='lines', line={'color':'magenta', 'width':3}, name='Signal')
        return trace + [trace1, trace2, trace3]

    def plot_bb_in_bb(self, mode='c',draw_mode='candlestick'):
        last_n = self._last_n - self._future_n
        tf = self._tf
        df = self._symbol.price_df[tf]
        if draw_mode == 'candlestick':
            trace = self.plot_candlestick()
        elif draw_mode == 'linechart':
            trace = self.plot_column(mode=mode)

        mavg18,lband18,hband18,wband18,pband18 = indicator.bolinger.BB(symbol = self._symbol, n=18,ndev= 2,mode= mode, as_standard=True, tf=tf)._bb()
        mavg200,lband200,hband200,wband200,pband200 = indicator.bolinger.BB(symbol = self._symbol, n=200,ndev= 2,mode= mode, as_standard=True, tf=tf)._bb()
        text = df['date'][-last_n:]
        trace1 = go.Scatter(y=mavg18[-last_n:], text=text, mode='lines', line={'color':'blue', 'width':2}, name='')
        trace2 = go.Scatter(y=lband18[-last_n:], text=text, mode='lines', line={'color':'blue', 'width':2}, name='Signal')
        trace3 = go.Scatter(y=hband18[-last_n:], text=text, mode='lines', line={'color':'blue', 'width':2}, name='Signal')
        
        trace4 = go.Scatter(y=mavg200[-last_n:], text=text, mode='lines', line={'color':'magenta', 'width':3}, name='')
        trace5 = go.Scatter(y=hband200[-last_n:], text=text, mode='lines', line={'color':'magenta', 'width':3}, name='Signal')
        trace6 = go.Scatter(y=lband200[-last_n:], text=text, mode='lines', line={'color':'magenta', 'width':3}, name='Signal')
        return trace + [trace1, trace2, trace3,trace4, trace5] #, trace6

    def plot_bb_with_levels(self,mode='c',draw_mode='candlestick'):
        last_n = self._last_n - self._future_n
        tf = self._tf
        df = self._symbol.price_df[tf]

        if draw_mode == 'candlestick':
            trace = self.plot_candlestick()
        elif draw_mode == 'linechart':
            trace = self.plot_column(mode=mode)

        # line, histogram, signal = indicator.macd.MACD(symbol = self._symbol_, add_column=False, as_standard=True, tf=tf)
        mavg,lband,hband,wband,pband= indicator.bolinger.BB(symbol = self._symbol, n=200,ndev= 2,mode= mode, as_standard=True, tf=tf)._bb()
        level_236 ,level_764 ,level_1236,level_1764,level_2000,level_2236,\
            level_236n,level_764n,level_1236n,level_1764n,level_2000n,level_2236n = \
            indicator.bolinger.BB(symbol = self._symbol,n=200,ndev= 2,mode= mode, as_standard=True, tf=tf)._bb_levels(mavg,hband)
        text = df['date'][-last_n:]
        trace1 = go.Scatter(y=mavg[-last_n:], text=text, mode='lines', line={'color':'magenta', 'width':3}, name='')
        # trace2 = go.Scatter(y=lband_result[-last_n:], text=text, mode='lines', line={'color':'magenta', 'width':3}, name='Signal')
        trace3 = go.Scatter(y=hband[-last_n:], text=text, mode='lines', line={'color':'magenta', 'width':3}, name='Signal')
        trace_level1 = go.Scatter(y=level_236[-last_n:], text=text, mode='lines', line={'color':'gray', 'width':1}, name='Signal')
        trace_level2 = go.Scatter(y=level_764[-last_n:], text=text, mode='lines', line={'color':'gray', 'width':1}, name='Signal')
        trace_level3 = go.Scatter(y=level_1236[-last_n:], text=text, mode='lines', line={'color':'gray', 'width':1}, name='Signal')
        trace_level4 = go.Scatter(y=level_1764[-last_n:], text=text, mode='lines', line={'color':'gray', 'width':1}, name='Signal')
        trace_level5 = go.Scatter(y=level_2000[-last_n:], text=text, mode='lines', line={'color':'magenta', 'width':1}, name='Signal')
        trace_level6 = go.Scatter(y=level_2236[-last_n:], text=text, mode='lines', line={'color':'gray', 'width':1}, name='Signal')
        trace_level7 = go.Scatter(y=level_236n[-last_n:], text=text, mode='lines', line={'color':'gray', 'width':1}, name='Signal')
        # trace_level8 = go.Scatter(y=level_764n[-last_n:], text=text, mode='lines', line={'color':'gray', 'width':1}, name='Signal')
        # trace_level9 = go.Scatter(y=level_1236n[-last_n:], text=text, mode='lines', line={'color':'gray', 'width':1}, name='Signal')
        # trace_level10 = go.Scatter(y=level_1764n[-last_n:], text=text, mode='lines', line={'color':'gray', 'width':1}, name='Signal')
        # trace_level11 = go.Scatter(y=level_2000n[-last_n:], text=text, mode='lines', line={'color':'magenta', 'width':1}, name='Signal')
        # trace_level12 = go.Scatter(y=level_2236n[-last_n:], text=text, mode='lines', line={'color':'gray', 'width':1}, name='Signal')
        return trace + [trace1, trace3, trace_level1, trace_level2, trace_level3, trace_level4,
                        trace_level5, trace_level6, trace_level7] #, trace2, trace_level8, trace_level9, trace_level10, trace_level11]


#-------------------------- adx ---------------------------------
    def plot_adx(self, mode='c', mode_h='h', mode_l='l'):
        last_n = self._last_n - self._future_n
        tf = self._tf
        df = self._symbol.price_df[tf]
        # line, histogram, signal = indicator.macd.MACD(symbol = self._symbol_, add_column=False, as_standard=True, tf=tf)
        adxresult = indicator.adx.ADX(symbol = self._symbol,mode=mode, mode_h=mode_h, mode_l=mode_l,tf=tf,as_standard=True).adx()
        text = df['date'][-last_n:]
        trace4 = go.Scatter(y=[35]*last_n, text=text, mode='lines', line={'color': '#505050', 'width': 1}, name='')
        if adxresult == None:
            return [trace4]
        adx, adx_neg, adx_pos =adxresult
        trace1 = go.Scatter(y=adx[-last_n:], text=text, mode='lines', line={'color':'blue', 'width':3}, name='ADX')
        trace2 = go.Scatter(y=adx_neg[-last_n:], text=text, mode='lines', line={'color':'red', 'width':3}, name='DI-')
        trace3 = go.Scatter(y=adx_pos[-last_n:], text=text, mode='lines', line={'color':'green', 'width':3}, name='DI+')
        return [trace1, trace2, trace3, trace4]

#-------------------------- stoch ---------------------------------
    def plot_stoch(self, mode='c', mode_l='l', mode_h = 'h'):
        last_n = self._last_n - self._future_n
        tf = self._tf
        df = self._symbol.price_df[tf]
        line, signal = indicator.stoch.STOCH(symbol = self._symbol,mode=mode, mode_l=mode_l, mode_h= mode_h, as_standard=True, tf=tf).stoch()
        text = df['date'][-last_n:]
        trace1 = go.Scatter(y=line[-last_n:], text=text, mode='lines', line={'color':'green', 'width':3}, name='')
        trace2 = go.Scatter(y=signal[-last_n:], text=text, mode='lines', line={'color':'red', 'width':3}, name='Signal')
        trace3 = go.Scatter(y=[20]*last_n, text=text, mode='lines', line={'color': '#505050', 'width': 1}, name='')
        trace4 = go.Scatter(y=[50]*last_n, text=text, mode='lines', line={'color': '#505050', 'width': 1}, name='')
        trace5 = go.Scatter(y=[80]*last_n, text=text, mode='lines', line={'color': '#505050', 'width': 1}, name='')
        return [trace1, trace2, trace3, trace4, trace5]

#-------------------------- volume ---------------------------------
    def plot_volume(self):
        last_n = self._last_n - self._future_n
        tf = self._tf
        vol = self._symbol.column_values('v',tf)
        vol_avg = vol.rolling(30).mean()
        text = self._symbol.column_values('date',tf)[-last_n:]
        trace1 = go.Bar(y=vol[-last_n:], text=text, name='', marker_color='green')
        trace2 = go.Scatter(y=vol_avg[-last_n:], text=text, mode='lines', line={'color':'red', 'width':1}, name='vol1to30')
       
        return [trace1, trace2]

    def plot_ind_volume(self):
        last_n = self._last_n - self._future_n
        tf = self._tf
        text = self._symbol.column_values('date',tf)[-last_n:]
        ind_vol = indicator.tableau.TABLEAU(symbol = self._symbol, tf=tf)._ind_vol()
        trace1 = go.Bar(y=ind_vol[-last_n:], text=text, name='حقیقی', marker_color='green')
        return [trace1]

    def plot_corp_volume(self):
        last_n = self._last_n - self._future_n
        tf = self._tf
        text = self._symbol.column_values('date',tf)[-last_n:]
        corp_vol = indicator.tableau.TABLEAU(symbol = self._symbol, tf=tf)._corp_vol()
        trace1 = go.Bar(y=corp_vol[-last_n:], text=text, name='حقوقی', marker_color='green')
        return [trace1]

    def plot_1to30_volume(self):
        last_n = self._last_n - self._future_n
        tf = self._tf
        text = self._symbol.column_values('date',tf)[-last_n:]
        result = indicator.tableau.TABLEAU(symbol = self._symbol, tf=tf)._vol_1to30()
        trace1 = go.Scatter(y=result[-last_n:], text=text, mode='lines', line={'color':'red', 'width':3}, name='vol1to30')
       
        return [trace1]


#-------------------------- buy ---------------------------------
    def plot_ind_buy(self):
        last_n = self._last_n - self._future_n
        tf = self._tf
        text = self._symbol.column_values('date',tf)[-last_n:]
        ind_buy = self._symbol.column_values('individual_buy_vol',tf)[-last_n:]
        trace1 = go.Bar(y=ind_buy[-last_n:], text=text, name='حقیقی', marker_color='green')
        return [trace1]

    def plot_corp_buy(self):
        last_n = self._last_n - self._future_n
        tf = self._tf
        text = self._symbol.column_values('date',tf)[-last_n:]        
        corp_buy = self._symbol.column_values('corporate_buy_vol',tf)[-last_n:]
        trace1 = go.Bar(y=corp_buy[-last_n:], text=text, name='حقوقی', marker_color='green')
        return [trace1]
    
    def plot_ind_buy_percent(self):
        last_n = self._last_n - self._future_n
        tf = self._tf
        text = self._symbol.column_values('date',tf)[-last_n:]
        ind_buy = indicator.tableau.TABLEAU(symbol = self._symbol, tf=tf)._ind_buy_percent()
        trace1 = go.Bar(y=ind_buy[-last_n:], text=text, name='حقیقی', marker_color='green')
        return [trace1]

    def plot_corp_buy_percent(self):
        last_n = self._last_n - self._future_n
        tf = self._tf
        text = self._symbol.column_values('date',tf)[-last_n:]        
        corp_buy = indicator.tableau.TABLEAU(symbol = self._symbol, tf=tf)._corp_buy_percent()
        trace1 = go.Bar(y=corp_buy[-last_n:], text=text, name='حقوقی', marker_color='green')
        return [trace1]

    def plot_buy_cumsum(self):
        last_n = self._last_n - self._future_n
        tf = self._tf
        df = self._symbol.price_df[tf]

        text = df['date'][-last_n:]

        individual_buy_cumsum = indicator.tableau.TABLEAU(symbol = self._symbol, tf=tf)._ind_buy_cumsum()
        corporate_buy_cumsum = indicator.tableau.TABLEAU(symbol = self._symbol, tf=tf)._corp_buy_cumsum()
        
        trace1 = go.Scatter(y=individual_buy_cumsum[-last_n:], text=text, mode='lines', line={'color':'#000099', 'width':3}, name='خرید حقیقی')
        trace2 = go.Scatter(y=corporate_buy_cumsum[-last_n:], text=text, mode='lines', line={'color':'#770044', 'width':3}, name='خرید حقوقی')
        return [trace1, trace2]

#-------------------------- zig zag ---------------------------------
    def plot_peeks_and_valies(self):
        last_n = self._last_n - self._future_n
        tf = self._tf
        text = self._symbol.column_values('date',tf)[-last_n:]        
        column = self._symbol.column_values('peeks_and_valies',tf)[-last_n:]
        trace1 = go.Scatter(y=column[-last_n:], text=text,  mode='lines', line={'color':'green', 'width':3}, name = 'P&V')
        return [trace1]

#-------------------------- combination, plot column ---------------------------------
    def plot_column(self, mode= 'c', name ='', color='magenta', width=3):
        last_n = self._last_n - self._future_n
        tf = self._tf
        text = self._symbol.column_values('date',tf)[-last_n:]        
        column = self._symbol.column_values(mode,tf)[-last_n:]
        trace1 = go.Scatter(y=column[-last_n:], text=text, line={'color':color, 'width':width}, name = name)
        return [trace1]

    def plot_columns(self, modes= [], names=[], colors=[], widths=[]):
        if not modes: return None
        if not names: names = modes
        if not colors: colors =['green']* len(modes)
        if not widths: widths = [2]* len(modes)
        traces = []
        for i in range(len(modes)):
            traces.append(self.plot_column(mode=modes[i],name=names[i],color=colors[i],width=widths[i]))
        return traces

    def plot_combination(self, **kwargs): 
        result_trace = []
        for value in kwargs.values():
            tracer = getattr(self, value)()
            result_trace += tracer
        return result_trace

    @staticmethod
    def plot_series(sr: pd.Series,x =None , name='', color='blue' , width=3):
        trace1 = go.Scatter( y=sr,x= x, text=sr, mode='lines', line={'color':color, 'width':width}, name=name)
        return [trace1]

#-------------------------- export plot, figures ---------------------------------
    @staticmethod
    def fig(plot, title='signal', rangeslider=False, legend=False):
        fg = go.Figure(data=plot).update_xaxes(rangeslider={'visible': rangeslider})
        fg.update_layout(title={'text':title, 'x':0.5, 'font':{'size':30, 'family':'B Koodak'}},showlegend=legend)
        return fg
    
    # @staticmethod
    # def export_plot(plot, filename = "figure", format= "png"):
    #     scope = PlotlyScope()
    #     fig = go.Figure(data=plot)
    #     with open(globals.FIGURE_EXPORT_PATH + filename, "wb") as f:
    #         f.write(scope.transform(fig, format=format))
    #     return
    
    @staticmethod
    def export_plot(plot, filename = "figure.png"):
        SymbolChart.export_fig(SymbolChart.fig(plot), filename)
        return

    @staticmethod
    def export_fig(fig, filename = "figure.png", format= None, scale = None):
        pio.write_image(fig, globals.FIGURE_EXPORT_PATH + filename,format = format, scale=scale)
        return

    @staticmethod
    def export_all_tf_charts(symbol, last_n=200, future_n=26,indicators=True,volumes=False,buys=False):
        for tf in ['D','W','M']:
            SymbolChart.export_charts(symbol, tf, last_n=last_n, future_n=future_n,indicators=indicators,volumes=volumes,buys=buys)            

    @staticmethod
    def export_charts(symbol,tf='D', last_n=200, future_n=26,indicators=True, volumes=False,buys=False):
        chart = SymbolChart(symbol, last_n=200, future_n=26, tf=tf)
        filename_prefix = symbol + "_" + tf + "_" 
        if indicators: SymbolChart.export_fig(chart.fig_indicators(),filename_prefix + "indicators.png")
        if buys:       SymbolChart.export_fig(chart.fig_buys(),filename_prefix + "buys.png")
        if volumes:    SymbolChart.export_fig(chart.fig_volumes(),filename_prefix + "volumes.png")
        
    @staticmethod
    def export_tablo(df):
        fig =  ff.create_table(df)
        fig.update_layout(
            autosize=False,
            width=500,
            height=200,
        )
        fig.write_image( globals.FIGURE_EXPORT_PATH + "table_plotly.png", scale=2)
        fig.show()

    @staticmethod
    def export_charts_for_symbols(symbols, tf='D', last_n=200, future_n=26,indicators=True, volumes=False,buys=False, tinyframe=False):
        for symbol in symbols:
            SymbolChart.show_charts(symbol,tf, last_n, future_n,indicators, volumes,buys)

        if tinyframe:
            filename_prefix = "tinyframe_"
            plot_list = ["plot_ichi","plot_individual_buyers_power_","plot_bb",'plot_bb_with_levels','plot_sma_2_18_54'] #, "plot_individual_trade_capita_"
            for plot in plot_list:
                filename = plot[len('plot_'):] if plot.startswith('plot_') else plot
                SymbolChart.export_fig(SymbolChart.fig_tinyframe(symbols=symbols,last_n=last_n, future_n=future_n,tf=tf, title='سیگنال', plot1=plot),filename_prefix +filename+".png")

#-------------------------- show tinyframe ---------------------------------
    @staticmethod
    def show_tinyframes_for_symbols(symbols, cols=4, tf='D', last_n=200, future_n=26,plot_list = [], secy_list = []):
        if not plot_list: plot_list = ["plot_ichi","plot_individual_buyers_power_","plot_bb",'plot_bb_with_levels','plot_sma_2_18_54'] #, "plot_individual_trade_capita_"
        if secy_list is None or (not secy_list): secy_list = [False]* len(plot_list)
        n = len(symbols) // 60
        b = len(symbols) % 60
        i=1
        for i in range(n):
            for j in range(len(plot_list)):
                SymbolChart.fig_tinyframe(symbols=symbols[i*60:(i+1)*60],cols=cols,last_n=last_n, future_n=future_n,tf=tf,secy=secy_list[j], title='سیگنال', plot1=plot_list[j]).show()
        for j in range(len(plot_list)):
            SymbolChart.fig_tinyframe(symbols=symbols[(i-1)*60:(i-1)*60+b],cols=cols,last_n=last_n, future_n=future_n,tf=tf,secy=secy_list[j], title='سیگنال', plot1=plot_list[j]).show()    

    @staticmethod
    def fig_tinyframe(symbols , cols=0 ,  last_n=200,future_n=26,tf= 'D',secy=False, title = "Signal",**kwargs): 

        num = len(symbols)
        if num == 0: return None
        if cols == 0:
            if num<=15:
                cols = 2
            elif num <= 30:
                cols = 3
            else:
                cols = 4
        rows = math.ceil(num /cols)

        titles = [s.get_name() for s in symbols]
        # row_heights = [0.5 for i in range(rows)]
        # specs = [[{'secondary_y': True}] for i in range(rows)]
        
        if (secy):
            specs = [[{'secondary_y': True}]*cols]*rows
            fig = make_subplots(rows=rows, cols=cols, shared_xaxes=True, vertical_spacing=0.01, horizontal_spacing=0.0,specs = specs, subplot_titles=titles) #,  row_heights=row_heights)
        else:
            fig = make_subplots(rows=rows, cols=cols, shared_xaxes=True, vertical_spacing=0.01, horizontal_spacing=0.0,subplot_titles=titles) #,  row_heights=row_heights)
       # fig = make_subplots(rows=rows, cols=cols, shared_xaxes=True, vertical_spacing=0.01, horizontal_spacing=0.0, specs=specs, subplot_titles=titles, row_heights=row_heights)
 
        i = 1
        j = 1
        for symbol in symbols:
            chart = SymbolChart(symbol,last_n=last_n,future_n=future_n,tf=tf )
            all_traces = chart.plot_combination(**kwargs) 
            if (secy):
                fig.add_traces(data=all_traces, rows=i, cols=j, secondary_ys=[False, True])
                fig.update_yaxes(row=i, col=j, secondary_y=True)
            else:
                fig.add_traces(data=all_traces, rows=i, cols=j)

            fig.update_xaxes(row=i, col=j, rangeslider={'visible': False})
            j+=1
            if(j > cols): 
                i +=1
                j =1

        ttl = '{} - {}'.format(title , SymbolChart.tf_names[tf])
        fig.update_layout(title={'text':ttl, 'x':0.5, 'font':{'size':30, 'family':'B Koodak'}},
                          showlegend=True, height=max(rows*300,1000))
        return fig

#-------------------------- show all ---------------------------------
    @staticmethod
    def show_all_tf_charts(symbol, last_n=200, future_n=26,indicators=True,volumes=False,buys=False):
        for tf in ['D','W','M']:
            SymbolChart.show_charts(symbol, tf, last_n=last_n, future_n=future_n,indicators=indicators,volumes=volumes,buys=buys)            

    @staticmethod
    def show_charts(symbol, tf='D', last_n=200, future_n=26,indicators=True, volumes=False,buys=False):
        chart = SymbolChart(symbol, last_n=200, future_n=26, tf=tf)
        if indicators: chart.fig_indicators().show()
        if buys: chart.fig_buys().show()
        if volumes: chart.fig_volumes().show()
        
    @staticmethod
    def show_charts_for_symbols(symbols, tf='D', last_n=200, future_n=26,indicators=True, volumes=False,buys=False):
        for symbol in symbols:
            SymbolChart.show_charts(symbol,tf, last_n, future_n,indicators, volumes,buys)
    
#-------------------------- general show ----------------------------
    def show(self):
        specs = [ [{}], [{}], [{}], [{}], [{}], [{}], [{}], [{}], [{'secondary_y': True}] , [{}], [{}]]
        titles = ['', 'RSI', 'MACD', 'Stochastics', 'ADX', 'vol', 'BB','trade Value', 'money in/out', 'MA', 'Buyers Power']
        row_heights = [0.15, 0.05, 0.05, 0.05, 0.05, 0.05, 0.15, 0.10, 0.10, 0.15, 0.10]
        trace_candlestick = self.plot_ichi()  
        trace_individual_buyers_power = self.plot_ind_buyers_power()
        trace_trades_value = self.plot_trades_value()
        trace_individual_money = self.plot_ind_ownership_change()
        trace_adx = self.plot_adx()
        trace_rsi = self.plot_rsi()
        trace_macd = self.plot_macd()
        trace_stoch = self.plot_stoch()
        trace_vol = self.plot_volume()
        trace_ma = self.plot_rainbow_ema()
        trace_bb = self.plot_bb_with_levels()

        fig = make_subplots(rows=11, cols=1, shared_xaxes=True, vertical_spacing=0.03, horizontal_spacing=0.0,
                            specs=specs, subplot_titles=titles, row_heights=row_heights)
        fig.add_traces(data=trace_candlestick, rows=1, cols=1)
        fig.update_xaxes(row=1, col=1, rangeslider={'visible': False})

        fig.add_traces(data=trace_rsi, rows=2, cols=1)
        fig.update_yaxes(range=[0, 100], row=2, col=1)

        fig.add_traces(data=trace_macd, rows=3, cols=1)
        fig.add_traces(data=trace_stoch, rows=4, cols=1)
        fig.add_traces(data=trace_adx, rows=5, cols=1)
        fig.add_traces(data=trace_vol, rows=6, cols=1)

        fig.add_traces(data=trace_bb, rows=7, cols=1)
        fig.update_xaxes(row=7, col=1, rangeslider={'visible': False})
        
        fig.add_traces(data=trace_trades_value, rows=8, cols=1)

        fig.add_traces(data=trace_individual_money, rows=9, cols=1, secondary_ys=[False, True])
        fig.update_yaxes(title_text='قیمت پایانی', row=9, col=1, secondary_y=True)
       
        fig.add_traces(data=trace_ma, rows=10, cols=1)
        fig.update_xaxes(row=10, col=1, rangeslider={'visible': False})
        
        fig.add_traces(data=trace_individual_buyers_power, rows=11, cols=1)
       
        title = '{} - {}'.format(self._symbol.get_name(), SymbolChart.tf_names[self._tf])
        fig.update_layout(title={'text':title, 'x':0.5, 'font':{'size':30, 'family':'B Koodak'}},
                          showlegend=False, height=5000)
        return fig

    def fig_plots_2(self, plots=[], titles=[], row_heights=[], specs=[]):
        rows = len(plots)
        if not titles: titles = plots
        if not row_heights: row_heights = [round(1/rows,2)]*rows
        if not specs: specs = [{}]*rows
        fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.03, horizontal_spacing=0.0,
                            specs=specs, subplot_titles=titles, row_heights=row_heights)

        for i in range(rows):
            traces = getattr(self, plots[i])()
            fig.add_traces(data=traces, rows=i+1, cols=1)

        title = '{} - {}'.format(self._symbol.get_name(), SymbolChart.tf_names[self._tf])
        fig.update_layout(title={'text':title, 'x':0.5, 'font':{'size':30, 'family':'B Koodak'}},
                          showlegend=False, height=rows*150)
        return fig

    def fig_plots(self, **kwargs):
        rows = len(kwargs)

        titles = list(kwargs.values())
        # print(titles)
        # row_heights = [0.5 for i in range(rows)]
        # specs = [[{'secondary_y': True}] for i in range(rows)]
        # fig = make_subplots(rows=rows, cols=cols, shared_xaxes=True, vertical_spacing=0.01, horizontal_spacing=0.0, specs=specs, subplot_titles=titles, row_heights=row_heights)
        fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.01, horizontal_spacing=0.0,subplot_titles=titles) #,  row_heights=row_heights)

        i = 1
        for value in kwargs.values():
            trace = getattr(self, value)()
            fig.add_traces(data=trace, rows=i, cols=1)
            fig.update_xaxes(row=i, col=1, rangeslider={'visible': False})
            i += 1

        title = '{} - {}'.format(self._symbol.get_name(), SymbolChart.tf_names[self._tf])
        fig.update_layout(title={'text':title, 'x':0.5, 'font':{'size':30, 'family':'B Koodak'}},
                          showlegend=False, height=max(rows*500,1000))
        return fig

#-------------------------- show indicators ---------------------------------
    def fig_indicators(self):
        specs = [ [{}], [{}], [{}], [{}], [{}], [{}], [{}], [{}], [{'secondary_y': True}] , [{}], [{}]]
        titles = ['', 'RSI', 'MACD', 'Stochastics', 'ADX', 'vol', 'BB','trade Value', 'money in/out', 'SMA', 'MA']
        row_heights = [0.15, 0.05, 0.05, 0.05, 0.05, 0.05, 0.15, 0.10, 0.10, 0.15, 0.10]
        trace_candlestick = self.plot_ichi()  
        trace_trades_value = self.plot_trades_value()
        trace_individual_money = self.plot_ind_ownership_change()
        trace_adx = self.plot_adx()
        trace_rsi = self.plot_rsi()
        trace_macd = self.plot_macd()
        trace_stoch = self.plot_stoch()
        trace_vol = self.plot_volume()
        trace_ma = self.plot_rainbow_ema()
        trace_bb = self.plot_bb_with_levels()
        trace_sma_2_18_54 = self.plot_sma_2_18_54()

        fig = make_subplots(rows=11, cols=1, shared_xaxes=True, vertical_spacing=0.03, horizontal_spacing=0.0,
                            specs=specs, subplot_titles=titles, row_heights=row_heights)
        fig.add_traces(data=trace_candlestick, rows=1, cols=1)
        fig.update_xaxes(row=1, col=1, rangeslider={'visible': False})

        fig.add_traces(data=trace_rsi, rows=2, cols=1)
        fig.update_yaxes(range=[0, 100], row=2, col=1)

        fig.add_traces(data=trace_macd, rows=3, cols=1)
        fig.add_traces(data=trace_stoch, rows=4, cols=1)
        fig.add_traces(data=trace_adx, rows=5, cols=1)
        fig.add_traces(data=trace_vol, rows=6, cols=1)

        fig.add_traces(data=trace_bb, rows=7, cols=1)
        fig.update_xaxes(row=7, col=1, rangeslider={'visible': False})
        
        fig.add_traces(data=trace_trades_value, rows=8, cols=1)

        fig.add_traces(data=trace_individual_money, rows=9, cols=1, secondary_ys=[False, True])
        fig.update_yaxes(title_text='قیمت پایانی', row=9, col=1, secondary_y=True)
       
        fig.add_traces(data=trace_sma_2_18_54, rows=10, cols=1)
        fig.update_xaxes(row=10, col=1, rangeslider={'visible': False})

        fig.add_traces(data=trace_ma, rows=11, cols=1)
        fig.update_xaxes(row=11, col=1, rangeslider={'visible': False})
        
       
        title = '{} - {}'.format(self._symbol.get_name(), SymbolChart.tf_names[self._tf])
        fig.update_layout(title={'text':title, 'x':0.5, 'font':{'size':30, 'family':'B Koodak'}},
                          showlegend=False, height=5000)
        return fig

    def fig_indicators_for_mode(self, mode='c', mode_l='l' , mode_h='h', mode_o='o'):
        if self._symbol.price_df[self._tf] is None: return None
        specs = [ [{}], [{}], [{}], [{}], [{}], [{}], [{}], [{}], [{'secondary_y': True}] , [{}], [{}]]
        titles = ['', 'RSI', 'MACD', 'Stochastics', 'ADX', 'vol', 'BB','Ichi', 'money in/out', 'SMA', 'MA']
        row_heights = [0.15, 0.05, 0.05, 0.05, 0.05, 0.05, 0.15, 0.10, 0.10, 0.15, 0.10]
        trace_candlestick = self.plot_ichi()  
        trace_mode_candlestick = self.plot_ichi(mode_o=mode_o, mode_l=mode_l, mode_h=mode_h, mode=mode,draw_mode='linechart')  
        trace_individual_money = self.plot_ind_ownership_change()
        trace_adx = self.plot_adx(mode=mode, mode_l=mode_l, mode_h=mode_h)
        trace_rsi = self.plot_rsi(mode=mode)
        trace_macd = self.plot_macd(mode=mode)
        trace_stoch = self.plot_stoch(mode=mode, mode_l=mode_l, mode_h=mode_h)
        trace_vol = self.plot_volume()
        trace_ma = self.plot_rainbow_ema(mode=mode,draw_mode='linechart')
        trace_bb = self.plot_bb_with_levels(mode=mode,draw_mode='linechart')
        trace_sma_2_18_54 = self.plot_sma_2_18_54(mode=mode, draw_mode='linechart')

        fig = make_subplots(rows=11, cols=1, shared_xaxes=True, vertical_spacing=0.03, horizontal_spacing=0.0,
                            specs=specs, subplot_titles=titles, row_heights=row_heights)
        fig.add_traces(data=trace_candlestick, rows=1, cols=1)
        fig.update_xaxes(row=1, col=1, rangeslider={'visible': False})

        fig.add_traces(data=trace_rsi, rows=2, cols=1)
        fig.update_yaxes(range=[0, 100], row=2, col=1)

        fig.add_traces(data=trace_macd, rows=3, cols=1)
        fig.add_traces(data=trace_stoch, rows=4, cols=1)
        fig.add_traces(data=trace_adx, rows=5, cols=1)
        fig.add_traces(data=trace_vol, rows=6, cols=1)

        fig.add_traces(data=trace_bb, rows=7, cols=1)
        fig.update_xaxes(row=7, col=1, rangeslider={'visible': False})
        
        fig.add_traces(data=trace_mode_candlestick, rows=8, cols=1)

        fig.add_traces(data=trace_individual_money, rows=9, cols=1, secondary_ys=[False, True])
        fig.update_yaxes(title_text='قیمت پایانی', row=9, col=1, secondary_y=True)
       
        fig.add_traces(data=trace_sma_2_18_54, rows=10, cols=1)
        fig.update_xaxes(row=10, col=1, rangeslider={'visible': False})

        fig.add_traces(data=trace_ma, rows=11, cols=1)
        fig.update_xaxes(row=11, col=1, rangeslider={'visible': False})
        
       
        title = '{} - {}'.format(self._symbol.get_name(), SymbolChart.tf_names[self._tf])
        fig.update_layout(title={'text':title, 'x':0.5, 'font':{'size':30, 'family':'B Koodak'}},
                          showlegend=False, height=5000)
        return fig

#-------------------------- show volumes ---------------------------------
    def fig_volumes(self):
        specs = [ [{}], [{'secondary_y': True}], [{}], [{}], [{}], [{}], [{}], [{}], [{'secondary_y': True}] ,[{'secondary_y': True}],[{}]]
        titles = ['', 'corp buy capita', 'corp sell capita', 'corp trade capita', 'ind buy capita', 'ind sell capita', 'ind trade capita', 'vol 1to30', 'ind money in/out', 'corp money in/out','buyers power']
        row_heights = [0.15, 0.08, 0.08, 0.08, 0.08, 0.12, 0.12, 0.12, 0.15, 0.12, 0.10]
        trace_candlestick = self.plot_combination(plot1='plot_candlestick' ,plot2='plot_ichi') 

        trace_individual_buy_capita = self.plot_ind_buy_capita()
        trace_individual_sell_capita = self.plot_ind_sell_capita()
        trace_individual_trade_capita = self.plot_ind_trade_capita()
        
        trace_corp_buy_capita = self.plot_corp_buy_capita()
        trace_corp_sell_capita = self.plot_corp_sell_capita()
        trace_corp_trade_capita = self.plot_corp_trade_capita()

        trace_trades_value = self.plot_trades_value()
        trace_individual_money = self.plot_ind_ownership_change()

        trace_corporate_money = self.plot_corp_ownership_change()
        trace_individual_buyers_power = self.plot_ind_buyers_power()
        trace_vol_1to30 = self.plot_1to30_volume()

        fig = make_subplots(rows=11, cols=1, shared_xaxes=True, vertical_spacing=0.03, horizontal_spacing=0.0,
                            specs=specs, subplot_titles=titles, row_heights=row_heights)
        fig.add_traces(data=trace_candlestick, rows=1, cols=1)
        fig.update_xaxes(row=1, col=1, rangeslider={'visible': False})

        fig.add_traces(data=trace_corp_buy_capita, rows=2, cols=1)
        fig.add_traces(data=trace_corp_sell_capita, rows=3, cols=1)
        fig.add_traces(data=trace_corp_trade_capita, rows=4, cols=1)

        fig.add_traces(data=trace_individual_buy_capita, rows=5, cols=1)
        fig.add_traces(data=trace_individual_sell_capita, rows=6, cols=1)
        fig.add_traces(data=trace_individual_trade_capita, rows=7, cols=1)

        # fig.add_traces(data=trace_trades_value, rows=8, cols=1)
        fig.add_traces(data=trace_vol_1to30, rows=8, cols=1)


        fig.add_traces(data=trace_individual_money, rows=9, cols=1, secondary_ys=[False, True])
        fig.update_yaxes(title_text='قیمت پایانی', row=9, col=1, secondary_y=True)
        
        fig.add_traces(data=trace_corporate_money, rows=10, cols=1, secondary_ys=[False, True])
        fig.update_yaxes(title_text='قیمت پایانی', row=10, col=1, secondary_y=True)
        fig.add_traces(data=trace_individual_buyers_power, rows=11, cols=1)
               
        title = '{} - {}'.format(self._symbol.get_name(), SymbolChart.tf_names[self._tf])
        fig.update_layout(title={'text':title, 'x':0.5, 'font':{'size':30, 'family':'B Koodak'}},
                          showlegend=False, height=2500)
        return fig

#-------------------------- show buys ---------------------------------
    def fig_buys(self):
        specs = [ [{}], [{'secondary_y': True}], [{}], [{}], [{}], [{}], [{}], [{'secondary_y': True}], [{'secondary_y': True}] ,[{'secondary_y': True}],[{}]]
        titles = ['', 'ind trade capita', 'ind buy %', 'corp buy %', 'vol', 'ind buy capita', 'ind sell capita', 'trade values', 'ind money in/out', 'corp money in/out','buyers power']
        row_heights = [0.15, 0.08, 0.08, 0.08, 0.08, 0.12, 0.12, 0.12, 0.15, 0.12, 0.10]
        trace_candlestick = self.plot_combination(plot1='plot_candlestick' ,plot2='plot_ichi') 
        trace_individual_buy_capita = self.plot_ind_buy_capita()
        trace_individual_sell_capita = self.plot_ind_sell_capita()
        trace_individual_trade_capita = self.plot_ind_trade_capita()
        trace_buy_cumsum = self.plot_buy_cumsum()
        trace_individual_money = self.plot_ind_ownership_change()
        trace_corp_buy_percent = self.plot_corp_buy_percent()
        trace_ind_buy_percent = self.plot_ind_buy_percent()
        trace_vol = self.plot_volume()
        trace_corporate_money = self.plot_corp_ownership_change()
        trace_individual_buyers_power = self.plot_ind_buyers_power()

        fig = make_subplots(rows=11, cols=1, shared_xaxes=True, vertical_spacing=0.03, horizontal_spacing=0.0,
                            specs=specs, subplot_titles=titles, row_heights=row_heights)
        fig.add_traces(data=trace_candlestick, rows=1, cols=1)
        fig.update_xaxes(row=1, col=1, rangeslider={'visible': False})
  
        fig.add_traces(data=trace_ind_buy_percent, rows=3, cols=1)
        fig.add_traces(data=trace_corp_buy_percent, rows=4, cols=1)
        fig.add_traces(data=trace_vol, rows=5, cols=1)


        fig.add_traces(data=trace_individual_buy_capita, rows=6, cols=1)
        fig.add_traces(data=trace_individual_sell_capita, rows=7, cols=1)
        fig.add_traces(data=trace_individual_trade_capita, rows=2, cols=1)
        
        # fig.add_traces(data=trace_individual_buyers_power, rows=7, cols=1)

        fig.add_traces(data=trace_buy_cumsum, rows=8, cols=1, secondary_ys=[False, True])
        fig.update_yaxes(title_text='corp cumsum', row=8, col=1, secondary_y=True)
     
        fig.add_traces(data=trace_individual_money, rows=9, cols=1, secondary_ys=[False, True])
        fig.update_yaxes(title_text='قیمت پایانی', row=9, col=1, secondary_y=True)
        
        fig.add_traces(data=trace_corporate_money, rows=10, cols=1, secondary_ys=[False, True])
        fig.update_yaxes(title_text='قیمت پایانی', row=10, col=1, secondary_y=True)
        fig.add_traces(data=trace_individual_buyers_power, rows=11, cols=1)
               
        title = '{} - {}'.format(self._symbol.get_name(), SymbolChart.tf_names[self._tf])
        fig.update_layout(title={'text':title, 'x':0.5, 'font':{'size':30, 'family':'B Koodak'}},
                          showlegend=False, height=2500)
        return fig

#-------------------------- show combination of plots in one chart specified by parameters ---------------------------------
    def show_combination(self,title='signal', **kwargs):
        specs = [ [{'secondary_y': True}]]
        titles = [title]
        row_heights = [.85]
        fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.03, horizontal_spacing=0.0,
                            specs=specs, subplot_titles=titles, row_heights=row_heights)
        all_traces = self.plot_combination(**kwargs) 
        fig.add_traces(data=all_traces, rows=1, cols=1)
        fig.update_yaxes(title_text='قیمت پایانی', row=1, col=1, secondary_y=True)
         
        title = '{} - {}'.format(self._symbol.get_name(), SymbolChart.tf_names[self._tf])
        fig.update_layout(title={'text':title, 'x':0.5, 'font':{'size':30, 'family':'B Koodak'}},
                          showlegend=False, height=1000)
        return fig 

            