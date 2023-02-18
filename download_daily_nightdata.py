import pytse_client as tse
from pytse_client import config, symbols_data, tse_settings, download_client_types_records
import pandas as pd
from datetime import datetime
import symbol_repository as rep
import globals

### Uncomment one of the below lines
# symbols = ['خودرو', 'وبملت', 'فولاد', 'فملی', 'پترول', 'خساپا', 'وتجارت', 'وبصادر', 'شبندر', 'برکت', 'فلات']
# symbols = ['ونیرو', 'ونفت', 'ولبهمن', 'وصنعت', 'وسینا', 'وسرمد', 'وسالت', 'وتجارت', 'واتی', 'مفاخر', 'ما',
#             'لکما', 'لابسا', 'فسا', 'فجام', 'فبیرا', 'سمازن', 'سفانو', 'سفاسی', 'سرود', 'ساروم', 'سخند',
#             'زمگسا', 'رتکو', 'رتاپ', 'دیران', 'دفرا', 'خودکفا',
#             'دفارا', 'ددام', 'دتماد', 'دانا', 'دالبر', 'دارو', 'خکار', 'خپارس']
# symbols = ['وصنعت', 'ما', 'وتجارت', 'وسالت', 'وسرمد']
symbols = sorted(list(symbols_data.all_symbols()))

### Downloading symbols
def download_symbols(symbols=None):
    if (symbols is None):
        symbols = sorted(list(symbols_data.all_symbols()))
    print('Start time:', datetime.now().time())
    rep.download_ohlc_daily_for_symbols(symbols, do_parallel=True)
    print('End time:', datetime.now().time())

def download_today_micro_trades(symbols=None):
    if (symbols is None):
        symbols = sorted(list(symbols_data.all_symbols()))
    print('Start time:', datetime.now().time())
    rep.download_today_trades_for_symbols(symbols)
    print('\nEnd time:', datetime.now().time())

### Generating weekly and monthly data
def generate_weekly_and_monthly_data(symbols=None):
    if (symbols is None):
        symbols = sorted(list(symbols_data.all_symbols()))
    print('Start time:', datetime.now().time())
    rep.generate_periodic_data(symbol_names=symbols, timeframes=['W', 'WJ'])
    rep.generate_periodic_data(symbol_names=symbols, timeframes=['M', 'MJ'])
    print('End time:', datetime.now().time())


if __name__ == "__main__":
    download_symbols()
    generate_weekly_and_monthly_data()
    # download_today_micro_trades(symbols)