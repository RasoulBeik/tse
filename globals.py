TRADE_DETAILS_URL = 'http://tsetmc.com/Loader.aspx?ParTree=15131P&i={0}&d={1}'      #0: symbol_id; 1: trade_date
TODAY_DETAILS_URL = 'http://tsetmc.com/Loader.aspx?ParTree=151321&i={0}'            #0: symbol_id
DAILY_OHLC_URL = 'http://tsetmc.com/tsev2/data/Export-txt.aspx?t=i&a=1&b=0&i={0}'   #0: symbol_id
SYMBOL_INFO_URL = 'http://www.tsetmc.com/Loader.aspx?ParTree=151311&i={0}'          #0: symbol_id
# TRADE_DETAILS_URL = 'http://tsetmc.ir/Loader.aspx?ParTree=15131P&i={}&d={}'
# TODAY_DETAILS_URL = 'http://tsetmc.ir/Loader.aspx?ParTree=151321&i={}'
# DAILY_OHLC_URL = 'http://tsetmc.ir/tsev2/data/Export-txt.aspx?t=i&a=1&b=0&i={}'
ACTIVE_SHAREHOLDERS_CHANGES_URL = 'http://www.tsetmc.com/Loader.aspx?ParTree=15131I&t=0'
TICKER_INFO_URL = 'http://www.tsetmc.com/Loader.aspx?ParTree=15131F'
MARKET_WATCH_URL = 'http://members.tsetmc.com/tsev2/excel/MarketWatchPlus.aspx?d=0'
SYMBOL_REALTIME_DEMANDS_URL = 'http://www.tsetmc.com/tsev2/data/instinfofast.aspx?i={0}&c=57+'  #0: symbol_id

BASE_DATA_PATH = './trade_details/'
FIGURE_EXPORT_PATH = './figure_export/'
SYMBOL_PATH = './trade_details/{}'
SYMBOL_DAILY_FILE = './trade_details/{}/{}_ohlc_daily.csv'
SYMBOL_FILE = './trade_details/{0}/{0}_ohlc_{1}.csv'                #0: symbol_name, 1: timeframe
SYMBOL_INTRADAY_FILE = './trade_details/{0}/{0}_intraday_{1}.csv'   #0: symbol_name; 1: year
SYMBOL_TODAY_FILE = './trade_details/{0}/{0}_today.csv'             #0: symbol_name
SYMBOLS_BASE_INFO_FILE = './trade_details/base_info.csv'
SYMBOLS_GROUPS_INFO_FILE = './trade_details/symbol_groups.csv'
SHAREHOLDERS_CHANGES_FILE = './trade_details/shareholders_changes.csv'
TICKER_INFO_FILE = './trade_details/ticker_info.csv'
TICKER_INFO_JSON = './trade_details/symbols_name.json'
MARKET_WATCH_FILE = './trade_details/market_watch/market_watch_{0}.csv'     #0: date
GENERAL_MARKET_WATCH_FILE = './trade_details/market_watch/market_watch.csv'  
REALTIME_DEMANDS_FILE = './trade_details/realtime_demands/realtime_demands_{0}.csv'     #0: date
GENERAL_REALTIME_DEMANDS_FILE = './trade_details/realtime_demands/realtime_demands.csv'   
BASE_INFO_FILE = './trade_details/base_info/base_info_{0}.csv'     #0: date
GENERAL_BASE_INFO_FILE = './trade_details/base_info/base_info.csv'     
