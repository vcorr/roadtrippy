import os
from dotenv import load_dotenv
from route_planning_service import RouteService # Import necessary components

load_dotenv() # Load environment variables from .env file for the test script

# --- Basic Test --- 
if __name__ == '__main__':
    print("--- RouteService Test ---")
    actual_api_key = os.getenv("OPENROUTESERVICE_API_KEY") 

    if not actual_api_key:
        print("CRITICAL: OPENROUTESERVICE_API_KEY environment variable is not set or not loaded from .env.")
        print("Please set it or ensure .env file is correct to run this test.")
    else:
        print(f"OPENROUTESERVICE_API_KEY found: {actual_api_key[:5]}...")
        
        route_service_instance = RouteService() # Uses the env var by default

        if route_service_instance.client:
            # Test geocoding
            start_place = "Tampere railway station, Finland"
            end_place = "Rovaniemi railway station, Finland"
            print(f"\nTesting geocoding for: {start_place}")
            start_coords = route_service_instance.get_coordinates(start_place)
            print(f"Result: {start_coords}")
            print(f"\nTesting geocoding for: {end_place}")
            end_coords = route_service_instance.get_coordinates(end_place)
            print(f"Result: {end_coords}")

            if start_coords and end_coords:
                # Test the main method for getting place names (this is what you actually need!)
                print(f"\n--- Testing Main Method: Get Places Along Route ---")
                places = route_service_instance.get_places_along_route(start_place, end_place, interval_km=100)
                print(f"Places along route from {start_place} to {end_place}:")
                print(f"Found {len(places)} places at ~100km intervals:")
                for i, place in enumerate(places):
                    print(f"  {i+1}. {place}")
                
                # Test different interval
                print(f"\n--- Testing with 150km intervals ---")
                places_150 = route_service_instance.get_places_along_route(start_place, end_place, interval_km=150)
                print(f"Found {len(places_150)} places at ~150km intervals:")
                for i, place in enumerate(places_150):
                    print(f"  {i+1}. {place}")
            else:
                print("\nCould not get coordinates for both start and end locations. Route tests skipped.")
        else:
            print("\nRouteService client could not be initialized. Tests skipped.")
            print("Please check your API key and network connection.")
    print("--- End of RouteService Test ---") 