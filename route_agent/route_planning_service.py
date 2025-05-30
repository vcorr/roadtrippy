from dotenv import load_dotenv
import openrouteservice # type: ignore
import polyline # type: ignore
from geopy.distance import geodesic # type: ignore
import os
from typing import List, Optional

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
                self.api_key = None
            except Exception as e:
                print(f"Error initializing Openrouteservice client: {e}")
                self.client = None
                self.api_key = None

    def get_coordinates(self, place_name: str) -> Optional[tuple[float, float]]:
        """Geocode a place name and return (longitude, latitude) tuple, or None if not found."""
        if not self.client:
            print("Error: RouteService client not initialized. Cannot geocode.")
            return None
        
        print(f"Attempting to geocode: '{place_name}'")
        try:
            # Add layers parameter to prefer places that are more likely to be near roads
            geocode_result = self.client.pelias_search(
                text=place_name, 
                size=1,
                layers=['locality', 'region', 'county']  # Prefer larger areas over specific addresses
            ) # type: ignore
            print(f"Successfully geocoded '{place_name}'.")
            
            if geocode_result and geocode_result.get('features'):  # type: ignore
                coords_list = geocode_result['features'][0].get('geometry', {}).get('coordinates')  # type: ignore
                if coords_list and len(coords_list) == 2:  # type: ignore
                    try:
                        return (float(coords_list[0]), float(coords_list[1]))  # type: ignore
                    except (ValueError, TypeError):
                        print(f"Warning: Could not convert coordinates to float for {place_name}")
                        return None
            return None
        except openrouteservice.exceptions.ApiError as e: # type: ignore
            print(f"API Error during geocoding for '{place_name}': {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred while geocoding '{place_name}': {e}")
            return None

    def get_places_along_route(self, start_place: str, end_place: str, interval_km: float = 50) -> List[str]:
        """
        Get a list of place names at intervals along the route between two places.
        This is the main method for getting places for weather forecasting.
        
        Args:
            start_place: Name of the starting location
            end_place: Name of the destination location  
            interval_km: Distance interval in kilometers (default: 100km)
        
        Returns:
            List of place names at intervals along the route
        """
        # Get coordinates for start and end
        start_coords = self.get_coordinates(start_place)
        end_coords = self.get_coordinates(end_place)
        
        if not start_coords or not end_coords:
            print(f"Could not geocode start ({start_place}) or end ({end_place}) location")
            return []

        # Get the route
        route_data = self._get_route(start_coords, end_coords)
        if not route_data:
            return []

        # Extract route geometry and decode it
        geometry = route_data['routes'][0]['geometry']
        decoded_coords = self._decode_polyline(geometry)
        if not decoded_coords:
            return []

        # Calculate distances and find interval points
        distances = self._calculate_distances(decoded_coords)
        if not distances:
            return []

        interval_points = self._find_interval_points(decoded_coords, distances, interval_km * 1000)
        
        # Convert coordinates to place names
        places = []
        for lat, lon, _ in interval_points:
            place_name = self._reverse_geocode(lat, lon)
            if place_name:
                places.append(place_name)
        
        return places

    def _get_route(self, start_coords: tuple[float, float], end_coords: tuple[float, float]) -> Optional[dict]:  # type: ignore
        """Internal: Get route from OpenRouteService API."""
        if not self.client:
            print("Error: RouteService client not initialized. Cannot fetch route.")
            return None
        try:
            print(f"Requesting route from {start_coords} to {end_coords}...")
            route = self.client.directions(  # type: ignore
                (start_coords, end_coords),
                profile='driving-car',
                format='json',
                instructions=False,
                radiuses=[5000, 5000]  # Allow 5km radius to find routable points
            )
            print("Route fetched successfully.")
            return route  # type: ignore
        except Exception as e:
            print(f"Error fetching route: {e}")
            return None

    def _decode_polyline(self, encoded_polyline: str) -> List[tuple[float, float]]:
        """Internal: Decode polyline into coordinate pairs."""
        try:
            decoded_coords = polyline.decode(encoded_polyline)
            return [(float(lat), float(lon)) for lat, lon in decoded_coords]
        except Exception as e:
            print(f"Error decoding polyline: {e}")
            return []

    def _calculate_distances(self, coords: List[tuple[float, float]]) -> List[float]:
        """Internal: Calculate cumulative distances along route."""
        if not coords or len(coords) < 2:
            return []
        
        distances = [0.0]
        for i in range(1, len(coords)):
            point_distance = float(geodesic(coords[i-1], coords[i]).meters)  # type: ignore
            distances.append(distances[-1] + point_distance)
        
        return distances

    def _find_interval_points(self, coords: List[tuple[float, float]], distances: List[float], interval_meters: float) -> List[tuple[float, float, float]]:
        """Internal: Find points at distance intervals."""
        if not coords or not distances or len(coords) != len(distances):
            return []
        
        interval_points = []  # type: ignore
        current_target = interval_meters
        total_distance = distances[-1]
        
        while current_target < total_distance:
            # Find closest point to target distance
            closest_index = min(range(len(distances)), key=lambda i: abs(distances[i] - current_target))
            lat, lon = coords[closest_index]
            interval_points.append((lat, lon, distances[closest_index]))  # type: ignore
            current_target += interval_meters
        
        return interval_points  # type: ignore

    def _reverse_geocode(self, lat: float, lon: float) -> Optional[str]:
        """Internal: Convert coordinates to place name."""
        if not self.client:
            return None
        
        try:
            result = self.client.pelias_reverse(point=[lon, lat], size=1)  # type: ignore
            if result and result.get('features') and len(result['features']) > 0:  # type: ignore
                properties = result['features'][0].get('properties', {})  # type: ignore
                place_name = (
                    properties.get('locality') or   # type: ignore
                    properties.get('county') or   # type: ignore
                    properties.get('region') or   # type: ignore
                    properties.get('country') or  # type: ignore
                    f"({lat:.4f}, {lon:.4f})"
                )
                return str(place_name)  # type: ignore
            return None
        except Exception as e:
            print(f"Error reverse geocoding ({lat}, {lon}): {e}")
            return None

