
# import pandas as pd
# from sqlalchemy import create_engine
# from sqlalchemy.exc import SQLAlchemyError
# import os
# from dotenv import load_dotenv
# import logging
# from urllib.parse import quote  # For URL-encoding the password

# # Set up logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# # Load environment variables
# load_dotenv()

# class Load:
#     _engine = None

#     @classmethod
#     def get_engine(cls):
#         """Create or reuse a SQLAlchemy engine using environment variables."""
#         if cls._engine is None:
#             db_host = os.getenv('DB_HOST', 'localhost')
#             db_name = os.getenv('DB_NAME', 'weather_db')
#             db_user = os.getenv('DB_USER', 'postgres')
#             db_password = os.getenv('DB_PASSWORD', '')
#             db_port = os.getenv('DB_PORT', '5432')

#             # URL-encode the password to handle special characters
#             encoded_password = quote(db_password, safe='')
#             db_url = f"postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"
#             try:
#                 cls._engine = create_engine(db_url, pool_pre_ping=True)
#                 logger.info("Database engine created successfully.")
#             except SQLAlchemyError as e:
#                 logger.error(f"Failed to create database engine: {e}")
#                 raise
#         return cls._engine

#     @staticmethod
#     def load_dataframe(data: pd.DataFrame, table_name: str, if_exists: str = 'append', index: bool = False, chunksize: int = 1000):
#         """
#         Load a DataFrame into a PostgreSQL table efficiently.

#         Parameters:
#         - data: pd.DataFrame to load
#         - table_name: target table name
#         - if_exists: {'fail', 'replace', 'append'} behavior if table exists
#         - index: whether to write DataFrame index as a column
#         - chunksize: number of rows to write at a time
#         """
#         if data.empty:
#             logger.warning("No data to load into the database.")
#             return

#         engine = Load.get_engine()
#         try:
#             data.to_sql(
#                 name=table_name,
#                 con=engine,
#                 if_exists=if_exists,
#                 index=index,
#                 method='multi',
#                 chunksize=chunksize
#             )
#             logger.info(f"Data loaded into table '{table_name}' (if_exists='{if_exists}', rows={len(data)})")
#         except SQLAlchemyError as e:
#             logger.error(f"Failed to load data into table '{table_name}': {e}")
#             raise

# if __name__ == "__main__":
#     # Example usage
#     data = pd.DataFrame({
#         'city': ['Nairobi'],
#         'temperature': [25.0]
#     })
#     Load.load_dataframe(data, table_name='weather_data', if_exists='replace')

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import os
from dotenv import load_dotenv
import logging
from urllib.parse import quote

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class Load:
    _engine = None

    @classmethod
    def get_engine(cls):
        """Create or reuse a SQLAlchemy engine using environment variables."""
        if cls._engine is None:
            db_host = os.getenv('DB_HOST', 'localhost')
            db_name = os.getenv('DB_NAME', 'weather_db')
            db_user = os.getenv('DB_USER', 'postgres')
            db_password = os.getenv('DB_PASSWORD', '')
            db_port = os.getenv('DB_PORT', '5432')

            # Debug: Log the credentials being used
            logger.info(f"Connecting to database with: user={db_user}, host={db_host}, port={db_port}, dbname={db_name}")

            # URL-encode the password to handle special characters
            encoded_password = quote(db_password, safe='')
            db_url = f"postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"
            try:
                cls._engine = create_engine(db_url, pool_pre_ping=True)
                logger.info("Database engine created successfully.")
            except SQLAlchemyError as e:
                logger.error(f"Failed to create database engine: {e}")
                raise
        return cls._engine

    @staticmethod
    def load_dataframe(data: pd.DataFrame, table_name: str, if_exists: str = 'append', index: bool = False, chunksize: int = 1000):
        """
        Load a DataFrame into a PostgreSQL table efficiently.

        Parameters:
        - data: pd.DataFrame to load
        - table_name: target table name
        - if_exists: {'fail', 'replace', 'append'} behavior if table exists
        - index: whether to write DataFrame index as a column
        - chunksize: number of rows to write at a time
        """
        if data.empty:
            logger.warning("No data to load into the database.")
            return

        engine = Load.get_engine()
        try:
            data.to_sql(
                name=table_name,
                con=engine,
                if_exists=if_exists,
                index=index,
                method='multi',
                chunksize=chunksize
            )
            logger.info(f"Data loaded into table '{table_name}' (if_exists='{if_exists}', rows={len(data)})")
        except SQLAlchemyError as e:
            logger.error(f"Failed to load data into table '{table_name}': {e}")
            raise

if __name__ == "__main__":
    # Example usage
    data = pd.DataFrame({
        'city': ['Nairobi'],
        'temperature': [25.0]
    })
    Load.load_dataframe(data, table_name='weather_data', if_exists='replace')