import requests
import os
from typing import Dict, Any, List # Make sure List is used or remove if not
from datetime import datetime, date

OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

class WeatherService:
    def __init__(self, api_key: str | None = OPENWEATHERMAP_API_KEY):
        if not api_key:
            print("Warning: OpenWeatherMap API key not configured. Set the OPENWEATHERMAP_API_KEY environment variable.")
            self.api_key = None
        else:
            self.api_key = api_key
        # Changed to the forecast endpoint
        self.base_url = "http://api.openweathermap.org/data/2.5/forecast"

    def _build_api_url(self, city: str) -> str | None:
        """Builds the API URL for OpenWeatherMap forecast."""
        if not self.api_key:
            print("Error: API key is missing. Cannot build API URL.")
            return None
        return f"{self.base_url}?appid={self.api_key}&q={city}&units=metric&cnt=40"

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

    def _parse_forecast_data(self, data: Dict[str, Any], city: str) -> Dict[str, Any]:
        """Parses the forecast API response and returns structured daily forecast data."""
        if data.get("cod") != "200":
            error_message = data.get("message", f"Weather forecast for '{city}' is not available.")
            return {"status": "error", "error_message": error_message}

        forecast_list = data.get("list")
        if not forecast_list:
            return {"status": "error", "error_message": f"No forecast data found for {city}."}

        daily_forecasts: Dict[date, Dict[str, Any]] = {}

        for period in forecast_list:
            dt_timestamp = period.get("dt")
            if not dt_timestamp:
                continue

            forecast_datetime = datetime.fromtimestamp(dt_timestamp)
            forecast_date = forecast_datetime.date()

            main_data = period.get("main", {})
            temp = main_data.get("temp")
            description = period.get("weather", [{}])[0].get("description", "N/A")

            if temp is None:
                continue # Skip if essential data is missing

            if forecast_date not in daily_forecasts:
                daily_forecasts[forecast_date] = {
                    "temps": [],
                    "descriptions": {}, # To find the most common description
                    "date_str": forecast_date.strftime('%Y-%m-%d')
                }
            
            daily_forecasts[forecast_date]["temps"].append(temp)
            daily_forecasts[forecast_date]["descriptions"][description] = daily_forecasts[forecast_date]["descriptions"].get(description, 0) + 1

        processed_daily_summaries: List[Dict[str, Any]] = [] # Explicitly type here
        for forecast_date, daily_data in sorted(daily_forecasts.items()): # Sort by date
            if not daily_data["temps"]:
                continue

            min_temp = min(daily_data["temps"])
            max_temp = max(daily_data["temps"])
            # Get the most frequent description for the day
            most_common_description = max(daily_data["descriptions"], key=daily_data["descriptions"].get) if daily_data["descriptions"] else "N/A"
            
            processed_daily_summaries.append({
                "date": daily_data["date_str"],
                "min_temp_celsius": round(min_temp, 1),
                "max_temp_celsius": round(max_temp, 1),
                "description": most_common_description
            })
        
        if not processed_daily_summaries:
             return {"status": "error", "error_message": f"Could not process daily forecast data for {city}."}

        city_name_from_api = data.get("city", {}).get("name", city.title())

        return {
            "status": "success",
            "data": {
                "city": city_name_from_api,
                "daily_summaries": processed_daily_summaries,
                "forecast_source_periods": len(forecast_list)
            }
        }

    def get_forecast_for_city(self, city: str) -> Dict[str, Any]:
        """Retrieves and parses weather forecast for a city."""
        if not self.api_key:
            return {"status": "error", "error_message": "Weather service not configured (API key missing)."}

        api_url = self._build_api_url(city)
        if not api_url:
             return {"status": "error", "error_message": "Could not build API URL."}
        try:
            raw_data = self._fetch_raw_data(api_url)
            return self._parse_forecast_data(raw_data, city) # Use renamed parsing method
        except requests.exceptions.RequestException as e:
            return {"status": "error", "error_message": f"Failed to retrieve weather data for {city}: {e}"}
        except Exception as e:
            return {
                "status": "error",
                "error_message": f"An unexpected error occurred while getting weather for {city}: {str(e)}",
            }
