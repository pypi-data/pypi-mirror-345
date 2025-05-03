"""
Core functionality for blockx-weather package.
"""
import datetime
import math
from typing import Dict, List, Union, Optional, Tuple

# Constants
UNITS = {
    "metric": {"temp": "°C", "speed": "m/s"},
    "imperial": {"temp": "°F", "speed": "mph"},
    "standard": {"temp": "K", "speed": "m/s"}
}

class WeatherData:
    """Class to represent weather data"""
    
    def __init__(self, city: str, country_code: str = None):
        """
        Initialize weather data for a city.
        
        Args:
            city (str): Name of the city
            country_code (str, optional): Two-letter country code. Defaults to None.
        """
        self.city = city
        self.country_code = country_code
        self.temperature = None
        self.feels_like = None
        self.humidity = None
        self.pressure = None
        self.wind_speed = None
        self.wind_direction = None
        self.description = None
        self.icon = None
        self.timestamp = None
        self.units = "metric"
    
    def set_temperature(self, temp: float, feels_like: float = None, units: str = "metric") -> None:
        """
        Set temperature data.
        
        Args:
            temp (float): Temperature value
            feels_like (float, optional): Feels like temperature. Defaults to None.
            units (str, optional): Units ('metric', 'imperial', 'standard'). Defaults to 'metric'.
        
        Raises:
            ValueError: If invalid units are provided
        """
        if units not in UNITS:
            raise ValueError(f"Invalid units. Choose from: {', '.join(UNITS.keys())}")
        
        self.temperature = temp
        self.feels_like = feels_like
        self.units = units
    
    def set_wind(self, speed: float, direction: int = None) -> None:
        """
        Set wind data.
        
        Args:
            speed (float): Wind speed
            direction (int, optional): Wind direction in degrees. Defaults to None.
        """
        self.wind_speed = speed
        self.wind_direction = direction
    
    def set_atmosphere(self, humidity: int = None, pressure: int = None) -> None:
        """
        Set atmospheric data.
        
        Args:
            humidity (int, optional): Humidity percentage. Defaults to None.
            pressure (int, optional): Atmospheric pressure in hPa. Defaults to None.
        """
        self.humidity = humidity
        self.pressure = pressure
    
    def set_description(self, description: str, icon: str = None) -> None:
        """
        Set weather description.
        
        Args:
            description (str): Weather description
            icon (str, optional): Weather icon code. Defaults to None.
        """
        self.description = description
        self.icon = icon
    
    def set_timestamp(self, timestamp: Union[int, datetime.datetime] = None) -> None:
        """
        Set timestamp for the weather data.
        
        Args:
            timestamp (Union[int, datetime.datetime], optional): Timestamp. Defaults to current time.
        """
        if timestamp is None:
            self.timestamp = datetime.datetime.now()
        elif isinstance(timestamp, int):
            self.timestamp = datetime.datetime.fromtimestamp(timestamp)
        else:
            self.timestamp = timestamp
    
    def to_dict(self) -> Dict:
        """
        Convert weather data to dictionary.
        
        Returns:
            Dict: Weather data as dictionary
        """
        return {
            "name": self.city,
            "country": self.country_code,
            "main": {
                "temp": self.temperature,
                "feels_like": self.feels_like,
                "humidity": self.humidity,
                "pressure": self.pressure
            },
            "wind": {
                "speed": self.wind_speed,
                "deg": self.wind_direction
            },
            "weather": [{
                "description": self.description,
                "icon": self.icon
            }],
            "dt": int(self.timestamp.timestamp()) if self.timestamp else None,
            "units": self.units
        }
    
    def __str__(self) -> str:
        """
        String representation of weather data.
        
        Returns:
            str: Formatted weather data
        """
        temp_unit = UNITS[self.units]["temp"]
        speed_unit = UNITS[self.units]["speed"]
        
        result = f"Weather in {self.city}"
        if self.country_code:
            result += f", {self.country_code}"
        
        if self.description:
            result += f": {self.description.capitalize()}"
        
        result += "\n"
        
        if self.temperature is not None:
            result += f"Temperature: {self.temperature}{temp_unit}"
            if self.feels_like is not None:
                result += f" (feels like {self.feels_like}{temp_unit})"
            result += "\n"
        
        if self.humidity is not None:
            result += f"Humidity: {self.humidity}%\n"
        
        if self.pressure is not None:
            result += f"Pressure: {self.pressure} hPa\n"
        
        if self.wind_speed is not None:
            result += f"Wind Speed: {self.wind_speed} {speed_unit}"
            if self.wind_direction is not None:
                result += f" (direction: {self.wind_direction}°)"
            result += "\n"
        
        if self.timestamp:
            result += f"Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        
        return result

def create_sample_weather(city: str, temp: float = 20.0, units: str = "metric") -> WeatherData:
    """
    Create a sample weather data object for demonstration purposes.
    
    Args:
        city (str): City name
        temp (float, optional): Temperature. Defaults to 20.0.
        units (str, optional): Units ('metric', 'imperial', 'standard'). Defaults to 'metric'.
    
    Returns:
        WeatherData: Sample weather data
    """
    weather = WeatherData(city)
    weather.set_temperature(temp, temp - 2, units)
    weather.set_atmosphere(humidity=65, pressure=1013)
    weather.set_wind(speed=5.5, direction=180)
    weather.set_description("clear sky", "01d")
    weather.set_timestamp()
    return weather

