import pandas as pd
from dash import Dash
from dash_table import DataTable
from symbol import Symbol

class DataFrameTable(DataTable):
    def __init__(self, headers=None, **args):
        if 'data' in args and 'columns' not in args:
            args['columns'] = [{'name': i, 'id': i} for i in args['data'][0].keys()]
        if headers is not None and 'columns' in args:
            for (c, h) in zip(args['columns'], headers):
                c['name'] = h
        if 'fixed_rows' not in args:
            args['fixed_rows'] = {'headers': True}
        if 'sort_action' not in args:
            args['sort_action'] = 'native'
        if 'filter_action' not in args:
            args['filter_action'] = 'native'
        if 'style_table' not in args:
            args['style_table'] = {'height': '400px', 'minWidth':'100%', 'overflowY': 'auto'}
        if 'style_data_condition' not in args:
            args['style_data_conditional'] = []

        super().__init__(**args)
        return

    def _append_style_data_conditional_(self, style_conditional):
        if not isinstance(style_conditional, list):
            style_conditional = [style_conditional]
        self.style_data_conditional = self.style_data_conditional + style_conditional
        return

    def set_cells_props(self, columns_id=None, colors=None, background_colors=None, filters=None):
        if columns_id is None:
            columns_id = []
        elif not isinstance(columns_id, list):
            columns_id = [columns_id]
        if colors is None:
            colors = []
        elif not isinstance(colors, list):
            colors = [colors]
        if background_colors is None:
            background_colors = []
        elif not isinstance(background_colors, list):
            background_colors = [background_colors]
        if filters is None:
            filters = []
        elif not isinstance(filters, list):
            filters = [filters]

        maxlen = max(len(columns_id), len(colors), len(background_colors), len(filters))

        props = [{i: {}} for i in range(maxlen)]

        for (prop, col_id, i) in zip(props, columns_id, range(maxlen)):
            if 'if' not in prop[i]:
                prop[i]['if'] = {}
            prop[i]['if']['column_id'] = col_id
        for (prop, filter, i) in zip(props, filters, range(maxlen)):
            if 'if' not in prop[i]:
                prop[i]['if'] = {}
            prop[i]['if']['filter_query'] = filter
        for (prop, color, i) in zip(props, colors, range(maxlen)):
            prop[i]['color'] = color
        for (prop, bgcolor, i) in zip(props, background_colors, range(maxlen)):
            prop[i]['backgroundColor'] = bgcolor

        conditions = [prop[i] for (prop, i) in zip(props, range(maxlen))]
        self._append_style_data_conditional_(conditions)
        return

##################################################################################

### Dash testing
if __name__ == '__main__':
    symbol = Symbol('پترول', read_base_info=False)
    df = symbol.get_df()[['date', 'open', 'high', 'low', 'close', 'volume']]
    headers = ['تاریخ', 'اولین', 'بیشترین', 'کمترین', 'پایانی', 'حجم']

    dft: DataFrameTable = DataFrameTable(
        headers = headers,
        id='table',
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

    # dft.set_cells_props(columns_id=['open', 'close'], colors=['#AA0000', '#00AA00'], background_colors=['#3D9970', '#FF3D70'], filters=['{open} < {close}', '{open} > {close}'])
    dft.set_cells_props(columns_id=['date', 'date'], colors=['#FFFFFF', '#FFFFFF'], background_colors=['#3D9970', '#FF3D70'], filters=['{open} < {close}', '{open} > {close}'])
    dft.set_cells_props(columns_id='high', colors='#0000FF', background_colors='#DDEEFF', filters='{high} > 15000')

    app = Dash(__name__)
    app.layout = dft
    app.run_server(debug=True)
    pass
