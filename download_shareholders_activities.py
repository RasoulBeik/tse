import pytse_client as tse
from pytse_client import config, symbols_data, tse_settings, download_client_types_records
import pandas as pd
from datetime import datetime
import symbol_repository as rep
from symbol import Symbol
import globals

if __name__ == "__main__":
    ### Uncomment one of the below lines
    # symbols = ['خودرو', 'وبملت', 'فولاد', 'فملی', 'پترول', 'خساپا', 'وتجارت', 'وبصادر', 'شبندر', 'برکت', 'شپنا', 'غگرجی']
    # symbols = sorted(list(symbols_data.all_symbols()))

    ### Downloading and saving base info of symbols
    print('Start time:', datetime.now().time())
    rep.download_shareholders_changes()
    print('End time:', datetime.now().time())
    
