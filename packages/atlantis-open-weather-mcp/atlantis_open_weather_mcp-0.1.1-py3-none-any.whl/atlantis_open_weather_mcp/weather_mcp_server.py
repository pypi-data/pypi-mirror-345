# weather_mcp_server.py
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import requests
from datetime import datetime, timedelta, timezone
import os
import argparse
import signal
import sys

# Create MCP server instance
mcp = FastMCP(
    name="WeatherForecastServer",
    description="Provides global weather forecasts and current weather conditions",
    version="1.0.0"
)

# Define data models
class WindInfo(BaseModel):
    speed: str = Field(..., description="Wind speed in meters per second")
    direction: str = Field(..., description="Wind direction in degrees")

class WeatherEntry(BaseModel):
    time: str = Field(..., description="Time of the weather data")
    temperature: str = Field(..., description="Temperature in Celsius")
    feels_like: str = Field(..., description="Feels like temperature in Celsius")
    temp_min: str = Field(..., description="Minimum temperature in Celsius")
    temp_max: str = Field(..., description="Maximum temperature in Celsius")
    weather_condition: str = Field(..., description="Weather condition description")
    humidity: str = Field(..., description="Humidity percentage")
    wind: WindInfo = Field(..., description="Wind speed and direction information")
    rain: str = Field(..., description="Rainfall amount")
    clouds: str = Field(..., description="Cloud coverage percentage")

class WeatherForecast(BaseModel):
    today: List[WeatherEntry] = Field(..., description="Today's weather forecast, including current weather")
    tomorrow: List[WeatherEntry] = Field(..., description="Tomorrow's weather forecast")

# Helper function to get API key
def get_api_key(provided_key: Optional[str] = None, cli_key: Optional[str] = None) -> str:
    """
    Get API key, prioritizing:
    1. Provided key (during tool call)
    2. Command-line argument (--api-key)
    3. Environment variable (OPENWEATHER_API_KEY)

    Parameters:
        provided_key: User-provided API key (optional, from tool call)
        cli_key: API key provided via command line (optional)

    Returns:
        API key string
    """
    if provided_key:
        print("Using API key provided in tool call.")
        return provided_key

    if cli_key:
        print("Using API key provided via command line.")
        return cli_key

    env_key = os.environ.get("OPENWEATHER_API_KEY")
    if env_key:
        print("Using API key from OPENWEATHER_API_KEY environment variable.")
        return env_key

    raise ValueError("No API key provided via tool call, command line (--api-key), or environment variable (OPENWEATHER_API_KEY)")

# Core weather forecast function
def get_weather_forecast(present_location, time_zone_offset, api_key=None, cli_key=None):
    # Get API key
    try:
        # Pass cli_key from the main execution context if available
        resolved_api_key = get_api_key(api_key, cli_key)
    except ValueError as e:
        return {'error': str(e)}

    # Get geographic coordinates
    geocode_url = f"https://api.openweathermap.org/data/2.5/weather?q={present_location}&appid={resolved_api_key}&units=metric"

    try:
        # Request current weather data to get geographic coordinates
        response = requests.get(geocode_url)
        response.raise_for_status()
        data = response.json()

        lat = data['coord']['lat']
        lon = data['coord']['lon']

        # Get 5-day 3-hour forecast
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={resolved_api_key}&units=metric"

        response = requests.get(forecast_url)
        response.raise_for_status()
        forecast_data = response.json()

        # Set timezone
        tz = timezone(timedelta(hours=time_zone_offset))

        today = datetime.now(tz).date()
        tomorrow = today + timedelta(days=1)

        today_and_current_forecast = []
        tomorrow_forecast = []

        # Current weather
        current_weather = {
            'time': datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S'),
            'temperature': f"{data['main']['temp']} °C",
            'feels_like': f"{data['main']['feels_like']} °C",
            'temp_min': f"{data['main']['temp_min']} °C",
            'temp_max': f"{data['main']['temp_max']} °C",
            'weather_condition': data['weather'][0]['description'],
            'humidity': f"{data['main']['humidity']}%",
            'wind': {
                'speed': f"{data['wind']['speed']} m/s",
                'direction': f"{data['wind']['deg']} degrees"
            },
            'rain': f"{data.get('rain', {}).get('1h', 0)} mm/h" if 'rain' in data else 'No rain',
            'clouds': f"{data['clouds']['all']}%"
        }

        today_and_current_forecast.append(current_weather)

        for entry in forecast_data['list']:
            dt = datetime.fromtimestamp(entry['dt'], tz)
            if dt.date() == today:
                today_and_current_forecast.append({
                    'time': dt.strftime('%Y-%m-%d %H:%M:%S'),
                    'temperature': f"{entry['main']['temp']} °C",
                    'feels_like': f"{entry['main']['feels_like']} °C",
                    'temp_min': f"{entry['main']['temp_min']} °C",
                    'temp_max': f"{entry['main']['temp_max']} °C",
                    'weather_condition': entry['weather'][0]['description'],
                    'humidity': f"{entry['main']['humidity']}%",
                    'wind': {
                        'speed': f"{entry['wind']['speed']} m/s",
                        'direction': f"{entry['wind']['deg']} degrees"
                    },
                    'rain': f"{entry.get('rain', {}).get('3h', 0)} mm/3h" if 'rain' in entry else 'No rain',
                    'clouds': f"{entry['clouds']['all']}%"
                })
            elif dt.date() == tomorrow:
                tomorrow_forecast.append({
                    'time': dt.strftime('%Y-%m-%d %H:%M:%S'),
                    'temperature': f"{entry['main']['temp']} °C",
                    'feels_like': f"{entry['main']['feels_like']} °C",
                    'temp_min': f"{entry['main']['temp_min']} °C",
                    'temp_max': f"{entry['main']['temp_max']} °C",
                    'weather_condition': entry['weather'][0]['description'],
                    'humidity': f"{entry['main']['humidity']}%",
                    'wind': {
                        'speed': f"{entry['wind']['speed']} m/s",
                        'direction': f"{entry['wind']['deg']} degrees"
                    },
                    'rain': f"{entry.get('rain', {}).get('3h', 0)} mm/3h" if 'rain' in entry else 'No rain',
                    'clouds': f"{entry['clouds']['all']}%"
                })

        # Return current weather and forecast for today and tomorrow
        return {
            'today': today_and_current_forecast,
            'tomorrow': tomorrow_forecast
        }
    except requests.RequestException as e:
        return {'error': f"Request error: {str(e)}"}
    except ValueError as e:
        return {'error': f"JSON parsing error: {str(e)}"}
    except KeyError as e:
        return {'error': f"Data structure error: Missing key {str(e)}"}
    except Exception as e:
        return {'error': f"Unexpected error: {str(e)}"}

