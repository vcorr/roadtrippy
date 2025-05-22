import os
import json
from dotenv import load_dotenv
from route_planning_service import RouteService # Import necessary components

load_dotenv() # Load environment variables from .env file for the test script

# --- Basic Test --- 
if __name__ == '__main__':
    print("--- Basic RouteService Test ---")
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
                print(f"\nTesting route fetching from {start_place} to {end_place}")
                route_data = route_service_instance.get_route_basic(start_coords, end_coords)
                if route_data:
                    print("\n--- Route Result (Raw) ---")
                    # import json # json is already imported at the top
                    print(json.dumps(route_data, indent=2))
                else:
                    print("\nFailed to fetch route.")
            else:
                print("\nCould not get coordinates for both start and end locations. Routing test skipped.")
        else:
            print("\nRouteService client could not be initialized. Geocoding/route tests skipped.")
            print("Please check your API key and network connection.")
    print("--- End of Basic RouteService Test ---") 