import os
import copy
import httpx
from asyncio import sleep
from dotenv import load_dotenv
 
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("unoff-qweather-mcp")
'''

Get API Key from local environment variable "QWEATHER_API_KEY", for getting an api key, please visit https://dev.qweather.com/ for more information.

Get API Host from local environment variable "QWEATHER_API_HOST", for getting an api host, please visit https://dev.qweather.com/docs/configuration/api-config/#api-host for more information.
'''
# Load environment variables from .env file if present
load_dotenv()

api_key = os.getenv("QWEATHER_API_KEY")
api_host = os.getenv("QWEATHER_API_HOST")
if api_host == None or api_key == None:
    raise ValueError("QWEATHER_API_KEY or QWEATHER_API_HOST is not set")
api_host = api_host.replace("https://", "").replace("http://", "")


@mcp.tool()
async def lookup_city(location, adm=None, range=None, number=None, lang=None):
    '''
    Lookup city by location name, coordinates, LocationID, or Adcode.
    
    Parameters:
    - location (required): City name, coordinates (comma-separated longitude,latitude), 
      LocationID or Adcode (China only). Supports fuzzy search with minimum 1 Chinese character or 2 letters.
    - adm (optional): Administrative division to narrow search and filter results.
    - range (optional): Limit search to specific country/region using ISO 3166 country code.
    - number (optional): Number of results to return (1-20, default is 10).
    - lang (optional): Language setting for the response.
    '''
    params = {
        "location": location
    }
    
    # Add optional parameters if provided
    if adm is not None:
        params["adm"] = adm
    if range is not None:
        params["range"] = range
    if number is not None:
        params["number"] = number
    if lang is not None:
        params["lang"] = lang
    
    # Set up headers with API key authentication
    headers = {
        "X-QW-Api-Key": api_key,
        "Accept-Encoding": "gzip"
    }
        
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://{api_host}/geo/v2/city/lookup", 
            params=params,
            headers=headers
        )
        return response.json()


@mcp.tool()
async def lookup_poi(location, type, city=None, number=None, lang=None):
    '''
    Lookup POI (Points of Interest) information by keyword and coordinates.
    
    Parameters:
    - location (required): Location to search, can be text, coordinates (comma-separated longitude,latitude), 
      LocationID or Adcode (China only).
    - type (required): POI type to search. Options include:
      'scenic' (scenic spots), 'CSTA' (tide stations), 'TSTA' (tidal current stations)
    - city (optional): Limit search to specific city. Can be city name or LocationID.
    - number (optional): Number of results to return (1-20, default is 10).
    - lang (optional): Language setting for the response.
    '''
    params = {
        "location": location,
        "type": type
    }
    
    # Add optional parameters if provided
    if city is not None:
        params["city"] = city
    if number is not None:
        params["number"] = number
    if lang is not None:
        params["lang"] = lang
    
    # Set up headers with API key authentication
    headers = {
        "X-QW-Api-Key": api_key,
        "Accept-Encoding": "gzip"
    }
        
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://{api_host}/geo/v2/poi/lookup", 
            params=params,
            headers=headers
        )
        return response.json()


@mcp.tool()
async def weather_now(location, lang=None, unit=None):
    '''
    Get real-time weather data for over 3000+ cities in China and 200,000+ cities worldwide.
    
    Parameters:
    - location (required): LocationID or coordinates (comma-separated longitude,latitude).
      LocationID can be obtained via the GeoAPI.
    - lang (optional): Language setting for the response.
    - unit (optional): Unit of measurement, 'm' for metric (default) or 'i' for imperial.
    
    Returns weather data including temperature, feels-like temperature, wind direction and speed,
    relative humidity, atmospheric pressure, precipitation, visibility, dew point, cloud cover, etc.
    
    Note: Real-time data has a 5-20 minute delay compared to the actual physical world.
    Check obsTime in the response for the accurate time of the data.
    '''
    params = {
        "location": location
    }
    
    # Add optional parameters if provided
    if lang is not None:
        params["lang"] = lang
    if unit is not None:
        params["unit"] = unit
    
    # Set up headers with API key authentication
    headers = {
        "X-QW-Api-Key": api_key,
        "Accept-Encoding": "gzip"
    }
        
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://{api_host}/v7/weather/now", 
            params=params,
            headers=headers
        )
        return response.json()


