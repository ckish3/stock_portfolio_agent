

"""
This module contains a class for downloading & savingstock price data from the AlphaVantage API.
"""

from typing import List
import datetime
import random
import os
import csv
import requests
import json
import pandas as pd
import logging
import yfinance


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
        self._symbols = self.get_list_of_symbols()
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


    def get_list_of_symbols(self) -> List[str]:
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

        return all_symbols[1:]

    def get_stock_price_data(self) -> dict:
        return self.data
