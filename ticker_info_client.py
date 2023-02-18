from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from time import sleep
import pandas as pd
import json
from shutil import copyfile
import globals
from pytse_client.symbols_data import get_ticker_index
from pytse_client import config

def download_ticker_info(save_to_file=globals.TICKER_INFO_FILE):
    browser = webdriver.Firefox(firefox_binary='/opt/firefox-dev/firefox')
    browser.get(globals.TICKER_INFO_URL)
    sleep(5)
    input('Change settings and then press enter ...')
    print()
    main_div: WebElement = browser.find_element_by_id('main')
    symbol_links = main_div.find_elements_by_class_name('inst')
    tickers = []
    for i in range(0, len(symbol_links), 2):
        try:
            symbol_id = symbol_links[i].get_attribute('target')
            symbol_name = symbol_links[i].text.replace('ك', 'ک').replace('ي', 'ی')
            corp_name = symbol_links[i+1].text.replace('ك', 'ک').replace('ي', 'ی')
            tickers.append({'symbol_id': symbol_id, 'symbol': symbol_name, 'corp_name': corp_name})
        except StaleElementReferenceException:
            continue
    if len(tickers) > 0:
        ticker_df = pd.DataFrame(tickers)
        ticker_df.to_csv(save_to_file, index=False, encoding='utf-8-sig')
    browser.close()
    return

def update_ticker_info(from_file=globals.TICKER_INFO_FILE):
    with open(f'{config.pytse_dir}/data/symbols_name.json', 'r+', encoding='utf8') as file:
        data = json.load(file)
        
        ticker_df = pd.read_csv(from_file)
        for _, row in ticker_df.iterrows():
            new_symbol = {row['symbol'].strip(): str(row['symbol_id']).strip()}
            data.update(new_symbol)
        file.seek(0)
        json.dump(data, file, ensure_ascii=False, indent=2)
    copyfile(f'{config.pytse_dir}/data/symbols_name.json', globals.TICKER_INFO_JSON)
    return

if __name__ == "__main__":
    download_ticker_info(save_to_file=globals.TICKER_INFO_FILE)
    update_ticker_info(from_file=globals.TICKER_INFO_FILE)
