from numpy.lib.shape_base import tile
from numpy.lib.utils import info
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
import pytse_client as tse
from pytse_client.symbols_data import get_ticker_index
from pytse_client import config, symbols_data, tse_settings, download_client_types_records, Ticker
import pandas as pd
import numpy as np
import os

import re
from datetime import date, datetime, time, timedelta
import jdatetime
from jdatetime import JalaliToGregorian
from bs4 import BeautifulSoup
from ast import literal_eval
import simple_request as sr
import globals
import multiprocessing as mp
from itertools import repeat
from time import sleep

def _download_symbol_(symbol_name, zero_ohlc_rows='substitute'):
    """
    sometimes some OHLC values are 0 in downloaded data and sometimes by downloading again it is OK.
    this function tries to download correct data for 5 times and after 5 iterations, if there are still 0 in
    OHLC, removes those rows if remove_zero_ohlc_rows == True
    """
    symbol_index = get_ticker_index(symbol_name)
    url = globals.DAILY_OHLC_URL.format(symbol_index)
    df = None
    try:
        for _ in range(5):
            with closing(get(url, allow_redirects=True)) as resp:
                resp = resp.content.decode('utf-8')
                resp = resp.split('\r\n')
                columns = ['ticker', 'date','open','high','low','adjClose','value','volume','count','<PER>','<OPEN>','close']
                df = pd.DataFrame([sub.split(",") for sub in resp[1:-1]], columns=columns)
                df = df[::-1]
                df = df.reset_index()
                df = df[['date','open','high','low','adjClose','value','volume','count','close']]
                df['date'] = pd.to_datetime(df['date'])
                df['open'] = df['open'].astype('float64')
                df['high'] = df['high'].astype('float64')
                df['low'] = df['low'].astype('float64')
                df['adjClose'] = df['adjClose'].astype('float64')
                df['value'] = df['value'].astype('float64')
                df['volume'] = df['volume'].astype('float64')
                df['count'] = df['count'].astype('float64')
                df['close'] = df['close'].astype('float64')

                ## check if there is not any 0 in OHLC return df, else download again
                if len(df[(df['open']==0) | (df['high']==0) | (df['low']==0) | (df['close']==0)]) == 0:
                    return df
        ## if there is a df, but it contains some OHLC with 0
        if df is not None:
            if zero_ohlc_rows.lower() == 'remove':
                df = df[(df['open']!=0) & (df['high']!=0) & (df['low']!=0) & (df['close']!=0)]
            elif zero_ohlc_rows.lower() == 'substitute':
                df = _substitute_zero_ohlc_(df)
            return df
    except Exception as ex:
        return None
    return None

def _substitute_zero_ohlc_(df: pd.DataFrame):
    cols = ['open', 'high', 'low', 'close']

    def __substitue_zeros_in_day__(day_row: pd.Series):
        zero_count = (list(day_row[cols]).count(0))

        # if number of zeros <= 2, then fill them with average of nonzero cols
        if zero_count <= 2:
            avg = round(day_row[cols].sum() / (4 - zero_count), 2)
            for col in cols:
                day_row[col] = avg if day_row[col] == 0 else day_row[col]
        # if number of zeros is 3, then find ration between current day and previous day of nonzero column and apply it on zero columns
        elif zero_count == 3:
            nonzero_col = None
            for col in cols:
                if day_row[col] != 0:
                    nonzero_col = col
                    break
            if nonzero_col:
                y_nonzero_col = 'y_' + nonzero_col
                ratio = (day_row[nonzero_col] - day_row[y_nonzero_col]) / day_row[y_nonzero_col]
            else:
                ratio = 0
            for col in cols:
                if col != nonzero_col:
                    y_col = 'y_' + col
                    day_row[col] = round((1 + ratio) * day_row[y_col], 2)
        # if all columns are zero, fill them with previous day values
        else:
            for col in cols:
                y_col = 'y_' + col
                day_row[col] = day_row[y_col]
        return day_row

    df['y_open'] = df['open'].shift(1)
    df['y_high'] = df['high'].shift(1)
    df['y_low'] = df['low'].shift(1)
    df['y_close'] = df['close'].shift(1)

    zero_df = df[(df['open'] == 0) | (df['high'] == 0) | (df['low'] == 0) | (df['close'] == 0)]
    zero_df = zero_df.apply(__substitue_zeros_in_day__, axis=1)
    for col in cols:
        df.loc[zero_df.index, col] = zero_df[col]
    df = df.drop(columns=['y_open', 'y_high', 'y_low', 'y_close'])
    return df

