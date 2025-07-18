# grid_service.py
import math

# A simple set of predefined grid points (0-99 integers)
GRID_POINTS = [
    {"id": "G01", "x": 10, "y": 20},
    {"id": "G02", "x": 50, "y": 75},
    {"id": "G03", "x": 5, "y": 90},
    {"id": "G04", "x": 95, "y": 5},
    {"id": "G05", "x": 40, "y": 40},
    {"id": "G06", "x": 80, "y": 15},
    {"id": "G07", "x": 15, "y": 85},
    {"id": "G08", "x": 60, "y": 30},
    {"id": "G09", "x": 25, "y": 55},
    {"id": "G10", "x": 70, "y": 90},
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

# Example of how your existing web service might expose this (if still separate):
# from flask import Flask, request, jsonify
# app = Flask(__name__)
#
# @app.route('/closest_grid', methods=['GET'])
# def get_closest_grid():
#     try:
#         x = int(request.args.get('x'))
#         y = int(request.args.get('y'))
#         if not (0 <= x <= 99 and 0 <= y <= 99):
#             return jsonify({"error": "Coordinates must be between 0 and 99"}), 400
#         result = find_closest_grid_point(x, y)
#         return jsonify(result)
#     except (TypeError, ValueError):
#         return jsonify({"error": "Invalid x or y coordinate"}), 400
#
# if __name__ == '__main__':
#     app.run(debug=True)