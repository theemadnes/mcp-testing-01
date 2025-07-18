# mcp-testing-01
use model context protocol to work with two services - one that finds the nearest "hotel" based on current location) and another that can be used to create bookings for the nearest hotel found


### fastmcp-hotel-finder

this is the only thing that works right now with Gemini CLI by adding (assuming you're running it locally) to `~/.gemini/settings.json`:
```
"mcpServers": {
    "httpServer": {
      "httpUrl": "http://localhost:8000/mcp-server/mcp/",
      "timeout": 5000
    }
  }
```

afterwards, use Gemini CLI to call it:

```
╭─────────────────────────────────────────────────────────────────────╮
│  > use find_nearest_hotel to find the nearest hotel to me. i'm at   │
│    coordinates 6,7                                                  │
╰─────────────────────────────────────────────────────────────────────╯

 ╭─────────────────────────────────────────────────────────────────────────╮
 │ ✔  find_nearest_hotel (httpServer MCP Server) {"coords":{"x":6,"y":7}}  │
 │                                                                         │
 │    {"id":1,"name":"Youth                                                │
 │    Hostel","x":10,"y":20,"distance":13.601470508735444}                 │
 ╰─────────────────────────────────────────────────────────────────────────╯
✦ The nearest hotel to you is the Youth Hostel, which is at coordinates (10, 20)
  and is 13.6 units away.
```

usage (for basic curl, instead of Gemini CLI):
```
curl -X POST "http://127.0.0.1:8000/find-nearest-hotel"      -H "Content-Type: application/json"      -d '{"x": 50, "y": 10}'
```