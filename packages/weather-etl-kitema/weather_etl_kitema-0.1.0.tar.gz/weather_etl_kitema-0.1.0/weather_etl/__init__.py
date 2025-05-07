# src/weather_etl/__init__.py

# Package version
__version__ = "0.1.0"

# Import the main functionality to expose it at the package level
from .etl import run_etl

# Optionally expose key classes if users might need direct access
from .extract import extract_weather_data
from .transform import Transform
from .load import Load

# Define what gets imported with "from weather_etl import *"
__all__ = [
    "run_etl",
    "extract_weather_data",
    "Transform",
    "Load",
]