from main import app

from fastapi_mcp import FastApiMCP

# Initialize the FastApiMCP instance
mcp = FastApiMCP(app)

# Mount the MCP server directly to your FastAPI app
mcp.mount()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)