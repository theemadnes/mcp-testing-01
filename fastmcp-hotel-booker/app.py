from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid # Import uuid for generating unique IDs
from fastmcp import FastMCP
from starlette.routing import Mount

# Create your FastMCP server
mcp = FastMCP("HotelBookingService")

# Create the ASGI app from your MCP server
mcp_app = mcp.http_app(path='/mcp')

# Initialize the FastAPI application
app = FastAPI(
    title="Hotel Booking Service",
    description="A simple FastAPI service for booking hotel stays.",
    version="1.0.0",
    lifespan=mcp_app.lifespan
)
app.mount("/mcp-server", mcp_app)

# --- Fake In-Memory Database ---
# This list will act as our simple database to store booking records.
# In a real application, this would be a connection to a persistent database (e.g., PostgreSQL, MongoDB).
fake_database: List[Dict[str, Any]] = []

# Define a Pydantic model for the booking request body.
# This helps with data validation and automatic documentation.
class BookingRequest(BaseModel):
    guest_name: str
    hotel_name: str
    num_nights: int

    # Example usage for OpenAPI documentation
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "guest_name": "Alice Smith",
                    "hotel_name": "Grand Hyatt",
                    "num_nights": 3
                }
            ]
        }
    }

# Define a POST endpoint for booking a hotel stay.
# The request body will be validated against the BookingRequest model.
@mcp.tool
@app.post("/book_stay")
async def book_stay(booking: BookingRequest):
    """
    Books a hotel stay with the provided guest name, hotel name, and number of nights.
    The booking will be stored in a fake in-memory database.

    - **guest_name**: The name of the guest (string).
    - **hotel_name**: The name of the hotel (string).
    - **num_nights**: The number of nights to stay (integer).

    Returns a confirmation message for the booking, including its unique ID.
    """
    
    # Basic validation for number of nights
    if booking.num_nights <= 0:
        raise HTTPException(
            status_code=400,
            detail="Number of nights must be a positive integer."
        )

    # Generate a unique ID for the booking
    booking_id = str(uuid.uuid4())

    # Create a dictionary for the booking record
    booking_record = {
        "id": booking_id,
        "guest_name": booking.guest_name,
        "hotel_name": booking.hotel_name,
        "num_nights": booking.num_nights
    }

    # Add the booking record to our fake database
    fake_database.append(booking_record)

    confirmation_message = (
        f"Booking confirmed for {booking.guest_name} at {booking.hotel_name} "
        f"for {booking.num_nights} night(s). Booking ID: {booking_id}. Thank you!"
    )

    return {"message": confirmation_message, "booking_id": booking_id}

# Define a GET endpoint to list all stored bookings.
@mcp.resource("data://list_bookings")
@app.get("/list_bookings")
async def list_bookings():
    """
    Retrieves a list of all current hotel bookings from the fake database.

    Returns a list of booking records.
    """
    return {"bookings": fake_database}

# To run this FastAPI application:
# 1. Save the code as a Python file (e.g., main.py).
# 2. Install FastAPI and Uvicorn: pip install fastapi "uvicorn[standard]"
# 3. Run from your terminal: uvicorn main:app --reload
#
# Then, you can access the API documentation at http://127.0.0.1:8000/docs
# and test the endpoints using the interactive UI.

# Add regular FastAPI routes
@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)