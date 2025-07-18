from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import random
import math
from typing import Optional
from fastmcp import FastMCP
from starlette.routing import Mount

# Create your FastMCP server
mcp = FastMCP("MyServer")

# Create the ASGI app from your MCP server
mcp_app = mcp.http_app(path='/mcp')

# Initialize the FastAPI application
app = FastAPI(
    title="Hotel Finder Service",
    description="A simple service to find the nearest hotel from an internal database.",
    lifespan=mcp_app.lifespan
)
app.mount("/mcp-server", mcp_app)

# Initialize the FastApiMCP instance
#mcp = FastApiMCP(app)

# Mount the MCP server directly to your FastAPI app
#mcp.mount()

# Pydantic model for the hotel data
class Hotel(BaseModel):
    id: int
    name: str
    x: int
    y: int
    distance: Optional[float] = None # Added distance field

# Pydantic model for the input coordinates
class Coordinates(BaseModel):
    # Ensure x and y coordinates are between 0 and 99 inclusive
    x: int = Field(..., ge=0, le=99, description="X coordinate (0-99)")
    y: int = Field(..., ge=0, le=99, description="Y coordinate (0-99)")

# Internal database of fake hotels
# Each hotel has grid coordinates (x, y) ranging from 0-99
fake_hotels_db: list[Hotel] = [
    Hotel(id=1, name="Youth Hostel", x=10, y=20),
    Hotel(id=2, name="Sky High Hotel", x=50, y=75),
    Hotel(id=3, name="Welcome Inn", x=5, y=90),
    Hotel(id=4, name="Hostel Attitude", x=95, y=5),
    Hotel(id=5, name="Apartment4Rent", x=40, y=40),
    Hotel(id=6, name="Grand Hotel", x=80, y=15),
    Hotel(id=7, name="Cheap Cheap Rooms", x=15, y=85),
    Hotel(id=8, name="Airport Inn", x=60, y=30),
    Hotel(id=9, name="Extended Stay Suites", x=25, y=55),
    Hotel(id=10, name="Super Hospitality Hotel", x=70, y=90),
]

'''
# Generate 10 fake hotels
for i in range(1, 11):
    fake_hotels_db.append(
        Hotel(
            id=i,
            name=f"Hotel {i:02d} - Grand Stay",
            x=random.randint(0, 99), # Already generates between 0 and 99
            y=random.randint(0, 99)  # Already generates between 0 and 99
        )
    )
'''

# Helper function to calculate Euclidean distance
def calculate_distance(x1: int, y1: int, x2: int, y2: int) -> float:
    """
    Calculates the Euclidean distance between two points (x1, y1) and (x2, y2).
    """
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

@mcp.tool
@app.post("/find-nearest-hotel", response_model=Hotel)
async def find_nearest_hotel(coords: Coordinates):
    """
    Finds the nearest hotel to the given x and y coordinates.

    Args:
        coords (Coordinates): A JSON object containing 'x' and 'y' integer coordinates.
                              These values must be between 0 and 99 inclusive.

    Returns:
        Hotel: The nearest hotel's information (id, name, x, y, and distance).

    Raises:
        HTTPException: If no hotels are found in the database (should not happen with pre-populated data),
                       or if input coordinates are out of the specified range (handled by Pydantic).
    """
    if not fake_hotels_db:
        raise HTTPException(status_code=500, detail="Hotel database is empty.")

    min_distance = float('inf')
    nearest_hotel = None
    calculated_distance = 0.0 # Initialize variable to store the distance

    # Iterate through each hotel to find the nearest one
    for hotel in fake_hotels_db:
        distance = calculate_distance(coords.x, coords.y, hotel.x, hotel.y)
        if distance < min_distance:
            min_distance = distance
            nearest_hotel = hotel
            calculated_distance = distance # Store the distance of the nearest hotel

    if nearest_hotel is None:
        # This case should ideally not be reached if the database is not empty
        raise HTTPException(status_code=404, detail="Could not find a nearest hotel.")

    # Assign the calculated distance to the nearest hotel object before returning
    nearest_hotel.distance = calculated_distance
    return nearest_hotel

# Add regular FastAPI routes
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Convert FastAPI app to MCP server
#mcp = FastMCP.from_fastapi(app=app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    #mcp.run(transport)  # Run as MCP server