def download_ohlc_daily(symbol_name):
    # symbol = symbol.strip()
    # symbol_df = tse.download(symbol_name)
    # symbol_df = symbol_df[symbol_name].reset_index()

    symbol_df = _download_symbol_(symbol_name, zero_ohlc_rows='substitute')
    if symbol_df is None:
        return
    
    symbol_actors_df = download_client_types_records(symbol_name)
    symbol_actors_df = symbol_actors_df[symbol_name].reset_index()
    symbol_df = pd.merge(symbol_df, symbol_actors_df, on='date', how='left')

    symbol_df['hl2'] = (symbol_df['high'] + symbol_df['low']) / 2
    symbol_df['hlc3'] = (symbol_df['high'] + symbol_df['low'] + symbol_df['close']) / 3
    symbol_df['hlcc4'] = (symbol_df['high'] + symbol_df['low'] + 2 * symbol_df['close']) / 4

    symbol_dir = globals.SYMBOL_PATH.format(symbol_name)
    try:
        os.mkdir(symbol_dir)
    except:
        pass
    file_name = globals.SYMBOL_FILE.format(symbol_name, 'D')
    symbol_df['date'] = symbol_df['date'].astype('str').apply(lambda x: x.replace('-', ''))
    symbol_df['symbol'] = symbol_name
    symbol_df.to_csv(file_name, index=False, encoding='utf-8-sig')

    symbol_df['date'] = pd.to_datetime(symbol_df['date'])
    symbol_df['date'] = symbol_df['date'].apply(_convert_to_jalali_date_).apply(lambda x: x.replace('-', ''))
    file_name = globals.SYMBOL_FILE.format(symbol_name, 'DJ')
    symbol_df.to_csv(file_name, index=False, encoding='utf-8-sig')
    return

def _download_symbol_with_fail_check_(symbol_name):
    """
    tries to download daily trades of symbol_name for 5 times.
    if download is successful returns None, otherwise returns symbol_name.
    """
    for _ in range(5):
        try:
            print(symbol_name, end='\t')
            download_ohlc_daily(symbol_name)
            return None
        except Exception as ex:
            continue
    return symbol_name

def download_ohlc_daily_for_symbols(symbols, do_parallel=True):
    failed_symbols = None
    if do_parallel:
        with mp.Pool() as pool:
            failded_symbols = pool.map(_download_symbol_with_fail_check_, symbols)
            failded_symbols = [symbol for symbol in failded_symbols if symbol]
        # failed_symbols = _download_symbols_in_parallel_(symbols)
    else:
        failed_symbols = []
        while len(symbols) > 0:
            symbol = symbols[0]
            failed_symbol = _download_symbol_with_fail_check_(symbol)
            if failed_symbol is not None:
                failed_symbols.append(symbol)
            symbols.remove(symbol)
    print('\nFailed symbols:', failed_symbols)
    return failed_symbols

def download_base_info_for_symbols(symbol_names):
    current_date = datetime.now().strftime('%Y%m%d')
    file_name = globals.BASE_INFO_FILE.format(current_date)
    general_file_name = globals.GENERAL_BASE_INFO_FILE

    symbols_info = []
    failed_symbols = []
    for symbol_name in symbol_names:
        print(symbol_name, end='\t')
        info = _download_base_info_(symbol_name)
        if info is not None:
            symbols_info.append(info)
        else:
            failed_symbols.append(symbol_name)
    print()

    info_df: pd.DataFrame = pd.DataFrame(symbols_info)
    
    # if save_to_file is not None:
    #     info_df.to_csv(save_to_file, index=False, encoding='utf-8-sig')
    info_df.to_csv(file_name, index=False, encoding='utf-8-sig')
    info_df.to_csv(general_file_name, index=False, encoding='utf-8-sig')
    
    return failed_symbols

def _get_symbol_market_from_title_(title: str):
    kala = 'بورس کالا'
    fara_bourse = 'فرابورس'
    bourse = 'بورس'

    corp_name = ''
    market = ''
    submarket = ''
    try:
        # market_part = title.strip().split('-')[1].strip()
        title_parts = title.strip().split('-')
        corp_name = title_parts[0]
        i = corp_name.find('(')
        corp_name = corp_name[:i].strip()
        
        market_part = title_parts[1].strip()
        if kala in market_part:
            market = kala
            submarket = ''
        elif fara_bourse in market_part:
            market = fara_bourse
            i = market_part.find(fara_bourse)
            submarket = market_part[:i].strip()
        elif bourse in market_part:
            market = bourse
            i = market_part.find(bourse)
            submarket = market_part[:i].strip()
    except:
        pass
    return corp_name, market, submarket

