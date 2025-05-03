"""
Tests for the blockx-weather package core functionality.
"""
import unittest
import datetime
from blockx_weather.core import (
    WeatherData,
    create_sample_weather,
    convert_temperature,
    calculate_heat_index,
    calculate_wind_chill,
    calculate_dew_point
)

class TestWeatherData(unittest.TestCase):
    """Test cases for WeatherData class."""
    
    def test_weather_data_initialization(self):
        """Test WeatherData initialization."""
        weather = WeatherData("London", "GB")
        self.assertEqual(weather.city, "London")
        self.assertEqual(weather.country_code, "GB")
        self.assertEqual(weather.units, "metric")
        self.assertIsNone(weather.temperature)
        self.assertIsNone(weather.feels_like)
    
    def test_set_temperature(self):
        """Test setting temperature data."""
        weather = WeatherData("London")
        weather.set_temperature(20.5, 19.8, "imperial")
        self.assertEqual(weather.temperature, 20.5)
        self.assertEqual(weather.feels_like, 19.8)
        self.assertEqual(weather.units, "imperial")
    
    def test_set_temperature_invalid_units(self):
        """Test setting temperature with invalid units."""
        weather = WeatherData("London")
        with self.assertRaises(ValueError):
            weather.set_temperature(20.5, 19.8, "invalid_unit")
    
    def test_set_wind(self):
        """Test setting wind data."""
        weather = WeatherData("London")
        weather.set_wind(5.5, 180)
        self.assertEqual(weather.wind_speed, 5.5)
        self.assertEqual(weather.wind_direction, 180)
    
    def test_set_atmosphere(self):
        """Test setting atmospheric data."""
        weather = WeatherData("London")
        weather.set_atmosphere(humidity=65, pressure=1013)
        self.assertEqual(weather.humidity, 65)
        self.assertEqual(weather.pressure, 1013)
    
    def test_set_description(self):
        """Test setting weather description."""
        weather = WeatherData("London")
        weather.set_description("clear sky", "01d")
        self.assertEqual(weather.description, "clear sky")
        self.assertEqual(weather.icon, "01d")
    
    def test_set_timestamp(self):
        """Test setting timestamp."""
        weather = WeatherData("London")
        # Test with no argument (current time)
        weather.set_timestamp()
        self.assertIsInstance(weather.timestamp, datetime.datetime)
        
        # Test with integer timestamp
        weather.set_timestamp(1609459200)  # 2021-01-01 00:00:00
        self.assertEqual(weather.timestamp.year, 2021)
        self.assertEqual(weather.timestamp.month, 1)
        self.assertEqual(weather.timestamp.day, 1)
        
        # Test with datetime object
        dt = datetime.datetime(2022, 1, 1)
        weather.set_timestamp(dt)
        self.assertEqual(weather.timestamp, dt)
    
    def test_to_dict(self):
        """Test converting weather data to dictionary."""
        weather = WeatherData("London", "GB")
        weather.set_temperature(20.5, 19.8, "metric")
        weather.set_atmosphere(humidity=65, pressure=1013)
        weather.set_wind(speed=5.5, direction=180)
        weather.set_description("clear sky", "01d")
        dt = datetime.datetime(2022, 1, 1)
        weather.set_timestamp(dt)
        
        data = weather.to_dict()
        self.assertEqual(data["name"], "London")
        self.assertEqual(data["country"], "GB")
        self.assertEqual(data["main"]["temp"], 20.5)
        self.assertEqual(data["main"]["feels_like"], 19.8)
        self.assertEqual(data["main"]["humidity"], 65)
        self.assertEqual(data["main"]["pressure"], 1013)
        self.assertEqual(data["wind"]["speed"], 5.5)
        self.assertEqual(data["wind"]["deg"], 180)
        self.assertEqual(data["weather"][0]["description"], "clear sky")
        self.assertEqual(data["weather"][0]["icon"], "01d")
        self.assertEqual(data["dt"], int(dt.timestamp()))
        self.assertEqual(data["units"], "metric")

