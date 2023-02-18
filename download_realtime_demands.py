import symbol_repository as rep
from datetime import datetime
from pytse_client import symbols_data
import numpy as np
from time import sleep

def download_realtime_demands_for_symbols(symbols, reload_period=30, max_reload=None):
    current_date = datetime.now().strftime('%Y%m%d')
    
    max_reload = np.inf if max_reload is None else max_reload
    reload_count = 0
    
    while reload_count < max_reload:
        current_time = datetime.now().strftime('%H:%M:%S')
        print('\nStart time:', datetime.now().time())
        # failed_symbols = rep.download_realtime_demands_for_symbols(symbols=symbols)
        failed_symbols = rep.download_realtime_demands_for_symbols_parallel(symbols=symbols)
        print('\nEnd time:', datetime.now().time())
        print('\nFailed symbols:', failed_symbols)
     
        reload_count = reload_count + 1
        print(reload_count, current_date, current_time)
        sleep(reload_period)
    return

if __name__ == "__main__":
    # symbols = ['خودرو', 'وبملت', 'فولاد', 'فملی', 'پترول', 'خساپا', 'وتجارت', 'وبصادر', 'شبندر', 'برکت', 'فلات']
    symbols = sorted(list(symbols_data.all_symbols()))
    download_realtime_demands_for_symbols(symbols=symbols)
