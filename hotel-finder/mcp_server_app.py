# mcp_server_app.py
from fastapi import FastAPI
from pydantic import BaseModel, Field
from mcp import MCPServer, Tool
from typing import Dict, Any

# Import your grid point logic
from grid_service import find_closest_grid_point

# 1. Initialize FastAPI application
app = FastAPI(
    title="Grid Point Finder MCP Server (0-99 Integer Grid)",
    description="An MCP server that provides a tool to find the closest grid point to given X and Y coordinates, restricted to 0-99 integers."
)

# 2. Initialize MCPServer with your FastAPI app
mcp_server = MCPServer(app)

# 3. Define Input Model for your Tool
class FindClosestGridInput(BaseModel):
    x_coordinate: int = Field(
        ...,
        ge=0, # Greater than or equal to 0
        le=99, # Less than or equal to 99
        description="The X coordinate for the query, must be an integer between 0 and 99 inclusive."
    )
    y_coordinate: int = Field(
        ...,
        ge=0, # Greater than or equal to 0
        le=99, # Less than or equal to 99
        description="The Y coordinate for the query, must be an integer between 0 and 99 inclusive."
    )

# 4. Define Output Model for your Tool
class FindClosestGridOutput(BaseModel):
    closest_point_id: str = Field(..., description="The ID of the closest grid point.")
    closest_x: int = Field(..., description="The X coordinate of the closest grid point.")
    closest_y: int = Field(..., description="The Y coordinate of the closest grid point.")
    distance_to_closest: float = Field(..., description="The calculated distance to the closest grid point.")

# 5. Register your function as an MCP Tool
@Tool(
    name="find_closest_grid_point",
    description="Finds the closest predefined grid point to given integer X and Y coordinates (0-99 range).",
    input_model=FindClosestGridInput,
    output_model=FindClosestGridOutput,
    tags=["geospatial", "grid", "integer_coordinates"]
)
def find_closest_grid_point_tool(inputs: FindClosestGridInput) -> Dict[str, Any]:
    """
    This function wraps your existing logic to be exposed as an MCP tool.
    It takes an instance of FindClosestGridInput and returns a dictionary
    that matches FindClosestGridOutput.
    """
    result = find_closest_grid_point(inputs.x_coordinate, inputs.y_coordinate)
    return result

# Register the tool with the MCP server
mcp_server.register_tool(find_closest_grid_point_tool)