def convert_temperature(temp: float, from_unit: str, to_unit: str) -> float:
    """
    Convert temperature between different units.
    
    Args:
        temp (float): Temperature value
        from_unit (str): Source unit ('metric', 'imperial', 'standard')
        to_unit (str): Target unit ('metric', 'imperial', 'standard')
    
    Returns:
        float: Converted temperature
    
    Raises:
        ValueError: If invalid units are provided
    """
    valid_units = ["metric", "imperial", "standard"]
    if from_unit not in valid_units or to_unit not in valid_units:
        raise ValueError(f"Invalid units. Choose from: {', '.join(valid_units)}")
    
    # No conversion needed
    if from_unit == to_unit:
        return temp
    
    # Convert to Kelvin first (standard)
    if from_unit == "metric":  # Celsius to Kelvin
        kelvin = temp + 273.15
    elif from_unit == "imperial":  # Fahrenheit to Kelvin
        kelvin = (temp - 32) * 5/9 + 273.15
    else:  # Already in Kelvin
        kelvin = temp
    
    # Convert from Kelvin to target unit
    if to_unit == "metric":  # Kelvin to Celsius
        return kelvin - 273.15
    elif to_unit == "imperial":  # Kelvin to Fahrenheit
        return (kelvin - 273.15) * 9/5 + 32
    else:  # Keep as Kelvin
        return kelvin

def calculate_heat_index(temp: float, humidity: float, units: str = "metric") -> float:
    """
    Calculate the heat index (feels like temperature) based on temperature and humidity.
    
    Args:
        temp (float): Temperature
        humidity (float): Relative humidity percentage
        units (str, optional): Units ('metric', 'imperial', 'standard'). Defaults to 'metric'.
    
    Returns:
        float: Heat index
    
    Raises:
        ValueError: If invalid units are provided
    """
    # Convert to Fahrenheit for the formula
    if units == "metric":
        temp_f = (temp * 9/5) + 32
    elif units == "imperial":
        temp_f = temp
    elif units == "standard":
        temp_f = (temp - 273.15) * 9/5 + 32
    else:
        raise ValueError(f"Invalid units: {units}. Choose from: metric, imperial, standard")
    
    # Heat index formula (Rothfusz regression)
    hi = 0.5 * (temp_f + 61.0 + ((temp_f - 68.0) * 1.2) + (humidity * 0.094))
    
    # If the heat index is greater than 80F, use the full regression equation
    if hi > 80:
        hi = -42.379 + 2.04901523 * temp_f + 10.14333127 * humidity
        hi += -0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2
        hi += -5.481717e-2 * humidity**2 + 1.22874e-3 * temp_f**2 * humidity
        hi += 8.5282e-4 * temp_f * humidity**2 - 1.99e-6 * temp_f**2 * humidity**2
    
    # Convert back to the original units
    if units == "metric":
        return (hi - 32) * 5/9
    elif units == "imperial":
        return hi
    else:  # standard (Kelvin)
        return (hi - 32) * 5/9 + 273.15

def calculate_wind_chill(temp: float, wind_speed: float, units: str = "metric") -> float:
    """
    Calculate the wind chill factor based on temperature and wind speed.
    
    Args:
        temp (float): Temperature
        wind_speed (float): Wind speed
        units (str, optional): Units ('metric', 'imperial', 'standard'). Defaults to 'metric'.
    
    Returns:
        float: Wind chill temperature
    
    Raises:
        ValueError: If invalid units are provided
    """
    # Convert to appropriate units for the formula
    if units == "metric":
        temp_c = temp
        wind_kph = wind_speed * 3.6  # m/s to km/h
    elif units == "imperial":
        temp_c = (temp - 32) * 5/9  # F to C
        wind_kph = wind_speed * 1.609344  # mph to km/h
    elif units == "standard":
        temp_c = temp - 273.15  # K to C
        wind_kph = wind_speed * 3.6  # m/s to km/h
    else:
        raise ValueError(f"Invalid units: {units}. Choose from: metric, imperial, standard")
    
    # Wind chill formula (North American and UK standard)
    # Valid for temperatures at or below 10°C (50°F) and wind speeds above 4.8 km/h (3 mph)
    if temp_c <= 10 and wind_kph > 4.8:
        wci = 13.12 + 0.6215 * temp_c - 11.37 * (wind_kph ** 0.16) + 0.3965 * temp_c * (wind_kph ** 0.16)
    else:
        # Return the actual temperature if conditions don't meet wind chill criteria
        wci = temp_c
    
    # Convert back to the original units
    if units == "metric":
        return wci
    elif units == "imperial":
        return wci * 9/5 + 32
    else:  # standard (Kelvin)
        return wci + 273.15

def calculate_dew_point(temp: float, humidity: float, units: str = "metric") -> float:
    """
    Calculate the dew point based on temperature and relative humidity.
    
    Args:
        temp (float): Temperature
        humidity (float): Relative humidity percentage (0-100)
        units (str, optional): Units ('metric', 'imperial', 'standard'). Defaults to 'metric'.
    
    Returns:
        float: Dew point temperature
    
    Raises:
        ValueError: If invalid units are provided
    """
    # Convert to Celsius for the formula
    if units == "metric":
        temp_c = temp
    elif units == "imperial":
        temp_c = (temp - 32) * 5/9
    elif units == "standard":
        temp_c = temp - 273.15
    else:
        raise ValueError(f"Invalid units: {units}. Choose from: metric, imperial, standard")
    
    # Constants for Magnus formula
    a = 17.27
    b = 237.7
    
    # Calculate dew point using Magnus formula
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    dew_point_c = (b * alpha) / (a - alpha)
    
    # Convert back to the original units
    if units == "metric":
        return dew_point_c
    elif units == "imperial":
        return dew_point_c * 9/5 + 32
    else:  # standard (Kelvin)
        return dew_point_c + 273.15
