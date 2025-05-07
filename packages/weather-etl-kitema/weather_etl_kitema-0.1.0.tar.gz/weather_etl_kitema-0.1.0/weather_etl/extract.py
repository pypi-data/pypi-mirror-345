# import requests
# import pandas as pd
# from dotenv import load_dotenv
# import os

# # Load environment variables from .env file
# load_dotenv()

# def extract_weather_data() -> pd.DataFrame:
#     """
#     Extract weather data from OpenWeather API for multiple cities.
#     Returns a pandas DataFrame with weather information.
#     """
#     # Your OpenWeather API key from .env file
#     api_key = os.getenv('OPENWEATHER_API_KEY')

#     # List of cities to fetch weather data for
#     cities = ['Nairobi', 'Mombasa', 'Kisumu', 'Eldoret']

#     # Initialize an empty list to hold the weather data
#     records = []

#     # Loop through each city and fetch the weather data
#     for city in cities:
#         # API request to fetch weather data for the city
#         try:
#             print(f"Fetching weather data for {city}...")
#             url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
#             response = requests.get(url)
#             data = response.json()

#             if response.status_code == 200:
#                 # Extracting relevant data from the response
#                 records.append({
#                     'city': data['name'],
#                     'temperature': data['main']['temp'],
#                     'humidity': data['main']['humidity'],
#                     'pressure': data['main']['pressure'],
#                     'weather_description': data['weather'][0]['description'],
#                     'timestamp': pd.to_datetime(data['dt'], unit='s')
#                 })
#             else:
#                 print(f"Failed to fetch data for {city}. Status code: {response.status_code}")

#         except Exception as e:
#             print(f"Error fetching data for {city}: {e}")

#     # Convert the list of records into a pandas DataFrame
#     df = pd.DataFrame.from_records(records)
    
#     # Return the DataFrame containing the weather data
#     return df

# # Test the function
# if __name__ == "__main__":
#     df = extract_weather_data()
#     print(df.head())
import requests
import pandas as pd
from dotenv import load_dotenv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from typing import List, Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
API_KEY = os.getenv('OPENWEATHER_API_KEY')
if not API_KEY:
    raise ValueError("OPENWEATHER_API_KEY not found in .env file")

def fetch_weather(city: str, api_key: str) -> Dict[str, Any]:
    """Fetch weather data for a single city."""
    try:
        logger.info(f"Fetching weather data for {city}...")
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()
        return {
            'city': data['name'],
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'weather_description': data['weather'][0]['description'],
            'timestamp': pd.to_datetime(data['dt'], unit='s')
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch data for {city}: {e}")
        return None
    except (KeyError, IndexError) as e:
        logger.error(f"Error parsing data for {city}: {e}")
        return None

def extract_weather_data(cities: List[str] = None) -> pd.DataFrame:
    """
    Extract weather data from OpenWeather API for multiple cities concurrently.
    Returns a pandas DataFrame with weather information.
    """
    # Default cities if none provided
    if cities is None:
        cities = ['Nairobi', 'Mombasa', 'Kisumu', 'Eldoret']

    # Fetch data concurrently
    records = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_city = {executor.submit(fetch_weather, city, API_KEY): city for city in cities}
        for future in as_completed(future_to_city):
            city = future_to_city[future]
            result = future.result()
            if result:
                records.append(result)
            else:
                logger.warning(f"No data returned for {city}")

    # Convert to DataFrame
    if not records:
        logger.error("No data fetched for any city.")
        return pd.DataFrame()
    
    df = pd.DataFrame(records)
    logger.info(f"Extracted data for {len(df)} cities.")
    return df

if __name__ == "__main__":
    df = extract_weather_data()
    print(df.head())