def _get_base_info_attribute_(response, att_name):
    start = '{}='.format(att_name)
    i = response.find(start) + len(start)
    j = len(response[:i]) + response[i:].find(',')
    return response[i:j].replace("'", '')

def _download_base_info_(symbol_name):
    try:
        t: Ticker = Ticker(symbol_name)

        eps = _get_base_info_attribute_(response=t.ticker_page_response.text, att_name='EstimatedEPS')
        total_shares = _get_base_info_attribute_(response=t.ticker_page_response.text, att_name='ZTitad')
        total_shares = '0' if total_shares.strip() == '' else total_shares
        float_shares_percent = _get_base_info_attribute_(response=t.ticker_page_response.text, att_name='KAjCapValCpsIdx')
        float_shares_percent = '0' if float_shares_percent.strip() == '' else float_shares_percent
        sector_code = _get_base_info_attribute_(response=t.ticker_page_response.text, att_name='CSecVal')
        sector = _get_base_info_attribute_(response=t.ticker_page_response.text, att_name='LSecVal')

        tmin = _get_base_info_attribute_(response=t.ticker_page_response.text, att_name='PSGelStaMin')
        tmax = _get_base_info_attribute_(response=t.ticker_page_response.text, att_name='PSGelStaMax')
        low_week = _get_base_info_attribute_(response=t.ticker_page_response.text, att_name='MinWeek')
        high_week = _get_base_info_attribute_(response=t.ticker_page_response.text, att_name='MaxWeek')
        low_year = _get_base_info_attribute_(response=t.ticker_page_response.text, att_name='MinYear')
        high_year = _get_base_info_attribute_(response=t.ticker_page_response.text, att_name='MaxYear')
        base_vol = _get_base_info_attribute_(response=t.ticker_page_response.text, att_name='BaseVol')
        vol_month = _get_base_info_attribute_(response=t.ticker_page_response.text, att_name='QTotTran5JAvg')

        title = _get_base_info_attribute_(response=t.ticker_page_response.text, att_name='Title')
        corp_name, market, submarket = _get_symbol_market_from_title_(title=title)

        info = {'symbol': symbol_name, 'corp_name':corp_name, 'eps': eps, 'total_shares': total_shares, 'float_shares': float_shares_percent, \
                'tmin': tmin, 'tmax': tmax, 'low_week': low_week, 'high_week': high_week, 'low_year': low_year, 'high_year': high_year, \
                'base_vol': base_vol, 'vol_month': vol_month,
                'sector': sector, 'sector_code': sector_code, 'market': market, 'submarket': submarket}
        # info = {'symbol': symbol_name, 'eps': eps, 'pe_ratio': pe_ratio, 'total_shares': total_shares, 'float_shares': float_shares_percent, 'sector': sector}
        return info
    except Exception as ex:
        print(str(ex))
        return None

def save_symbols_groups(save_to_file=globals.SYMBOLS_GROUPS_INFO_FILE):
    symbol_info_df = pd.read_csv(globals.SYMBOLS_BASE_INFO_FILE)
    sector_df = symbol_info_df.groupby(by=['sector', 'sector_code']).count().reset_index()
    sector_df = sector_df[['sector', 'sector_code']]
    sector_df.to_csv(save_to_file, index=False, encoding='utf-8-sig')
    return

def generate_periodic_data(symbol_names, timeframes):
    failed_symbols = []
    for symbol_name in symbol_names:
        daily_file_name = globals.SYMBOL_FILE.format(symbol_name, 'D')
        try:
            daily_df = pd.read_csv(daily_file_name)
            for tf in timeframes:
                temp_df = _aggregate_(origin_df=daily_df, timeframe=tf, remove_null_rows=True)
                temp_df['symbol'] = symbol_name
                file_name = globals.SYMBOL_FILE.format(symbol_name, tf)
                temp_df.to_csv(file_name, index=False, encoding='utf-8-sig')
            print(symbol_name, end='\t')
        except Exception as ex:
            failed_symbols.append(symbol_name)
            print(ex)
            continue
    print('\nFailed sybmols:', failed_symbols)
    return failed_symbols

def read_data_file(symbol_name, timeframe='D'):
    file_name = globals.SYMBOL_FILE.format(symbol_name, timeframe)
    try:
        return pd.read_csv(file_name)
    except:
        return None