# Define MCP tools
# We capture the cli_api_key from the main scope if it exists
cli_key_global = None

@mcp.tool()
def get_weather(location: str, api_key: Optional[str] = None, timezone_offset: float = 0) -> Dict[str, Any]:
    """
    Get current weather and forecast for a specified location

    Parameters:
        location: Location name, e.g., "Beijing", "New York", "Tokyo"
        api_key: OpenWeatherMap API key (optional, will read from environment variable if not provided)
        timezone_offset: Timezone offset in hours, e.g., 8 for Beijing, -4 for New York. Default is 0 (UTC time)

    Returns:
        Dictionary containing today's and tomorrow's weather forecast
    """
    # Call weather forecast function, passing the globally stored CLI key
    return get_weather_forecast(location, timezone_offset, api_key, cli_key_global) # type: ignore

@mcp.tool()
def get_current_weather(location: str, api_key: Optional[str] = None, timezone_offset: float = 0) -> Dict[str, Any]:
    """
    Get current weather for a specified location

    Parameters:
        location: Location name, e.g., "Beijing", "New York", "Tokyo"
        api_key: OpenWeatherMap API key (optional, will read from environment variable if not provided)
        timezone_offset: Timezone offset in hours, e.g., 8 for Beijing, -4 for New York. Default is 0 (UTC time)

    Returns:
        Current weather information
    """
    # Get full weather information, passing the globally stored CLI key
    full_weather = get_weather(location, api_key, timezone_offset) # get_weather now passes cli_key_global implicitly

    # Check if an error occurred
    if 'error' in full_weather:
        return full_weather

    # Only return current weather (first entry of today)
    if full_weather['today'] and len(full_weather['today']) > 0:
        return full_weather['today'][0]
    else:
        return {"error": "Unable to get current weather information"}


# Define the main execution function
def main():
    # --- Signal Handler Setup ---
    def handle_sigint(signum, frame):
        print("\nCtrl+C detected. Shutting down server...")
        # In a more complex server, you might call mcp.stop() or similar here
        # For stdio transport, exiting the process is usually sufficient
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_sigint)
    # ---------------------------

    parser = argparse.ArgumentParser(description="Weather MCP Server")
    parser.add_argument('--api-key', type=str, help='OpenWeatherMap API Key')
    args = parser.parse_args()

    # Store CLI key globally for tool functions to access if needed
    global cli_key_global  # Ensure we modify the global variable
    cli_key_global = args.api_key

    # Check if API key is available from CLI or ENV
    api_key_available = False
    if args.api_key:
        print("API key provided via --api-key argument.")
        api_key_available = True
    elif os.environ.get("OPENWEATHER_API_KEY"):
        print("API key found in OPENWEATHER_API_KEY environment variable.")
        api_key_available = True
    else:
        print("ERROR: No API key provided via --api-key or environment variable OPENWEATHER_API_KEY.")
        print("Please provide the key using either method.")
        exit(1) # Exit if no key is available on startup

    # Fetch and print weather for Nuuk, Greenland on startup
    print("\nFetching startup weather for Nuuk, Greenland...")
    try:
        # Call get_current_weather, it will use cli_key_global or ENV var internally
        startup_weather = get_current_weather(location="Nuuk, Greenland", timezone_offset=-2) # Nuuk is UTC-2
        if 'error' in startup_weather:
            print(f"ERROR fetching startup weather: {startup_weather['error']}")
        else:
            # Pretty print the result if successful
            import json
            print(f"Current weather in Nuuk:\n{json.dumps(startup_weather, indent=2)}")
    except Exception as e:
        print(f"An unexpected error occurred during startup weather fetch: {e}")
    print("\nStarting MCP server...")

    print("Weather Forecast MCP Server running...")
    mcp.run(transport='stdio')


# Start server by calling main when the script is run directly
if __name__ == "__main__":
    main()
