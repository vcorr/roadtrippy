from typing import Dict, Any, List # Added List
from google.adk.agents import Agent  # type: ignore

from dotenv import load_dotenv # type: ignore
load_dotenv() # Added to load .env file

from .weather_service import WeatherService # Import the service

try:
    weather_service_instance = WeatherService()
except ValueError as e: # Catch potential API key configuration errors from WeatherService __init__
    print(f"Error initializing WeatherService: {e}")
    # Fallback: create a dummy instance or handle as critical error
    # For now, if it fails, get_weather will report the service is unavailable.
    weather_service_instance = None

def get_weather_forecast(city: str) -> Dict[str, Any]: # Changed return type
    """Retrieves the weather forecast for a specified city.
    Args:
        city (str): The name of the city for which to retrieve the weather forecast.
    Returns:
        Dict[str, Any]: A dictionary with the forecast information.
                        If successful, contains 'status', 'city', 'daily_summaries' (a list of dicts),
                        and 'human_readable_report' (a string).
                        If error, contains 'status' and 'error_message'.
    """
    if not weather_service_instance or not weather_service_instance.api_key:
        return {
            "status": "error",
            "error_message": "Weather service is not configured (API key may be missing or invalid)."
        }

    # Call the new forecast method
    forecast_info: Dict[str, Any] = weather_service_instance.get_forecast_for_city(city)

    if forecast_info.get("status") == "success":
        data = forecast_info.get("data", {})
        city_name = data.get("city", city.title())
        daily_summaries: List[Dict[str, Any]] = data.get("daily_summaries", []) # Type hint for clarity

        if not daily_summaries:
            return {
                "status": "error",
                "city": city_name, # Good to include city even in this error case
                "error_message": f"No daily forecast summaries available for {city_name}."
            }

        report_parts = [f"Weather forecast for {city_name}:"]
        for summary in daily_summaries:
            date_str = summary.get("date")
            min_temp = summary.get("min_temp_celsius")
            max_temp = summary.get("max_temp_celsius")
            description = summary.get("description")
            report_parts.append(
                f"On {date_str}: {description}, Min Temp: {min_temp}°C, Max Temp: {max_temp}°C."
            )
        
        human_readable_report = " ".join(report_parts)

        return {
            "status": "success", 
            "city": city_name,
            "daily_summaries": daily_summaries, # The structured data
            "human_readable_report": human_readable_report # The text summary
        }
    else:
        return { # Error from WeatherService
            "status": "error",
            "error_message": forecast_info.get("error_message", "An unknown error occurred with the weather service.")
        }


root_agent = Agent(
    name="weather_agent",
    model="gemini-2.0-flash",
    description=("Agent to answer questions about the weather forecast for a city, providing details for up to 5 days."), # Updated description
    instruction=("You are a helpful agent who can answer user questions about the weather forecast in a city. You can provide a forecast for up to 5 days. When asked for a forecast, provide a summary for the requested period if possible."), # Updated instruction
    tools=[get_weather_forecast] # Updated tool
)