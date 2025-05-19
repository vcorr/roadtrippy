import requests
import os
from typing import Dict, Any

OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

class WeatherService:
    def __init__(self, api_key: str | None = OPENWEATHERMAP_API_KEY):
        if not api_key:
            print("Warning: OpenWeatherMap API key not configured. Set the OPENWEATHERMAP_API_KEY environment variable.")
            self.api_key = None
        else:
            self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    def _build_api_url(self, city: str) -> str | None:
        """Builds the API URL for OpenWeatherMap."""
        if not self.api_key:
            print("Error: API key is missing. Cannot build API URL.")
            return None
        return f"{self.base_url}?appid={self.api_key}&q={city}&units=metric"

    def _fetch_raw_data(self, url: str) -> Dict[str, Any]:
        """Fetches raw weather data from the given URL."""
        try:
            response = requests.get(url)
            response.raise_for_status() # Raise an error for bad responses
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            raise
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred: {req_err}") 
            raise

    def _parse_weather_data(self, data: Dict[str, Any], city: str) -> Dict[str, Any]: # Renamed and changed return type
        """Parses the API response and returns structured data."""
        if data.get("cod") != 200: # Check for API error code
            error_message = data.get("message", f"Weather information for '{city}' is not available.")
            return {"status": "error", "error_message": error_message}

        main_data = data.get("main", {})
        description = data.get("weather", [{}])[0].get("description", "N/A")
        temp_celsius = main_data.get("temp")

        if temp_celsius is None:
            return {"status": "error", "error_message": f"Temperature data not available for {city}."}

        return {
            "status": "success",
            "data": {
                "city": city.title(), # Store the original city name as passed, or titleized
                "temperature_celsius": temp_celsius,
                "description": description
            }
        }

    def get_weather_for_city(self, city: str) -> Dict[str, Any]: # Changed return type
        """Retrieves and formats weather for a city."""
        if not self.api_key:
            return {"status": "error", "error_message": "Weather service not configured (API key missing)."}

        api_url = self._build_api_url(city)
        if not api_url: 
             return {"status": "error", "error_message": "Could not build API URL."}
        try:
            raw_data = self._fetch_raw_data(api_url)
            return self._parse_weather_data(raw_data, city) # Use renamed method
        except requests.exceptions.RequestException as e:
            return {"status": "error", "error_message": f"Failed to retrieve weather data for {city}: {e}"}
        except Exception as e:
            return {
                "status": "error",
                "error_message": f"An unexpected error occurred while getting weather for {city}: {str(e)}",
            }