def _aggregate_(origin_df, timeframe, remove_null_rows=True):
    agg_dict = {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'adjClose': 'last',
        'value' : 'sum',
        'volume': 'sum',
        'count': 'sum',
        'individual_buy_count': 'sum',
        'corporate_buy_count': 'sum',
        'individual_sell_count': 'sum',
        'corporate_sell_count': 'sum',
        'individual_buy_vol': 'sum',
        'corporate_buy_vol': 'sum',
        'individual_sell_vol': 'sum',
        'corporate_sell_vol': 'sum',
        'individual_buy_value' : 'sum',
        'corporate_buy_value' : 'sum',
        'individual_sell_value' : 'sum',
        'corporate_sell_value' : 'sum',
        'individual_buy_mean_price' : 'mean',
        'individual_sell_mean_price' : 'mean',
        'corporate_buy_mean_price' : 'mean',
        'corporate_sell_mean_price' : 'mean',
        'individual_ownership_change': 'sum'
    }

    origin_df['date'] = pd.to_datetime(origin_df['date'].astype('str'))
    origin_df['individual_buy_count'] = origin_df['individual_buy_count'].fillna(0).astype('float64')
    origin_df['corporate_buy_count'] = origin_df['corporate_buy_count'].fillna(0).astype('float64')
    origin_df['individual_sell_count'] = origin_df['individual_sell_count'].fillna(0).astype('float64')
    origin_df['corporate_sell_count'] = origin_df['corporate_sell_count'].fillna(0).astype('float64')
    origin_df['individual_buy_vol'] = origin_df['individual_buy_vol'].fillna(0).astype('float64')
    origin_df['corporate_buy_vol'] = origin_df['corporate_buy_vol'].fillna(0).astype('float64')
    origin_df['individual_sell_vol'] = origin_df['individual_sell_vol'].fillna(0).astype('float64')
    origin_df['corporate_sell_vol'] = origin_df['corporate_sell_vol'].fillna(0).astype('float64')
    origin_df['individual_buy_value'] = origin_df['individual_buy_value'].fillna(0).astype('float64')
    origin_df['corporate_buy_value'] = origin_df['corporate_buy_value'].fillna(0).astype('float64')
    origin_df['individual_sell_value'] = origin_df['individual_sell_value'].fillna(0).astype('float64')
    origin_df['corporate_sell_value'] = origin_df['corporate_sell_value'].fillna(0).astype('float64')
    origin_df['individual_buy_mean_price'] = origin_df['individual_buy_mean_price'].fillna(0).astype('float64')
    origin_df['corporate_buy_mean_price'] = origin_df['corporate_buy_mean_price'].fillna(0).astype('float64')
    origin_df['individual_sell_mean_price'] = origin_df['individual_sell_mean_price'].fillna(0).astype('float64')
    origin_df['corporate_sell_mean_price'] = origin_df['corporate_sell_mean_price'].fillna(0).astype('float64')
    origin_df['individual_ownership_change'] = origin_df['individual_ownership_change'].fillna(0).astype('float64')

    agg_df = None
    timeframe = timeframe.upper()
    if 'W' in timeframe:
        if 'J' in timeframe:
            tf = 'W-FRI'
        else:
            tf = 'W'
        agg_df = origin_df.resample(tf, on='date', label='left').agg(agg_dict)
        agg_df = agg_df.reset_index()
        if 'J' in timeframe:
            agg_df['date'] = agg_df['date'].apply(_convert_to_jalali_date_)
    elif 'M' in timeframe:
        if 'J' not in timeframe:
            tf = 'MS'
            agg_df = origin_df.resample(tf, on='date', label='left').agg(agg_dict)
            agg_df = agg_df.reset_index()
        else:
            origin_df['jdate'] = origin_df['date'].apply(_convert_to_jalali_year_and_month_)
            agg_df = origin_df.groupby(by='jdate').agg(agg_dict)
            agg_df = agg_df.reset_index()
            agg_df = agg_df.rename(columns={'jdate': 'date'})
            origin_df = origin_df.drop(columns=['jdate'])

    origin_df['date'] = origin_df['date'].astype('str')
    agg_df['date'] = agg_df['date'].astype('str').apply(lambda x: x.replace('-', ''))
    agg_df['hl2'] = (agg_df['high'] + agg_df['low']) / 2
    agg_df['hlc3'] = (agg_df['high'] + agg_df['low'] + agg_df['close']) / 3
    agg_df['hlcc4'] = (agg_df['high'] + agg_df['low'] + 2 * agg_df['close']) / 4

    if remove_null_rows:
        agg_df = agg_df[agg_df['close'].notnull()]
    return agg_df

def _convert_to_jalali_year_and_month_(gdate):
    jd = jdatetime.GregorianToJalali(gdate.year, gdate.month, gdate.day)
    return '%d-%02d' % (jd.jyear, jd.jmonth)

