from dotenv import load_dotenv
from route_planning_service import RouteService

load_dotenv() # Load environment variables from .env file for the test script

# Manually test the function logic (similar to agent.py but without relative imports)
try:
    route_service_instance = RouteService()
except ValueError as e:
    print(f"Error initializing RouteService: {e}")
    route_service_instance = None

def get_route_places(start_location: str, end_location: str, interval_km: float = 100):
    """Test version of the route agent function."""
    if not route_service_instance or not route_service_instance.api_key:
        return {
            "status": "error",
            "error_message": "Route service is not configured (API key may be missing or invalid)."
        }

    try:
        places = route_service_instance.get_places_along_route(
            start_location, end_location, interval_km
        )

        if not places:
            return {
                "status": "error", 
                "start_location": start_location,
                "end_location": end_location,
                "error_message": f"No places found along the route from {start_location} to {end_location}."
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

# --- Route Agent Test --- 
if __name__ == '__main__':
    print("--- Route Agent Test ---")
    
    # Test the route agent function
    print("\n=== Test 1: Tampere to Rovaniemi (default 100km intervals) ===")
    result = get_route_places("Tampere railway station, Finland", "Rovaniemi railway station, Finland")
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Start: {result['start_location']}")
        print(f"End: {result['end_location']}")
        print(f"Interval: {result['interval_km']}km")
        print(f"Places: {result['places']}")
        print(f"Report: {result['human_readable_report']}")
    else:
        print(f"Error: {result['error_message']}")
    
    print("\n=== Test 2: Helsinki to Turku (50km intervals) ===")
    result2 = get_route_places("Helsinki", "Turku", interval_km=50)
    print(f"Status: {result2['status']}")
    if result2['status'] == 'success':
        print(f"Start: {result2['start_location']}")
        print(f"End: {result2['end_location']}")
        print(f"Interval: {result2['interval_km']}km")
        print(f"Places: {result2['places']}")
        print(f"Report: {result2['human_readable_report']}")
    else:
        print(f"Error: {result2['error_message']}")
    
    print("\n=== Test 3: Invalid locations ===")
    result3 = get_route_places("NonExistentPlace123", "AnotherFakePlace456")
    print(f"Status: {result3['status']}")
    if result3['status'] == 'error':
        print(f"Error (expected): {result3['error_message']}")
    
    print("--- End of Route Agent Test ---") 