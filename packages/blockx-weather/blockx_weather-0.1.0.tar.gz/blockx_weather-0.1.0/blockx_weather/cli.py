"""
Command-line interface for blockx-weather package.
"""
import argparse
import sys
from .core import (
    WeatherData, 
    create_sample_weather, 
    convert_temperature, 
    calculate_heat_index, 
    calculate_wind_chill,
    calculate_dew_point
)

def main():
    """
    Main entry point for the CLI application.
    """
    parser = argparse.ArgumentParser(description="BlockX Weather - Weather calculation utilities")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Sample weather command
    sample_parser = subparsers.add_parser("sample", help="Generate sample weather data")
    sample_parser.add_argument("city", help="Name of the city")
    sample_parser.add_argument("--temp", type=float, default=20.0, help="Temperature value")
    sample_parser.add_argument("--units", 
                        choices=["metric", "imperial", "standard"], 
                        default="metric", 
                        help="Units of measurement (metric=Celsius, imperial=Fahrenheit, standard=Kelvin)")
    
    # Temperature conversion command
    convert_parser = subparsers.add_parser("convert", help="Convert temperature between units")
    convert_parser.add_argument("temp", type=float, help="Temperature value to convert")
    convert_parser.add_argument("--from", dest="from_unit", 
                        choices=["metric", "imperial", "standard"], 
                        default="metric", 
                        help="Source units (metric=Celsius, imperial=Fahrenheit, standard=Kelvin)")
    convert_parser.add_argument("--to", dest="to_unit", 
                        choices=["metric", "imperial", "standard"], 
                        default="imperial", 
                        help="Target units (metric=Celsius, imperial=Fahrenheit, standard=Kelvin)")
    
    # Heat index command
    heat_parser = subparsers.add_parser("heat-index", help="Calculate heat index (feels like temperature)")
    heat_parser.add_argument("temp", type=float, help="Temperature value")
    heat_parser.add_argument("humidity", type=float, help="Relative humidity (0-100)%")
    heat_parser.add_argument("--units", 
                        choices=["metric", "imperial", "standard"], 
                        default="metric", 
                        help="Units of measurement (metric=Celsius, imperial=Fahrenheit, standard=Kelvin)")
    
    # Wind chill command
    wind_parser = subparsers.add_parser("wind-chill", help="Calculate wind chill factor")
    wind_parser.add_argument("temp", type=float, help="Temperature value")
    wind_parser.add_argument("wind_speed", type=float, help="Wind speed")
    wind_parser.add_argument("--units", 
                        choices=["metric", "imperial", "standard"], 
                        default="metric", 
                        help="Units of measurement (metric=Celsius, imperial=Fahrenheit, standard=Kelvin)")
    
    # Dew point command
    dew_parser = subparsers.add_parser("dew-point", help="Calculate dew point")
    dew_parser.add_argument("temp", type=float, help="Temperature value")
    dew_parser.add_argument("humidity", type=float, help="Relative humidity (0-100)%")
    dew_parser.add_argument("--units", 
                        choices=["metric", "imperial", "standard"], 
                        default="metric", 
                        help="Units of measurement (metric=Celsius, imperial=Fahrenheit, standard=Kelvin)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    try:
        if args.command == "sample":
            weather = create_sample_weather(args.city, args.temp, args.units)
            print(weather)
            
        elif args.command == "convert":
            converted = convert_temperature(args.temp, args.from_unit, args.to_unit)
            from_symbol = "°C" if args.from_unit == "metric" else "°F" if args.from_unit == "imperial" else "K"
            to_symbol = "°C" if args.to_unit == "metric" else "°F" if args.to_unit == "imperial" else "K"
            print(f"{args.temp}{from_symbol} = {converted:.2f}{to_symbol}")
            
        elif args.command == "heat-index":
            heat_index = calculate_heat_index(args.temp, args.humidity, args.units)
            temp_symbol = "°C" if args.units == "metric" else "°F" if args.units == "imperial" else "K"
            print(f"Temperature: {args.temp}{temp_symbol}")
            print(f"Humidity: {args.humidity}%")
            print(f"Heat Index (Feels Like): {heat_index:.2f}{temp_symbol}")
            
        elif args.command == "wind-chill":
            wind_chill = calculate_wind_chill(args.temp, args.wind_speed, args.units)
            temp_symbol = "°C" if args.units == "metric" else "°F" if args.units == "imperial" else "K"
            speed_unit = "m/s" if args.units in ["metric", "standard"] else "mph"
            print(f"Temperature: {args.temp}{temp_symbol}")
            print(f"Wind Speed: {args.wind_speed} {speed_unit}")
            print(f"Wind Chill: {wind_chill:.2f}{temp_symbol}")
            
        elif args.command == "dew-point":
            dew_point = calculate_dew_point(args.temp, args.humidity, args.units)
            temp_symbol = "°C" if args.units == "metric" else "°F" if args.units == "imperial" else "K"
            print(f"Temperature: {args.temp}{temp_symbol}")
            print(f"Humidity: {args.humidity}%")
            print(f"Dew Point: {dew_point:.2f}{temp_symbol}")
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
