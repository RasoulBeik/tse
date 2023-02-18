import pandas as pd
from datetime import datetime
import symbol_repository as rep

class TodaySymbol:
    def __init__(self, symbol_name, start_time='09:00:00'):
        self._symbol_name_ = symbol_name
        self._today_df_: pd.DataFrame = rep.read_today_trades(self._symbol_name_)
        if self._today_df_ is not None:
            start_time = datetime.strptime(start_time, '%H:%M:%S')
            self._today_df_['time'] = self._today_df_['time'].apply(lambda x: datetime.strptime(str(x), '%H%M%S'))
            self._today_df_ = self._today_df_[self._today_df_['time'] >= start_time]
        return

    def _generate_ohlc(self, target_col, timeframe):
        # today_df: pd.DataFrame = rep.read_today_trades(self._symbol_name_)
        if self._today_df_ is None:
            return None

        # start_time = datetime.strptime(start_time, '%H:%M:%S')
        # self._today_df_['time'] = self._today_df_['time'].apply(lambda x: datetime.strptime(str(x), '%H%M%S'))
        # today_df = today_df[today_df['time'] >= start_time]

        ohlc_agg = self._today_df_.resample(timeframe, on='time', label='left')
        open = ohlc_agg.agg({ target_col: 'first'})[target_col]
        high = ohlc_agg.agg({ target_col: 'max'})[target_col]
        low = ohlc_agg.agg({ target_col: 'min'})[target_col]
        close = ohlc_agg.agg({ target_col: 'last'})[target_col]
        volume = ohlc_agg.agg({ 'volume': 'sum'})['volume']
        ohlc_df = pd.DataFrame({'open': open, 'high': high, 'low': low, 'close': close, 'volume': volume}, dtype='float64').reset_index()
        ohlc_df['time'] = ohlc_df['time'].apply(lambda x: str(datetime.time(x)))
        return ohlc_df

    @property
    def ohlc(self):
        return {
            'm1': self._generate_ohlc('close', '1T'),
            'm5': self._generate_ohlc('close', '5T'),
            'm15': self._generate_ohlc('close', '15T'),
            'm30': self._generate_ohlc('close', '30T')
        }
