from typing import Dict, Any, List
from google.adk.agents import Agent  # type: ignore

from dotenv import load_dotenv # type: ignore
load_dotenv() # Load .env file for API keys

from .route_planning_service import RouteService # Import the service

try:
    route_service_instance = RouteService()
except ValueError as e: # Catch potential API key configuration errors from RouteService __init__
    print(f"Error initializing RouteService: {e}")
    route_service_instance = None

def get_route_places(start_location: str, end_location: str, interval_km: float = 100.0) -> Dict[str, Any]:
    """Retrieves places along a route between two locations at specified intervals.
    
    Args:
        start_location (str): The starting location (city, address, landmark, etc.)
        end_location (str): The destination location (city, address, landmark, etc.)
        interval_km (float): Distance interval in kilometers between places (default: 100.0km)
        
    Returns:
        Dict[str, Any]: A dictionary with the route information.
                        If successful, contains 'status', 'start_location', 'end_location', 
                        'interval_km', 'places' (a list of place names), and 'human_readable_report'.
                        If error, contains 'status' and 'error_message'.
    """
    if not route_service_instance or not route_service_instance.api_key:
        return {
            "status": "error",
            "error_message": "Route service is not configured (API key may be missing or invalid)."
        }

    try:
        # Get places along the route
        places: List[str] = route_service_instance.get_places_along_route(
            start_location, end_location, interval_km
        )

        if not places:
            return {
                "status": "error", 
                "start_location": start_location,
                "end_location": end_location,
                "error_message": f"No places found along the route from {start_location} to {end_location}. This could be due to geocoding issues or route calculation problems."
            }

        # Create human-readable report
        if len(places) == 1:
            human_readable_report = f"On the route from {start_location} to {end_location}, you will pass through: {places[0]}."
        else:
            places_list = ", ".join(places[:-1]) + f", and {places[-1]}"
            human_readable_report = f"On the route from {start_location} to {end_location} (with stops every {interval_km}km), you will pass through: {places_list}."

        return {
            "status": "success",
            "start_location": start_location,
            "end_location": end_location,
            "interval_km": interval_km,
            "places": places,
            "human_readable_report": human_readable_report
        }

    except Exception as e:
        return {
            "status": "error",
            "start_location": start_location,
            "end_location": end_location,
            "error_message": f"An error occurred while calculating the route: {str(e)}"
        }


root_agent = Agent(
    name="route_agent",
    model="gemini-2.0-flash", 
    description=("Agent to answer questions about places along driving routes between two locations, providing intermediate stops at specified intervals."),
    instruction=("You are a helpful agent who can answer user questions about what places are along a route between two locations. You can find cities, towns, and landmarks at regular intervals along driving routes. When asked about a route, provide the places that travelers will encounter along the way."),
    tools=[get_route_places]
) 