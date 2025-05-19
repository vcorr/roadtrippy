import datetime
from zoneinfo import ZoneInfo
from typing import Dict # Added import
from google.adk.agents import Agent  # type: ignore

def get_weather(city: str) -> Dict[str, str]:
    """Retrieves the current weather report for a specified city.
    Args:
        city (str): The name of the city for which to retrieve the weather report.
    Returns:
        dict: A dictionary with the weather information
              status and result or error msg.
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "The weather in New York is sunny with a temperature of 25 degrees"
                " Celsius (77 degrees Fahrenheit)."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }


root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to answer questions about theweather in a city."
    ),
    instruction=(
        "You are a helpful agent who can answer user questions about the weather in a city."
    ),
    tools=[get_weather]
)