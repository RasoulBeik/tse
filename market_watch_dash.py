import pandas as pd
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dftable import DataFrameTable
import globals
from market_model import Market


prefered_by = 'realtime' if Market.is_open() else 'daily'
mw : Market = Market(by=prefered_by)

# change below variables based on dataframe
refresh_interval = 30   # in seconds

dft: DataFrameTable = DataFrameTable(
    headers = mw.tabloview.columns,
    id='df-table',
    data = mw.tabloview.to_dict('records'),
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
    global mw

    if (mw._by != 'daily') and Filter.is_open():
        df = mw.initialize_realtime_tablo()
    else: 
        df = mw.tablo
    return df.to_dict('records')

if __name__ == "__main__":
    app.run_server(debug=True)