def _convert_to_jalali_date_(gdate):
    jd = jdatetime.GregorianToJalali(gdate.year, gdate.month, gdate.day)
    return '%d-%02d-%02d' % (jd.jyear, jd.jmonth, jd.jday)

def download_today_trades(symbol_name, save_to_file=True):
    print(symbol_name, end='\t')

    file_name = globals.SYMBOL_TODAY_FILE.format(symbol_name)
    try:
        os.remove(file_name)
    except:
        pass

    symbol_index = get_ticker_index(symbol_name)
    url = globals.TODAY_DETAILS_URL.format(symbol_index)
    try:
        symbol_page = sr.simple_get(url, timeout=60, verbose=False)
        if symbol_page is not None:
            soup = BeautifulSoup(symbol_page, 'html.parser')
            trades_script = [str(s) for s in soup.find_all('script') if 'ClosingPriceData' in str(s)]
            var_data = trades_script[0].split(';')
            today_data = None
            for v in var_data:
                if 'ClosingPriceData' in v:
                    today_data = v
                    break
            if today_data:
                i = today_data.find('[')
                today_data = today_data[i:]
                today_data = literal_eval(today_data)
                if len(today_data) > 0:
                    today_df = pd.DataFrame(today_data,
                                            columns=['time', 'adjClose', 'close', 'seq', 'volume', 'value', 'y_day', 'G', 'l_day', 'h_day'])
                    if save_to_file:
                        today_df.to_csv(file_name, index=False, encoding='utf-8')
                    return today_df
                else:
                    print('No trade data available for', symbol_name)
        else:
            print('Error! Page is empty!', symbol_name)
            return None
    except Exception as ex:
        print('Connection timeout for', symbol_name)
        # print(str(ex))
        return None
    return None

def download_today_trades_for_symbols(symbols):
    with mp.Pool() as pool:
        pool.map(download_today_trades, symbols)
    return

def read_today_trades(symbol_name):
    file_name = globals.SYMBOL_TODAY_FILE.format(symbol_name)
    try:
        return pd.read_csv(file_name)
    except:
        return None

def _generate_date_range_(start_date: date, end_date: date, days_step=1, to_string=True, remove_separator=True):
    days = (end_date - start_date).days
    all_dates = [start_date + timedelta(days=d) for d in range(0, days, days_step)]
    all_dates = [date.isoformat() for date in all_dates if (date.weekday()!=3) and (date.weekday()!=4)]
    if to_string:
        all_dates = [str(d).replace('-', '') if remove_separator else str(d) for d in all_dates]
    return all_dates

def _download_intraday_trades_in_date_(symbol_name: str, trade_date: str):
    symbol_id = symbols_data.get_ticker_index(symbol_name)
    url = globals.TRADE_DETAILS_URL.format(symbol_id, trade_date)
    try:
        symbol_page = sr.simple_get(url, timeout=30)
        if symbol_page is not None:
            soup = BeautifulSoup(symbol_page, 'html.parser')
            trades_script = [str(s) for s in soup.find_all('script') if 'IntraTradeData' in str(s)]
            var_data = trades_script[0].split(';')
            intra_trade_data = None
            for v in var_data:
                if 'IntraTradeData' in v:
                    intra_trade_data = v
                    break
            if intra_trade_data:
                i = intra_trade_data.find('[')
                intra_trade_data = intra_trade_data[i:]
                intra_trade_data = literal_eval(intra_trade_data)
                if len(intra_trade_data) > 0:
                    trade_df = pd.DataFrame(intra_trade_data,
                                            columns=['seq', 'time', 'volume', 'price', 'dummy'])
                    trade_df['seq'] = trade_df['seq'].astype(np.int32)
                    trade_df = trade_df.sort_values(by='seq')
                    trade_df = trade_df.set_index('seq')
                    trade_df['date'] = trade_date
                    trade_df['symbol'] = symbol_name
                    # filename = SYMBOL_INTRADAY_FILE.format(symbol, symbol, date)
                    # trade_df.to_csv(filename, index=False, encoding='utf-8-sig')
                    print('Downloaded.', symbol_name, trade_date)
                    return trade_df[['symbol', 'date', 'time', 'volume', 'price']]
                else:
                    print('No trade data available!', symbol_name, trade_date)
                    return None
        else:
            print('Page is empty!', symbol_name, trade_date)
            return None
    except Exception as ex:
        print('Connection timeout!', symbol_name, trade_date)
        return None
    return None

