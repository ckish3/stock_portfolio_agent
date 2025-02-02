
import sqlalchemy
import pandas as pd


class DatabaseActions:
    raw_schema_name = 'raw_data'

    def __init__(self, connection_string: str):
        self._engine = sqlalchemy.create_engine(connection_string)

        
        with self._engine.connect() as connection:
            connection.execute(sqlalchemy.schema.CreateSchema(DatabaseActions.raw_schema_name, if_not_exists=True))
            connection.commit()

    def get_engine(self):
        return self._engine