import pandas as pd
import symbol_repository as rep
from datetime import datetime
from pytse_client import symbols_data
from today_symbol import TodaySymbol

if __name__ == "__main__":
    # symbols = ['خودرو', 'وبملت', 'فولاد', 'فملی', 'پترول', 'خساپا', 'وتجارت', 'وبصادر', 'شبندر', 'برکت', 'فلات']
    # symbols = ['وصنعت', 'ما', 'وتجارت', 'وسالت', 'وسرمد']
    # symbols = ['ونیرو', 'ونفت', 'ولبهمن', 'وصنعت', 'وسینا', 'وسرمد', 'وسالت', 'وتجارت', 'واتی', 'مفاخر', 'ما',
    #             'لکما', 'لابسا', 'فسا', 'فجام', 'فبیرا', 'سمازن', 'سفانو', 'سفاسی', 'سرود', 'ساروم', 'سخند',
    #             'زمگسا', 'رتکو', 'رتاپ', 'دیران', 'دفرا', 'خودکفا',
    #             'دفارا', 'ددام', 'دتماد', 'دانا', 'دالبر', 'دارو', 'خکار', 'خپارس']
    symbols = sorted(list(symbols_data.all_symbols()))

    print('Start time:', datetime.now().time())
    rep.download_intraday_trades_for_symbols(symbols=symbols,year=2021)
    print('\nEnd time:', datetime.now().time())