def download_intraday_trades_in_year(symbol_name, year,forced_download = False):
    file_name = globals.SYMBOL_INTRADAY_FILE.format(symbol_name, year)

    if os.path.isfile(file_name) and not forced_download:
        print (file_name, " is already downloaded...")
        return
    present = datetime.now().date()
    endyear = date(year+1, 1, 1)
    year_dates = _generate_date_range_(date(year, 1, 1), min(present, endyear), to_string=True, remove_separator=True)
    year_df = pd.DataFrame(columns=['symbol', 'date', 'time', 'volume', 'price'])
    for d in year_dates:
        day_df = _download_intraday_trades_in_date_(symbol_name=symbol_name, trade_date=d)
        if day_df is not None:
            year_df = pd.concat([year_df, day_df])
    if len(year_df) > 0:
        year_df.to_csv(file_name, index=False, encoding='utf-8')
    return

def download_intraday_trades_for_symbols(symbols, year,forced_download = False):
    with mp.Pool() as pool:
        pool.starmap(download_intraday_trades_in_year, zip(symbols, repeat(year), repeat(forced_download)))
    return

def download_shareholders_changes(append_to_file=globals.SHAREHOLDERS_CHANGES_FILE):
    page = sr.simple_get(globals.ACTIVE_SHAREHOLDERS_CHANGES_URL)
    soup = BeautifulSoup(page, 'html.parser')
    rows = soup.find_all('tr')
    last_jdate = rows[0].find_all('th')[1].text
    jdate = last_jdate.split('/')
    gdate = JalaliToGregorian(jyear=int(jdate[0]), jmonth=int(jdate[1]), jday=int(jdate[2]))
    gdate = date(gdate.gyear, gdate.gmonth, gdate.gday)
    last_gdate = str(gdate).replace('-', '')

    current_symbol_company = ''
    current_symbol_id = ''
    share_changes = []
    for tr in rows[1:]:
        cols = tr.find_all('td')

        # symbol company name and symbol id are in a <a> tag in in the first <td> of each <tr>.
        # the first shareholder is also in this <td> as a <li> tag.
        # other sharholders of each company name are in separated <tr>s without repeating company name.

        # extracting symbol company name and symbol id from first <td> of each <tr>
        symbol_company_link = cols[0].find('a')     # cols[0] is first <td>
        if symbol_company_link is not None:
            current_symbol_company = symbol_company_link.text
            try:
                current_symbol_id = symbol_company_link['href'].split('&i=')[1]
            except:
                pass

        # extracting shareholder name from first <td> of each <tr>
        shareholder = cols[0].find('li')    # cols[0] is first <td>
        if shareholder is not None:
            shareholder = shareholder.text

        # extracting available shares from second <tr> of each <tr>
        available_shares = str(list(cols[1].children)[0])       # cols[1] is second <tr>
        available_shares = available_shares.replace(',', '')

        # extracting share changes from second <tr> of each <tr>
        neg_changed_shares = cols[1].find('div', class_='mn')
        pos_changed_shares = cols[1].find('div', class_='pn')
        if neg_changed_shares is not None:
            changed_shares = '-' + neg_changed_shares.text.replace('(', '').replace(')', '').replace(',', '')
        elif pos_changed_shares is not None:
            changed_shares = pos_changed_shares.text.replace('(', '').replace(')', '').replace(',', '')
        else:
            changed_shares = '0'
        share_changes.append(
            {'jdate': last_jdate, 'date': last_gdate, 'symbol_company': current_symbol_company, 'symbol_id': current_symbol_id, \
             'shareholder': shareholder, 'available_shares': available_shares, 'changed_shares': changed_shares})
    
    if len(share_changes) <= 0:
        return

    new_changes_df = pd.DataFrame(share_changes)

    try:
        ticker_df = pd.read_csv(globals.TICKER_INFO_FILE)
        ticker_df['symbol_id'] = ticker_df['symbol_id'].astype('str')
        new_changes_df = pd.merge(left=new_changes_df, right=ticker_df, on='symbol_id', how='left')
    except:
        new_changes_df['symbol'] = np.nan

    columns = ['jdate', 'date', 'symbol_company', 'symbol_id', 'symbol', 'shareholder', 'available_shares', 'changed_shares']
    new_changes_df = new_changes_df[columns]

    try:
        current_df = pd.read_csv(append_to_file)
        # if changes of last date were saved in file, they should not be saved again.
        if len(current_df.loc[current_df['date'].astype('str')==last_gdate]) == 0:
            current_df = pd.concat([current_df, new_changes_df])
            current_df.to_csv(append_to_file, index=False, encoding='utf-8-sig')
    except Exception as ex:
        new_changes_df.to_csv(append_to_file, index=False, encoding='utf-8-sig')
    return

