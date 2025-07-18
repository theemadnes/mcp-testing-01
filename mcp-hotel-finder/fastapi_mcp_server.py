# fastapi_mcp_server.py
from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, Field, ValidationError
from typing import Dict, Any, List, Literal, Optional

# Import your grid point logic
from grid_service import find_closest_grid_point

app = FastAPI(
    title="Grid Point Finder (MCP-like) Server",
    description="A FastAPI server implementing MCP-like endpoints for a grid point finder tool. "
                "Grid coordinates are integers between 0 and 99.",
    version="1.0.0"
)

# --- Pydantic Models for Tool Definition and Invocation ---

# Input model for our tool
class FindClosestGridInput(BaseModel):
    x_coordinate: int = Field(
        ...,
        ge=0,
        le=99,
        description="The X coordinate for the query, must be an integer between 0 and 99 inclusive."
    )
    y_coordinate: int = Field(
        ...,
        ge=0,
        le=99,
        description="The Y coordinate for the query, must be an integer between 0 and 99 inclusive."
    )

# Output model for our tool
class FindClosestGridOutput(BaseModel):
    closest_point_id: str = Field(..., description="The ID of the closest grid point.")
    closest_x: int = Field(..., description="The X coordinate of the closest grid point.")
    closest_y: int = Field(..., description="The Y coordinate of the closest grid point.")
    distance_to_closest: float = Field(..., description="The calculated distance to the closest grid point.")

# --- MCP Protocol Models (Simplified for our needs) ---
# These models represent the structures expected by a generic MCP client.

class ToolParameter(BaseModel):
    """Represents a single parameter for a tool."""
    name: str = Field(..., description="The name of the parameter.")
    type: str = Field(..., description="The JSON schema type of the parameter (e.g., 'integer', 'string').")
    description: Optional[str] = Field(None, description="A description of the parameter.")
    required: bool = Field(False, description="Whether the parameter is required.")
    minimum: Optional[int] = Field(None, description="Minimum value for numerical types.")
    maximum: Optional[int] = Field(None, description="Maximum value for numerical types.")

class ToolDefinition(BaseModel):
    """Represents a single tool an MCP server exposes."""
    name: str = Field(..., description="A unique name for the tool.")
    description: str = Field(..., description="A human-readable description of the tool's purpose.")
    parameters: List[ToolParameter] = Field(
        ...,
        description="A list of input parameters the tool accepts."
    )
    # The 'output_schema' could be a full JSON schema, but for simplicity, we'll
    # just indicate it's an object. A real MCP might provide more detail.
    output_schema: Dict[str, Any] = Field(
        {"type": "object"},
        description="A JSON schema defining the structure of the tool's output."
    )
    # Tags are useful for categorization
    tags: List[str] = Field(default_factory=list, description="Categorization tags for the tool.")

class ToolManifest(BaseModel):
    """The root manifest of all tools provided by the server."""
    tools: List[ToolDefinition] = Field(..., description="A list of tools available on this server.")

class ToolInvocationRequest(BaseModel):
    """The request structure for invoking a tool."""
    tool_name: str = Field(..., description="The name of the tool to invoke.")
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="A dictionary of parameters for the tool invocation."
    )

class ToolInvocationResponse(BaseModel):
    """The response structure for a successful tool invocation."""
    tool_name: str = Field(..., description="The name of the tool that was invoked.")
    output: Any = Field(..., description="The output of the tool execution.")

class ToolInvocationErrorResponse(BaseModel):
    """The response structure for a failed tool invocation."""
    tool_name: str = Field(..., description="The name of the tool that failed.")
    error: str = Field(..., description="A description of the error that occurred.")
    error_type: Literal["validation_error", "execution_error", "tool_not_found"] = Field(
        ...,
        description="The type of error that occurred."
    )


# --- MCP Endpoints ---

# Endpoint to list available tools (corresponds to /mcp/v1/tools or similar)
@app.get("/tools", response_model=ToolManifest, summary="List available tools")
async def list_tools():
    """
    Returns a manifest of all tools available on this server, including their
    descriptions and input schemas.
    """
    # Dynamically generate parameters from the Pydantic input model
    # This simulates how mcp-sdk would extract schema from your BaseModel
    input_schema = FindClosestGridInput.model_json_schema()
    parameters: List[ToolParameter] = []
    for prop_name, prop_details in input_schema.get("properties", {}).items():
        param_type = prop_details.get("type")
        param_description = prop_details.get("description")
        param_required = prop_name in input_schema.get("required", [])
        param_min = prop_details.get("minimum")
        param_max = prop_details.get("maximum")

        parameters.append(ToolParameter(
            name=prop_name,
            type=param_type,
            description=param_description,
            required=param_required,
            minimum=param_min,
            maximum=param_max
        ))

    tool_definition = ToolDefinition(
        name="find_closest_grid_point",
        description="Finds the closest predefined grid point to given integer X and Y coordinates (0-99 range).",
        parameters=parameters,
        output_schema=FindClosestGridOutput.model_json_schema(), # Provide full output schema
        tags=["geospatial", "grid", "integer_coordinates"]
    )
    return ToolManifest(tools=[tool_definition])

# Endpoint to invoke a tool (corresponds to /mcp/v1/invoke or similar)
@app.post("/invoke", response_model=ToolInvocationResponse, responses={
    400: {"model": ToolInvocationErrorResponse, "description": "Invalid Tool Invocation Request"},
    404: {"model": ToolInvocationErrorResponse, "description": "Tool Not Found"},
    422: {"model": ToolInvocationErrorResponse, "description": "Tool Parameter Validation Error"},
    500: {"model": ToolInvocationErrorResponse, "description": "Tool Execution Error"}
}, summary="Invoke a specific tool")
async def invoke_tool(request_body: ToolInvocationRequest):
    """
    Invokes a specified tool with the provided parameters and returns its output.
    Handles validation and execution errors.
    """
    tool_name = request_body.tool_name
    parameters = request_body.parameters

    if tool_name == "find_closest_grid_point":
        try:
            # Validate input parameters using our Pydantic model
            validated_inputs = FindClosestGridInput(**parameters)
            
            # Call your core logic
            result = find_closest_grid_point(
                query_x=validated_inputs.x_coordinate,
                query_y=validated_inputs.y_coordinate
            )
            
            # Ensure output matches expected schema (optional, Pydantic does this implicitly if assigned)
            # FindClosestGridOutput(**result) # Can add this line for explicit validation
            
            return ToolInvocationResponse(tool_name=tool_name, output=result)
        except ValidationError as e:
            raise HTTPException(
                status_code=422,
                detail=ToolInvocationErrorResponse(
                    tool_name=tool_name,
                    error=f"Input validation failed: {e.errors()}",
                    error_type="validation_error"
                ).model_dump() # .dict() for Pydantic v1
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=ToolInvocationErrorResponse(
                    tool_name=tool_name,
                    error=f"Tool execution failed: {str(e)}",
                    error_type="execution_error"
                ).model_dump() # .dict() for Pydantic v1
            )
    else:
        raise HTTPException(
            status_code=404,
            detail=ToolInvocationErrorResponse(
                tool_name=tool_name,
                error=f"Tool '{tool_name}' not found.",
                error_type="tool_not_found"
            ).model_dump() # .dict() for Pydantic v1
        )