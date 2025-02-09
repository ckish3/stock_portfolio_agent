

"""
This module contains a class for downloading & savingstock price data from the AlphaVantage API.
"""

import concurrent.futures
from typing import List, Tuple
import datetime
import random
import os
import csv
import requests
import json
import pandas as pd
import logging
import yfinance
import time

import recommendation
import price_target
import stock_price
import database_actions


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class StockData:
    def __init__(self):
        self._symbols = self.download_list_of_symbols()
        #self.data = self.download_stock_price_data()
        pass

    def download_stock_price_data(self, time_period: str = '5y', number_of_symbols: int = 20, check_file: bool = False) -> pd.DataFrame:
        """
        Retrieves stock price data from the yfinance API. The format
        of the returned data has the following columns:
        | symbol | Date | Open | Close |

        Args:
            time_period (str, optional): The time period for which to retrieve stock price data. Defaults to '5y'.
                                        Must be one of the following: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'
            number_of_symbols (int, optional): The number of symbols to retrieve stock price data for. Defaults to 20.
                If None, will retrieve data for all symbols
            check_file (bool, optional): Whether to check if a file of previously-downloaded stock price data exists before downloading. Defaults to False.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the stock price data
        """

        filename = 'stock_data.csv'
    
        if os.path.exists(filename) and check_file:
            logger.info('Loading stock price data from file')
            data = pd.read_csv(filename)
            return data

        logger.info('Downloading stock price data')
     
        all_symbols = self._symbols

        if number_of_symbols is not None:
            all_symbols = random.sample(all_symbols, number_of_symbols)


        results = pd.DataFrame()
        for symbol in all_symbols:
            logger.info(f'Getting data for {symbol}')
            
            data_df = yfinance.Ticker(symbol).history(period=time_period).reset_index()
            data_df['symbol'] = symbol
            
            data_df = data_df[['symbol', 'Date', 'Open', 'Close']]
            results = pd.concat([results, data_df], axis=0)

        results.to_csv(filename, index=False)

        return results

    def download_stock_prices(self, db_actions: database_actions.DatabaseActions, symbols: List[str]) -> List[price_target.PriceTarget]:
        """
        Retrieves the price targets from the yfinance API.

        Args:
            None
        Returns:
            List[price_target.PriceTarget]: A list of Recommendation objects containing the analyst price targets data
        """
        today = datetime.date.today()
        now = datetime.datetime.now()

        symbol_maxes = stock_price.StockPrice().get_max_date_by_symbol(db_actions)
        final_list = []

        for symbol in symbols:
            if symbol in symbol_maxes:
                max_existing_date = symbol_maxes[symbol]
            else:
                max_existing_date = today - datetime.timedelta(days=99*365)

            start_date = max_existing_date + datetime.timedelta(days=1)

            worked, prices = self.download_price_of_one_symbol(symbol, today, now, start_date)
            if worked:
                final_list.extend(prices)

        return final_list

    def download_price_of_one_symbol(self, symbol: str, today: datetime.date, now: datetime.datetime, start_date: datetime.date) -> Tuple[bool, List[stock_price.StockPrice]]:

        """
        Retrieves the stock price data for a given stock symbol from the yfinance API.

        Args:
            symbol (str): The stock symbol for which to retrieve the price data.
            today (datetime.date): The current date.
            now (datetime.datetime): The current datetime.
            start_date (datetime.date): The date from which to begin retrieving price data.

        Returns:
            Tuple[bool, List[stock_price.StockPrice]]: A tuple containing a boolean indicating success and a list of StockPrice objects with the price data.
        """
        iteration = 0
        prices = []
        worked = False
        data_df = None
        while iteration < 3:
            logger.info(f'Getting price for {symbol}')
            try:
                data_df = yfinance.Ticker(symbol).history(start=start_date.isoformat(), end=today.isoformat()).reset_index()
                break
            except Exception as e:
                logger.error(f'Error getting price for {symbol}: {e}')
                iteration += 1
                time.sleep(1)
        if data_df is None or len(data_df) == 0:
            logger.warning(f'!!!WARNING: {symbol} price never retrieved')
        else:
            for i in data_df.index:
                row = data_df.loc[i]
                price = stock_price.StockPrice(id=symbol + '_' + row['Date'].isoformat(),
                                               symbol=symbol,
                                               date=row['Date'],
                                               open_price=float(row['Open']),
                                               high_price=float(row['High']),
                                               low_price=float(row['Low']),
                                               close_price=float(row['Close']),
                                               volume=int(row['Volume']),
                                               dividends=float(row['Dividends']),
                                               stock_splits=float(row['Stock Splits']),
                                               inserted_at=now)
                prices.append(price)
            worked = True

        return worked, prices

    def download_recommendations(self) -> List[recommendation.Recommendation]:
        """
        Retrieves the recommendations counts from the yfinance API. The format
        of the returned data has the following columns:
        | symbol | Date | strongBuy | buy | hold | sell | strongSell |

        Args:
            None
        Returns:
            List[recommendation.Recommendation]: A list of Recommendation objects containing the stock recommendation data
        """
        today = datetime.date.today()
        final_list = []

        for symbol in self._symbols:
            worked, rec = self.download_recommedation_of_one_symbol(symbol, today)
            if worked:
                final_list.append(rec)
        return final_list

    def download_recommedation_of_one_symbol(self, symbol: str, today: datetime.date) -> Tuple[bool, recommendation.Recommendation]:
        
        """
        Retrieves the recommendation counts for a given stock symbol from the yfinance API.

        The function attempts to get the recommendation counts for the specified symbol up to three times. If successful, it returns a Recommendation object with the strongBuy, buy, hold, sell, and strongSell counts. Otherwise, it logs warnings if the data could not be retrieved.

        Args:
            symbol (str): The stock symbol for which to retrieve the recommendation counts.
            today (datetime.date): The current date.

        Returns:
            Tuple[bool, recommendation.Recommendation]: A tuple containing a boolean indicating success and a Recommendation object with the recommendation counts.

        """
        iteration = 0
        rec = None
        worked = False
        data_df = None
        while iteration < 3:
            logger.info(f'Getting recommendation counts for {symbol}')
            try:
                data_df = yfinance.Ticker(symbol).get_recommendations()
                break
            except Exception as e:
                logger.error(f'Error getting recommendation counts for {symbol}: {e}')
                iteration += 1
                time.sleep(1)
        if data_df is None:
            logger.warning(f'!!!WARNING: {symbol} recommendations never retrieved')
        if 'strongBuy' in data_df and len(data_df) > 0:
            data_df = data_df.iloc[0]
            rec = recommendation.Recommendation(
                id = symbol + '_' + today.isoformat(),
                symbol = symbol,
                date = today,
                strong_buy = int(data_df['strongBuy']),
                buy = int(data_df['buy']),
                hold = int(data_df['hold']),
                sell = int(data_df['sell']),
                strong_sell = int(data_df['strongSell'])
            )
            worked = True

        return worked, rec

    def download_price_targets(self) -> List[price_target.PriceTarget]:
        """
        Retrieves the price targets from the yfinance API.

        Args:
            None
        Returns:
            List[price_target.PriceTarget]: A list of Recommendation objects containing the analyst price targets data
        """
        today = datetime.date.today()
        final_list = []

        for symbol in self._symbols:
            worked, target = self.download_price_target_of_one_symbol(symbol, today)
            if worked:
                final_list.append(target)
        return final_list
    def download_price_target_of_one_symbol(self, symbol: str, today: datetime.date) -> Tuple[
        bool, price_target.PriceTarget]:

        """
        Retrieves the price target for a given stock symbol from the yfinance API.

        The function attempts to get the price target for the specified symbol up to three times. If successful, it returns a PriceTarget object with
        the current, low, high, mean, and median price targets. Otherwise, it logs warnings if the data could not be retrieved.

        Args:
            symbol (str): The stock symbol for which to retrieve the price target.
            today (datetime.date): The current date.

        Returns:
            Tuple[bool, price_target.PriceTarget]: A tuple containing a boolean indicating success and a PriceTarget object with the price target data.

        """
        iteration = 0
        target = None
        worked = False
        data_dict = None
        while iteration < 3:
            logger.info(f'Getting price target for {symbol}')
            try:
                data_dict = yfinance.Ticker(symbol).get_analyst_price_targets()
                break
            except Exception as e:
                logger.error(f'Error getting price target for {symbol}: {e}')
                iteration += 1
                time.sleep(1)
        if data_dict is None:
            logger.warning(f'!!!WARNING: {symbol} price target never retrieved')
        elif 'current' in data_dict and \
                'low' in data_dict and \
                'high' in data_dict and \
                'mean' in data_dict and \
                'median' in data_dict:
            target = price_target.PriceTarget(
                                              id=symbol + '_' + today.isoformat(),
                                              symbol=symbol,
                                              date=today,
                                              current=float(data_dict['current']) if data_dict['current'] is not None else None,
                                              low=float(data_dict['low']) if data_dict['low'] is not None else None,
                                              high=float(data_dict['high']) if data_dict['high'] is not None else None,
                                              mean=float(data_dict['mean']) if data_dict['mean'] is not None else None,
                                              median=float(data_dict['median']) if data_dict['median'] is not None else None
            )
            worked = True
        else:
            logger.warning(f'!!!WARNING: {symbol} price target incomplete')

        return worked, target

    def download_list_of_symbols(self) -> List[str]:
        """
        Retrieves a list of currently listed US stock symbols

        Returns:
            List[str]: The list of stock symbols

        """
        logger.info('Getting list of stock symbols')

        url = 'https://www.alphavantage.co/query'
        api_key = os.getenv('ALPHAVANTAGE_API_KEY')

        symbol_index = 0
        exchange_index = 2

        params =  {'function': 'LISTING_STATUS',
                'apikey': api_key}

        all_symbols = []

        with requests.Session() as s:
            download = s.get(url, params=params)
            decoded_content = download.content.decode('utf-8')
            cr = csv.reader(decoded_content.splitlines(), delimiter=',')
            my_list = list(cr)
            for row in my_list:
                all_symbols.append(row[symbol_index])

        symbols = all_symbols[1:]
        logger.info(f'Retrieved {len(symbols)} symbols')
        return symbols

    def get_list_of_symbols(self) -> List[str]:
        return self._symbols

    def get_stock_price_data(self) -> dict:
        return self.data