@mcp.tool()
async def weather_forecast_days(location, days=3, lang=None, unit=None):
    '''
    Get daily weather forecast for global cities for 3 to 30 days.
    
    Parameters:
    - location (required): LocationID or coordinates (comma-separated longitude,latitude).
      LocationID can be obtained via the GeoAPI.
    - days (optional): Number of forecast days. If not a valid API value (3,7,10,15,30), 
      will use the next higher valid option. Values above 30 will return 30 days. Default is 3.
    - lang (optional): Language setting for the response.
    - unit (optional): Unit of measurement, 'm' for metric (default) or 'i' for imperial.
    
    Returns daily forecast data including:
    - Sunrise and sunset times
    - Moonrise and moonset times
    - Maximum and minimum temperatures
    - Day and night weather conditions
    - Wind direction, speed and scale
    - Relative humidity
    - Atmospheric pressure
    - Precipitation
    - UV index
    - Visibility
    - Cloud cover
    - And more
    '''
    # Validate days parameter
    valid_days = [3, 7, 10, 15, 30]
    
    # Cap at 30 days
    if days > 30:
        days = 30
    # Find the next higher valid option if not a valid value
    elif days not in valid_days:
        for valid_day in valid_days:
            if valid_day >= days:
                days = valid_day
                break
        
    params = {
        "location": location
    }
    
    # Add optional parameters if provided
    if lang is not None:
        params["lang"] = lang
    if unit is not None:
        params["unit"] = unit
    
    # Set up headers with API key authentication
    headers = {
        "X-QW-Api-Key": api_key,
        "Accept-Encoding": "gzip"
    }
        
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://{api_host}/v7/weather/{days}d", 
            params=params,
            headers=headers
        )
        return response.json()


@mcp.tool()
async def weather_forecast_hours(location, hours=24, lang=None, unit=None):
    '''
    Get hourly weather forecast for global cities for a extended period.
    
    Parameters:
    - location (required): LocationID or coordinates (comma-separated longitude,latitude).
      LocationID can be obtained via the GeoAPI.
    - hours (optional): Number of forecast hours. If not a valid API value (24,72,168), 
      will use the next higher valid option. Values above 168 will return 168 hours. Default is 24.
    - lang (optional): Language setting for the response.
    - unit (optional): Unit of measurement, 'm' for metric (default) or 'i' for imperial.
    
    Returns hourly forecast data including:
    - Temperature
    - Weather conditions
    - Wind direction, speed and scale
    - Relative humidity
    - Atmospheric pressure
    - Precipitation probability
    - Cloud cover
    - Dew point
    - And more
    '''
    # Validate hours parameter
    valid_hours = [24, 72, 168]
    
    # Cap at 168 hours (7 days)
    if hours > 168:
        hours = 168
    # Find the next higher valid option if not a valid value
    elif hours not in valid_hours:
        for valid_hour in valid_hours:
            if valid_hour >= hours:
                hours = valid_hour
                break
        
    params = {
        "location": location
    }
    
    # Add optional parameters if provided
    if lang is not None:
        params["lang"] = lang
    if unit is not None:
        params["unit"] = unit
    
    # Set up headers with API key authentication
    headers = {
        "X-QW-Api-Key": api_key,
        "Accept-Encoding": "gzip"
    }
        
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://{api_host}/v7/weather/{hours}h", 
            params=params,
            headers=headers
        )
        return response.json()


@mcp.tool()
async def warning_city_list(range="cn"):
    '''
    Get a list of cities with active weather disaster warnings for a specified country or region.
    
    Parameters:
    - range (required): Country or region in ISO 3166 format, e.g., 'cn' for China or 'hk' for Hong Kong.
      Currently, this feature only supports regions within China (including Hong Kong, Macau, and Taiwan).
      Default is 'cn'.
    
    Returns a list of LocationIDs for cities that currently have active weather warnings.
    These LocationIDs can be used with other weather API calls to get detailed warning information.
    
    Note: For countries and regions outside China, please use the weather disaster warning API directly.
    '''
    params = {
        "range": range
    }
    
    # Set up headers with API key authentication
    headers = {
        "X-QW-Api-Key": api_key,
        "Accept-Encoding": "gzip"
    }
        
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://{api_host}/v7/warning/list", 
            params=params,
            headers=headers
        )
        return response.json()