def download_market_watch(reload_period=60, max_reload=None):
    current_date = datetime.now().strftime('%Y%m%d')
    file_name = globals.MARKET_WATCH_FILE.format(current_date)
    general_file_name = globals.GENERAL_MARKET_WATCH_FILE

    max_reload = np.inf if max_reload is None else max_reload
    reload_count = 0
    
    while reload_count < max_reload:
        reload_count = reload_count + 1
        current_time = datetime.now().strftime('%H:%M:%S')
        try:
            resp = get(globals.MARKET_WATCH_URL, allow_redirects=True)
            df = pd.read_excel(resp.content)
        except:
            print(reload_count, current_date, current_time, 'Download Error!')
            continue
        df.columns = df.iloc[1].values
        df = df.iloc[2:]
        df['date'] = current_date
        df['time'] = current_time
        df.columns = [ \
            'symbol', 'corp_name', 'count', 'volume', 'value', 'yesterday', 'open', 'close', 'close_change', 'close_percent', \
            'adjClose', 'adjClose_change', 'adjClose_percent', 'low', 'high', 'eps', 'pe', \
            'demand_count_1', 'demand_volume_1', 'demand_price_1', 'offer_price_1', 'offer_volume_1', 'offer_count_1', 'date', 'time' ]
        df['symbol'] = df['symbol'].apply(lambda x: x.replace('ك', 'ک').replace('ي', 'ی'))

        try:
            mw_df = pd.read_csv(file_name)
            mw_df = pd.concat([mw_df, df])
            mw_df.to_csv(file_name, index=False, encoding='utf-8-sig')
            mw_df.to_csv(general_file_name, index=False, encoding='utf-8-sig')
        except:
            df.to_csv(file_name, index=False, encoding='utf-8-sig')
            df.to_csv(general_file_name, index=False, encoding='utf-8-sig')
            
        # reload_count = reload_count + 1
        print(reload_count, current_date, current_time)
        sleep(reload_period)
    return

def _download_symbol_realtime_demands_(symbol_name):
    try:
        print(symbol_name, end='\t')
     
        symbol_id = get_ticker_index(symbol_name)
        response = sr.simple_get(globals.SYMBOL_REALTIME_DEMANDS_URL.format(symbol_id))
        response = str(response)
        ohlc = response.split(';')[0].split(',')
        demands = response.split(';')[2].split(',')
        shareholders = response.split(';')[4].split(',')
        return {
            'symbol': symbol_name,
            'close': int(ohlc[2]),
            'adjClose': int(ohlc[3]),
            'open': int(ohlc[4]),
            'yesterday': int(ohlc[5]),
            'high': int(ohlc[6]),
            'low': int(ohlc[7]),
            'count': int(ohlc[8]),
            'volume': int(ohlc[9]),
            'value': int(ohlc[10]),
            'date': int(ohlc[12]),
            'time': int(ohlc[13]),

            'demand_count_1': int(demands[0].split("@")[0]),
            'demand_volume_1': int(demands[0].split("@")[1]),
            'demand_price_1': int(demands[0].split("@")[2]),
            'offer_count_1': int(demands[0].split("@")[5]),
            'offer_volume_1': int(demands[0].split("@")[4]),
            'offer_price_1': int(demands[0].split("@")[3]),

            'demand_count_2': int(demands[1].split("@")[0]),
            'demand_volume_2': int(demands[1].split("@")[1]),
            'demand_price_2': int(demands[1].split("@")[2]),
            'offer_count_2': int(demands[1].split("@")[5]),
            'offer_volume_2': int(demands[1].split("@")[4]),
            'offer_price_2': int(demands[1].split("@")[3]),

            'demand_count_3': int(demands[2].split("@")[0]),
            'demand_volume_3': int(demands[2].split("@")[1]),
            'demand_price_3': int(demands[2].split("@")[2]),
            'offer_count_3': int(demands[2].split("@")[5]),
            'offer_volume_3': int(demands[2].split("@")[4]),
            'offer_price_3': int(demands[2].split("@")[3]),

            'individual_buy_vol': int(shareholders[0]),
            'corporate_buy_vol': int(shareholders[1]),
            'individual_sell_vol': int(shareholders[3]),
            'corporate_sell_vol': int(shareholders[4]),
            'individual_buy_count': int(shareholders[5]),
            'corporate_buy_count': int(shareholders[6]),
            'individual_sell_count': int(shareholders[8]),
            'corporate_sell_count': int(shareholders[9])
        }
    except:
        return None

