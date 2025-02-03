
import os
import logging
import sqlalchemy
from sqlalchemy.orm import Session
import database_actions
import database_base
import stock_data


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    connection_string = os.getenv('DATABASE_URL')
    db = database_actions.DatabaseActions(connection_string)
    engine = db.get_engine()
    stocks = stock_data.StockData()
    symbols = stocka.get_list_of_symbols()

    symbol_size = 100
    i = 0
    j = i + symbol_size
    database_base.Base.metadata.create_all(bind=engine)
    with Session(engine) as session:
        recs = stocks.download_recommendations()
        logger.info('Adding recommendations to database')
        session.add_all(recs)
        session.commit()

    with Session(engine) as session:
        targets = stocks.download_price_targets()
        logger.info('Adding price targets to database')
        session.add_all(targets)
        session.commit()

    while i < len(symbols):
        with Session(engine) as session:
            j = min(j, len(symbols))
            symbol_sample = symbols[i:j]
            prices = stocks.download_stock_prices(db, symbol_sample)
            logger.info('Adding stockprices to database')
            session.add_all(prices)
            session.commit()
            i = j
            j = i + symbol_size

#    stock_data.StockData()

if __name__ == '__main__':
    main()