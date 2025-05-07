
import pandas as pd
from extract import extract_weather_data
from transform import Transform
from load import Load
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_etl(cities: list = None, table_name: str = 'weather_data'):
    """
    Run the ELT pipeline: Extract weather data, transform it, and load it into PostgreSQL.

    Parameters:
    - cities: List of cities to fetch weather data for (default: None, uses extract.py default).
    - table_name: Name of the PostgreSQL table to load data into.
    """
    try:
        # Extract
        logger.info("Starting ETL pipeline: Extracting data...")
        df_raw = extract_weather_data(cities=cities)
        if df_raw.empty:
            logger.error("No data extracted. Aborting pipeline.")
            return
        logger.info(f"Extracted {len(df_raw)} rows.")

        # Transform
        logger.info("Transforming data...")
        transformer = Transform()
        transformer.add_clean_data(strategy='drop')
        transformer.add_format_data()
        # Optional aggregation (uncomment if needed)
        # transformer.add_aggregate_data(group_by='city', aggregations={'temperature': 'mean', 'humidity': 'mean'})
        df_transformed = transformer.apply(df_raw)
        logger.info(f"Rows after transformation: {len(df_transformed)}")
        logger.info(f"Column names: {df_transformed.columns.tolist()}")

        # Load
        logger.info("Loading data into PostgreSQL...")
        Load.load_dataframe(
            data=df_transformed,
            table_name=table_name,
            if_exists='append',
            index=False
        )

        logger.info("ETL pipeline completed successfully!")

    except Exception as e:
        logger.error(f"ETL pipeline failed: {e}")
        raise

if __name__ == "__main__":
    run_etl()

