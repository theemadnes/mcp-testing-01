# grid_service.py
import math

# A simple set of predefined grid points (0-99 integers)
GRID_POINTS = [
    {"id": "Youth Hostel", "x": 10, "y": 20},
    {"id": "Sky High Hotel", "x": 50, "y": 75},
    {"id": "Welcome Inn", "x": 5, "y": 90},
    {"id": "Hostel Attitude", "x": 95, "y": 5},
    {"id": "Apartment4Rent", "x": 40, "y": 40},
    {"id": "Grand Hotel", "x": 80, "y": 15},
    {"id": "Cheap Cheap Rooms", "x": 15, "y": 85},
    {"id": "Airport Inn", "x": 60, "y": 30},
    {"id": "Extended Stay Suites", "x": 25, "y": 55},
    {"id": "Super Hospitality Hotel", "x": 70, "y": 90},
]

def calculate_distance(x1: int, y1: int, x2: int, y2: int) -> float:
    """Calculates Euclidean distance between two (x, y) points."""
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def find_closest_grid_point(query_x: int, query_y: int) -> dict:
    """
    Finds the closest predefined grid point to the given query coordinates.
    Returns JSON-serializable dictionary.
    """
    closest_point = None
    min_distance = float('inf')

    for point in GRID_POINTS:
        distance = calculate_distance(query_x, query_y, point["x"], point["y"])
        if distance < min_distance:
            min_distance = distance
            closest_point = point

    if closest_point:
        return {
            "closest_point_id": closest_point["id"],
            "closest_x": closest_point["x"],
            "closest_y": closest_point["y"],
            "distance_to_closest": min_distance
        }
    return {}