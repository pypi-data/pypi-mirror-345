# Unofficial QWeather MCP

An unofficial MCP (Multiagent Conversation Protocol) wrapper for the QWeather API. This package provides tools to easily access QWeather's comprehensive weather data services through MCP, allowing integration with AI agents, chatbots, and other applications.

## Features

- **City Lookup**: Search for cities by name, coordinates, LocationID or Adcode
- **POI Lookup**: Find points of interest like scenic spots and stations
- **Real-time Weather**: Get current weather conditions for global locations
- **Weather Forecasts**: Daily forecasts for 3-30 days and hourly forecasts up to 7 days
- **Weather Warnings**: Access real-time disaster warnings and warning lists by region
- **Weather Indices**: Get lifestyle indices like UV index, sports conditions, etc.
- **Air Quality**: Real-time and forecast air quality data with detailed pollutant information

## Installation

```bash
pip install unoff-qweather-mcp
```

## Authentication

This package requires a QWeather API key. You'll need to:

1. Register for an account at [QWeather Developer Platform](https://dev.qweather.com/)
2. Create an API key in the developer console
3. Set the following environment variables:

```bash
export QWEATHER_API_KEY="your_api_key_here"
export QWEATHER_API_HOST="api.qweather.com"  # or another appropriate host based on your subscription
```

The API host depends on your subscription tier. See [QWeather API Configuration](https://dev.qweather.com/docs/configuration/api-config/#api-host) for details.

## Usage


### Running as an Claude MCP


macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

Windows: `%APPDATA%\Claude\claude_desktop_config.json`



```bash
# Clone and config the env
git clone https://github.com/HongpengM/unoff-qweather-mcp.git

# Set up your environment variables by copying the example file
copy env.example .env

# Run the MCP server
uv --directory /path/to/your_dir run src/unoff_qweather/qweather.py
```

Using the published version:

```json
{
  "mcpServers": {
    "qweather": {
      "command": "uvx",
      "args": [
        "unoff-qweather-mcp"
      ],
      "env": {
        "QWEATHER_API_KEY": "your_api_key_here",
        "QWEATHER_API_HOST": "api.qweather.com" 
      }
    }
  }
}
```


For local pulled repository: 
```json
{
  "mcpServers": {
    "qweather": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your_dir",
        "run",
        "src/unoff_qweather/qweather.py"
      ],
      "env": {
        "QWEATHER_API_KEY": "your_api_key_here",
        "QWEATHER_API_HOST": "api.qweather.com" 
      }
    }
  }
}
```

## Available Tools

This package provides the following MCP tools:

- `lookup_city` - Search for cities by name or coordinates
- `lookup_poi` - Find points of interest
- `weather_now` - Get current weather conditions
- `weather_forecast_days` - Get daily weather forecasts (3-30 days)
- `weather_forecast_hours` - Get hourly weather forecasts (24-168 hours)
- `warning_city_list` - Get cities with active weather warnings
- `weather_warning` - Get detailed weather warnings for a location
- `weather_indices` - Get lifestyle indices (UV, sports, etc.)
- `air_quality_now` - Get current air quality data
- `air_quality_forecast` - Get air quality forecasts

For detailed parameter information, see each function's docstring in the code.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This is an unofficial wrapper and not affiliated with or endorsed by QWeather. Users must comply with QWeather's terms of service when using this package.
