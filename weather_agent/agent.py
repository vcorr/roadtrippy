from typing import Dict, Any
from google.adk.agents import Agent  # type: ignore

from dotenv import load_dotenv # Added import
load_dotenv() # Added to load .env file

from .weather_service import WeatherService # Import the service

try:
    weather_service_instance = WeatherService()
except ValueError as e: # Catch potential API key configuration errors from WeatherService __init__
    print(f"Error initializing WeatherService: {e}")
    # Fallback: create a dummy instance or handle as critical error
    # For now, if it fails, get_weather will report the service is unavailable.
    weather_service_instance = None

def get_weather(city: str) -> Dict[str, str]:
    """Retrieves the current weather report for a specified city.
    Args:
        city (str): The name of the city for which to retrieve the weather report.
    Returns:
        Dict[str, str]: A dictionary with the weather information:
                        status ('success' or 'error') and
                        report (if success) or error_message (if error).
    """
    if not weather_service_instance or not weather_service_instance.api_key:
        return {
            "status": "error",
            "error_message": "Weather service is not configured (API key may be missing or invalid)."
        }

    weather_info: Dict[str, Any] = weather_service_instance.get_weather_for_city(city)

    if weather_info.get("status") == "success":
        data = weather_info.get("data", {})
        city_name = data.get("city", city.title()) # Fallback to input city if not in data
        description = data.get("description", "N/A")
        temp_celsius = data.get("temperature_celsius")

        if temp_celsius is None:
            return {
                "status": "error",
                "error_message": f"Temperature data was not available in the response for {city_name}."
            }

        report_string = (
            f"The weather in {city_name} is {description} "
            f"with a temperature of {temp_celsius}°C."
        )
        return {"status": "success", "report": report_string}
    else:
        return {
            "status": "error",
            "error_message": weather_info.get("error_message", "An unknown error occurred with the weather service.")
        }


root_agent = Agent(
    name="weather_agent",
    model="gemini-2.0-flash",
    description=("Agent to answer questions about the weather in a city."),
    instruction=("You are a helpful agent who can answer user questions about the weather in a city."),
    tools=[get_weather]
)