class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""
    
    def test_create_sample_weather(self):
        """Test creating sample weather data."""
        weather = create_sample_weather("London", 25.0, "imperial")
        self.assertEqual(weather.city, "London")
        self.assertEqual(weather.temperature, 25.0)
        self.assertEqual(weather.units, "imperial")
        self.assertIsNotNone(weather.humidity)
        self.assertIsNotNone(weather.pressure)
        self.assertIsNotNone(weather.wind_speed)
        self.assertIsNotNone(weather.description)
    
    def test_convert_temperature(self):
        """Test temperature conversion."""
        # Celsius to Fahrenheit
        self.assertAlmostEqual(convert_temperature(0, "metric", "imperial"), 32.0, places=1)
        self.assertAlmostEqual(convert_temperature(100, "metric", "imperial"), 212.0, places=1)
        
        # Fahrenheit to Celsius
        self.assertAlmostEqual(convert_temperature(32, "imperial", "metric"), 0.0, places=1)
        self.assertAlmostEqual(convert_temperature(212, "imperial", "metric"), 100.0, places=1)
        
        # Celsius to Kelvin
        self.assertAlmostEqual(convert_temperature(0, "metric", "standard"), 273.15, places=1)
        
        # Kelvin to Celsius
        self.assertAlmostEqual(convert_temperature(273.15, "standard", "metric"), 0.0, places=1)
        
        # No conversion needed
        self.assertEqual(convert_temperature(20, "metric", "metric"), 20)
    
    def test_convert_temperature_invalid_units(self):
        """Test temperature conversion with invalid units."""
        with self.assertRaises(ValueError):
            convert_temperature(20, "invalid_unit", "metric")
        
        with self.assertRaises(ValueError):
            convert_temperature(20, "metric", "invalid_unit")
    
    def test_calculate_heat_index(self):
        """Test heat index calculation."""
        # Test with metric units (Celsius)
        hi_metric = calculate_heat_index(30.0, 80.0, "metric")
        self.assertGreater(hi_metric, 30.0)  # Heat index should be higher than actual temperature
        
        # Test with imperial units (Fahrenheit)
        hi_imperial = calculate_heat_index(86.0, 80.0, "imperial")
        self.assertGreater(hi_imperial, 86.0)
        
        # Test with standard units (Kelvin)
        hi_standard = calculate_heat_index(303.15, 80.0, "standard")
        self.assertGreater(hi_standard, 303.15)
    
    def test_calculate_wind_chill(self):
        """Test wind chill calculation."""
        # Test with metric units (Celsius)
        wc_metric = calculate_wind_chill(5.0, 20.0, "metric")
        self.assertLess(wc_metric, 5.0)  # Wind chill should be lower than actual temperature
        
        # Test with imperial units (Fahrenheit)
        wc_imperial = calculate_wind_chill(41.0, 15.0, "imperial")
        self.assertLess(wc_imperial, 41.0)
        
        # Test with standard units (Kelvin)
        wc_standard = calculate_wind_chill(278.15, 20.0, "standard")
        self.assertLess(wc_standard, 278.15)
        
        # Test with temperature above 10°C (should return actual temperature)
        wc_high_temp = calculate_wind_chill(15.0, 20.0, "metric")
        self.assertEqual(wc_high_temp, 15.0)
    
    def test_calculate_dew_point(self):
        """Test dew point calculation."""
        # Test with metric units (Celsius)
        dp_metric = calculate_dew_point(20.0, 65.0, "metric")
        self.assertLess(dp_metric, 20.0)  # Dew point should be lower than actual temperature
        
        # Test with imperial units (Fahrenheit)
        dp_imperial = calculate_dew_point(68.0, 65.0, "imperial")
        self.assertLess(dp_imperial, 68.0)
        
        # Test with standard units (Kelvin)
        dp_standard = calculate_dew_point(293.15, 65.0, "standard")
        self.assertLess(dp_standard, 293.15)