def download_realtime_demands_for_symbols(symbols):
    current_date = datetime.now().strftime('%Y%m%d')
    current_time = datetime.now().strftime('%H:%M:%S')

    file_name = globals.REALTIME_DEMANDS_FILE.format(current_date)

    symbol_demands = []
    failed_symbols = []

    for symbol in symbols:
        demands = _download_symbol_realtime_demands_(symbol_name=symbol)
        if demands is not None:
            symbol_demands.append(demands)
        else:
            failed_symbols.append(symbol)
    print()

    if len(symbol_demands) > 0:
        df = pd.DataFrame(symbol_demands)
        df['fetch_time'] = current_time 
        try:
            demands_df = pd.read_csv(file_name)
            demands_df = pd.concat([demands_df, df]).drop_duplicates()
            demands_df.to_csv(file_name, index=False, encoding='utf-8-sig')
        except:
            df.to_csv(file_name, index=False, encoding='utf-8-sig')
    return failed_symbols

def download_realtime_demands_for_symbols_parallel(symbols):
    current_date = datetime.now().strftime('%Y%m%d')
    current_time = datetime.now().strftime('%H:%M:%S')
    file_name = globals.REALTIME_DEMANDS_FILE.format(current_date)
    general_file_name = globals.GENERAL_REALTIME_DEMANDS_FILE

    with mp.Pool() as pool:
        symbol_demands = pool.map(_download_symbol_realtime_demands_, symbols)
    symbol_demands = [sd for sd in symbol_demands if sd is not None]

    downloaded_symbols = [sd['symbol'] for sd in symbol_demands]
    failed_symbols = [symbol for symbol in symbols if symbol not in downloaded_symbols]

    if len(symbol_demands) > 0:
        df = pd.DataFrame(symbol_demands)
        df['fetch_time'] = current_time 
        try:
            demands_df = pd.read_csv(file_name)
            demands_df = pd.concat([demands_df, df]).drop_duplicates()
            demands_df.to_csv(file_name, index=False, encoding='utf-8-sig')
            demands_df.to_csv(general_file_name, index=False, encoding='utf-8-sig')
        except:
            df.to_csv(file_name, index=False, encoding='utf-8-sig')
            df.to_csv(general_file_name, index=False, encoding='utf-8-sig')
    return failed_symbols

def aggregate_realtime_demands(symbol_name, timeframe='15T', demand_file_date=None):
    agg_dict = {
        'close_open': 'first',
        'close_high': 'max',
        'close_low': 'min',
        'close': 'last',
    }

    if demand_file_date is None:
        file_name = globals.GENERAL_REALTIME_DEMANDS_FILE
    else:
        file_name = globals.REALTIME_DEMANDS_FILE.format(demand_file_date)
    try:
        df = pd.read_csv(file_name)
    except:
        print(file_name, 'not found!')
        return None
    df['fetch_time'] = pd.to_datetime(df['fetch_time'])
    df['close_open'] = df['close']
    df['close_high'] = df['close']
    df['close_low'] = df['close']
    symbol_df = df.loc[df['symbol'] == symbol_name]
    agg_df = symbol_df.resample(timeframe, on='fetch_time', label='left').agg(agg_dict)
    agg_df = agg_df.reset_index()
    agg_df['fetch_time'] = agg_df['fetch_time'].apply(lambda x: datetime.time(x))
    agg_df.columns = ['fetch_time', 'open', 'high', 'low', 'close']
    return agg_df

#--------------------- load functions ------------------------

def load_base_info(date=None):
    if date is None:
        date = datetime.now().strftime('%Y%m%d')
    file_name = globals.BASE_INFO_FILE.format(date)
    general_file_name = globals.GENERAL_BASE_INFO_FILE
    try:
        return pd.read_csv(file_name)
    except:
        try:
            return pd.read_csv(general_file_name)
        except:
            return None

def load_market_watch(date=None):
    if date is None:
        date = datetime.now().strftime('%Y%m%d')
    file_name = globals.MARKET_WATCH_FILE.format(date)
    general_file_name = globals.GENERAL_MARKET_WATCH_FILE
    try:
        return pd.read_csv(file_name)
    except:
        try:
            return pd.read_csv(general_file_name)
        except:
            return None

def load_realtime_demands(date=None):
    if date is None:
        date = datetime.now().strftime('%Y%m%d')
    file_name = globals.REALTIME_DEMANDS_FILE.format(date)
    general_file_name = globals.GENERAL_REALTIME_DEMANDS_FILE

    try:
        return pd.read_csv(file_name)
    except:
        try:
            return pd.read_csv(general_file_name)
        except:
            return None


def load_shareholders_activities():
    file_name = globals.SHAREHOLDERS_CHANGES_FILE
    try:
        sh = pd.read_csv(file_name)
        sh['date'] = sh['date'].astype('str') 
        return sh
    except:
        return None
