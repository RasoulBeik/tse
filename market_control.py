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
import market_model
from market_model import Market

class watch:
    def __init__(self, model, view):
        self.model = model
        self.view = view

class MarketControl:
    watches = {
        'DEFAULT_WATCH' : watch(model= lambda symbol_names, by, tf, offset, date,in_groups, except_groups,in_markets,except_markets : 
                            market_model.DefaultModel(symbol_names=symbol_names, by=by, tf = tf, date=date,in_groups=in_groups, except_groups=except_groups,in_markets=in_markets,except_markets=except_markets )
                        , view = lambda : market_view.DefaultView())
        ,'MA_WATCH' : watch(model = lambda symbol_names, by, tf, offset, date,in_groups, except_groups,in_markets,except_markets : 
                            market_model.MAModel(symbol_names=symbol_names, by=by, tf = tf, date=date,in_groups=in_groups, except_groups=except_groups,in_markets=in_markets,except_markets=except_markets )
                        , view = lambda : market_view.MAView())
        ,'REGULAR_WATCH' : watch(model = lambda symbol_names, by, tf, offset, date,in_groups, except_groups,in_markets,except_markets : 
                            market_model.RegularModel(symbol_names=symbol_names, by=by, tf = tf, date=date,in_groups=in_groups, except_groups=except_groups,in_markets=in_markets,except_markets=except_markets )
                        , view = lambda : market_view.RegularView())
        ,'REGULAR_FARSI_WATCH' : watch(model = lambda symbol_names, by, tf, offset, date,in_groups, except_groups,in_markets,except_markets : 
                            market_model.RegularModel(symbol_names=symbol_names, by=by, tf = tf, date=date,in_groups=in_groups, except_groups=except_groups,in_markets=in_markets,except_markets=except_markets )
                        , view = lambda : market_view.RegularFarsiView())
        ,'SYMBOL_WATCH' : watch(model = lambda symbol,by, tf, offset,date  : 
                            market_model.SymbolModel(symbol=symbol, by=by, tf = tf,offset=offset, date=date)
                        , view = lambda : market_view.SymbolWatchView())
    }

    @property
    def tablo(self):
        return self._tablo

    @property
    def tabloview(self):
        return self._tabloview

    def __init__(self, by='', tf ='D',offset = -1, date=''):
        self._tf = tf
        self._offset = offset
        self._date = datetime.datetime.now().strftime('%Y%m%d') if date == '' else date
        self._by = ('realtime' if Market.is_open() else 'daily') if by == '' else by
     
        # ---------- model, view ------------
        self._view:market_view.MarketView = None
        self._model:market_model.MarketModel = None
        # ---------- set tablo , tabloview ------------
        self._tablo: pd.DataFrame = None
        self._tabloview : pd.DataFrame = None

    def apply_filter(self):
        pass

    def refresh(self):
        self._tablo = self._model.refresh()
        self.apply_filter()
        self._tabloview = self._view._map_columns(self._tablo)
        return self._tabloview
 
 
    def start_dash(self):
        refresh_interval = 30   # in seconds

        dft: DataFrameTable = DataFrameTable(
            headers = self.tabloview.columns,
            id='df-table',
            data = self.tabloview.to_dict('records'),
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

        app = Dash(__name__)
        app.layout = html.Div([
            html.Div(dft),
            dcc.Interval(id='interval-component', interval=refresh_interval * 1000, n_intervals=0)
            ])

        @app.callback(
            Output('df-table', 'data'),
            Input('interval-component', 'n_intervals'))
        def update_data(_):
            # global mw

            if (self._by != 'daily') and Market.is_open():
                df = self.refresh()
            else: 
                df = self.tabloview
            return df.to_dict('records')

        app.run_server(debug=True)

    def show_tablo(self):
        refresh_df = self.refresh if (self._by != 'daily') and Market.is_open() else None
        tabloo.show(df=self._tabloview ,refresh_df=refresh_df)
        return self

    def export_tablo(self):
        SymbolChart.export_tablo(df = self._tabloview)
