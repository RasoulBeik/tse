import pytse_client as tse
from pytse_client import config, symbols_data, tse_settings, download_client_types_records
import pandas as pd
from datetime import datetime
import symbol_repository as rep
from symbol import Symbol
import globals

rep.download_market_watch(reload_period=175)