@mcp.tool()
async def weather_warning(location, lang=None):
    '''
    Get real-time weather disaster warnings for a specific location.
    
    Parameters:
    - location (required): LocationID or coordinates (comma-separated longitude,latitude).
      LocationID can be obtained via the GeoAPI.
    - lang (optional): Language setting for the response.
    
    Returns weather warning data including:
    - Warning ID
    - Publishing organization
    - Publication time
    - Warning title and detailed text
    - Start and end time
    - Status (active, etc.)
    - Severity level and color
    - Warning type and type name
    
    Note: If there are no active warnings for the location, the warning field in the response will be empty.
    '''
    params = {
        "location": location
    }
    
    # Add optional parameters if provided
    if lang is not None:
        params["lang"] = lang
    
    # Set up headers with API key authentication
    headers = {
        "X-QW-Api-Key": api_key,
        "Accept-Encoding": "gzip"
    }
        
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://{api_host}/v7/warning/now", 
            params=params,
            headers=headers
        )
        return response.json()


@mcp.tool()
async def weather_indices(location, type, days=1, lang=None):
    '''
    Get weather lifestyle indices forecast data for cities in China and globally.
    
    Parameters:
    - location (required): LocationID or coordinates (comma-separated longitude,latitude).
      LocationID can be obtained via the GeoAPI.
    - type (required): Weather index type IDs, can be a single ID or multiple IDs separated by commas.
      Common indices include:
      1: Sport, 2: Car Wash, 3: Clothing, 4: Cold/Flu, 5: Tourism, 6: UV, 7: Air Pollution, 
      8: AC, 9: Allergy, 10: Sunglasses, 11: Makeup, 12: Drying, 13: Traffic, 14: Fishing, 15: Sunscreen
      Note: Not all indices are available for all cities.
    - days (optional): Number of days to forecast, valid values are 1 or 3. Default is 1.
    - lang (optional): Language setting for the response.
    
    Returns weather indices data including:
    - Index date
    - Index type and name
    - Index level and category
    - Detailed description text
    '''
    # Validate days parameter
    if days != 1 and days != 3:
        days = 1  # Default to 1 day if invalid value provided
        
    params = {
        "location": location,
        "type": type
    }
    
    # Add optional parameters if provided
    if lang is not None:
        params["lang"] = lang
    
    # Set up headers with API key authentication
    headers = {
        "X-QW-Api-Key": api_key,
        "Accept-Encoding": "gzip"
    }
        
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://{api_host}/v7/indices/{days}d", 
            params=params,
            headers=headers
        )
        return response.json()


@mcp.tool()
async def air_quality_now(latitude, longitude, lang=None):
    '''
    Get real-time air quality data for a specific location with 1x1 km precision.
    
    Parameters:
    - latitude (required): Latitude of the location. Decimal, supports up to two decimal places.
    - longitude (required): Longitude of the location. Decimal, supports up to two decimal places.
    - lang (optional): Language setting for the response.
    
    Returns detailed air quality data including:
    - Air Quality Index (AQI) based on local standards and QWeather universal AQI
    - AQI level, category, color and primary pollutant
    - Pollutant concentrations and sub-indices
    - Health recommendations for general and sensitive populations
    - Related monitoring station information
    '''
    params = {}
    
    # Add optional parameters if provided
    if lang is not None:
        params["lang"] = lang
    
    # Set up headers with API key authentication
    headers = {
        "X-QW-Api-Key": api_key,
        "Accept-Encoding": "gzip"
    }
        
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://{api_host}/airquality/v1/current/{latitude}/{longitude}", 
            params=params,
            headers=headers
        )
        return response.json()


@mcp.tool()
async def air_quality_forecast(latitude, longitude, lang=None):
    '''
    Get air quality forecast for the next 3 days, including AQI, pollutant concentrations, 
    and health recommendations.
    
    Parameters:
    - latitude (required): Latitude of the location. Decimal, supports up to two decimal places.
    - longitude (required): Longitude of the location. Decimal, supports up to two decimal places.
    - lang (optional): Language setting for the response.
    
    Returns daily forecast data for the next 3 days including:
    - Forecast start and end times
    - Air Quality Indices (AQI) from different standards
    - AQI level, category, color and primary pollutant
    - Pollutant concentrations and sub-indices
    - Health recommendations for general and sensitive populations
    '''
    params = {}
    
    # Add optional parameters if provided
    if lang is not None:
        params["lang"] = lang
    
    # Set up headers with API key authentication
    headers = {
        "X-QW-Api-Key": api_key,
        "Accept-Encoding": "gzip"
    }
        
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://{api_host}/airquality/v1/daily/{latitude}/{longitude}", 
            params=params,
            headers=headers
        )
        return response.json()


if __name__ == "__main__":
    mcp.run()