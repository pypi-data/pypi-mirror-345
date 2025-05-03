"""
blockx-weather - A Python package for weather data processing and calculations
"""

from .core import (
    WeatherData,
    create_sample_weather,
    convert_temperature,
    calculate_heat_index,
    calculate_wind_chill,
    calculate_dew_point,
    UNITS
)

__version__ = "0.1.0"
