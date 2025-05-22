from dotenv import load_dotenv
import openrouteservice # type: ignore
import os
from typing import Dict, Any, Optional

load_dotenv() # Load environment variables from .env file

OPENROUTESERVICE_API_KEY = os.getenv("OPENROUTESERVICE_API_KEY")

class RouteService:
    def __init__(self, api_key: str | None = OPENROUTESERVICE_API_KEY):
        if not api_key:
            print("Warning: Openrouteservice API key not configured. Set the OPENROUTESERVICE_API_KEY environment variable.")
            self.api_key = None
            self.client: Optional[openrouteservice.Client] = None
        else:
            self.api_key = api_key
            try:
                self.client = openrouteservice.Client(key=self.api_key)
                print(f"Openrouteservice client initialized successfully with key: {self.api_key[:5]}...")
            except openrouteservice.exceptions.ApiError as api_err: # type: ignore
                print(f"Openrouteservice API Error during client initialization: {api_err}. Key might be invalid or quotas exceeded.")
                self.client = None
                self.api_key = None # Mark as not configured if client fails due to API key issue
            except Exception as e:
                print(f"Error initializing Openrouteservice client: {e}")
                self.client = None
                self.api_key = None # Mark as not configured if client fails

    def geocode_location_basic(self, place_name: str) -> Optional[Dict[str, Any]]:
        """
        Performs a basic geocoding lookup for a place name and returns the raw API response.
        Returns None if the client is not initialized or an API error occurs.
        """
        if not self.client:
            print("Error: RouteService client not initialized. Cannot geocode.")
            return None
        
        print(f"Attempting to geocode: '{place_name}'")
        try:
            geocode_result = self.client.pelias_search(text=place_name, size=1) # type: ignore
            print(f"Successfully geocoded '{place_name}'.")
            return geocode_result # type: ignore
        except openrouteservice.exceptions.ApiError as e: # type: ignore
            print(f"API Error during geocoding for '{place_name}': {e}")
            return None
        except Exception as e:
            # Catch any other unexpected exceptions during the API call
            print(f"An unexpected error occurred while geocoding '{place_name}': {e}")
            return None

    def get_coordinates(self, place_name: str) -> Optional[tuple[float, float]]:
        """
        Geocode a place name and return (longitude, latitude) tuple, or None if not found.
        """
        result = self.geocode_location_basic(place_name)
        if result and result.get('features'):
            coords_list = result['features'][0].get('geometry', {}).get('coordinates')
            if coords_list and len(coords_list) == 2:
                # Ensure coordinates are floats before returning as tuple[float, float]
                try:
                    return (float(coords_list[0]), float(coords_list[1]))
                except (ValueError, TypeError):
                    print(f"Warning: Could not convert coordinates to float for {place_name}")
                    return None
        return None

    def get_route_basic(self, start_coords: tuple[float, float], end_coords: tuple[float, float], profile: str = 'driving-car') -> Optional[Dict[str, Any]]: # Changed to built-in tuple
        """
        Fetch a route between two (lon, lat) coordinates using the Directions API.
        Returns the raw route response or None on error.
        """
        if not self.client:
            print("Error: RouteService client not initialized. Cannot fetch route.")
            return None
        try:
            ors_coords = (start_coords, end_coords) 
            print(f"Requesting route from {ors_coords[0]} to {ors_coords[1]}...")
            route = self.client.directions( # type: ignore
                ors_coords,
                profile=profile,
                format='json',
                instructions=False
            )
            print("Route fetched successfully.")
            return route
        except openrouteservice.exceptions.ApiError as e: # type: ignore
             print(f"API Error fetching route: {e}")
             return None
        except Exception as e:
            print(f"Error fetching route: {e}")
            return None

