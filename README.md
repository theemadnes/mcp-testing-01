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

### fastmcp-hotel-booker

after adding the hotel booker to `settings.json`, use Gemini CLI to call it:
```
╭──────────────────────────────────────────────────────────────────────────────╮
│  > i'm currently at 50,50. please find the closest hotel to me and make me   │
│    (Alex) a booking for 3 nights                                             │
╰──────────────────────────────────────────────────────────────────────────────╯

 ╭─────────────────────────────────────────────────────────────────────────────────╮
 │ ✔  find_nearest_hotel (hotelFinderServer MCP Server) {"coords":{"x":50,"y":50}} │
 │                                                                                 │
 │    {"id":5,"name":"Apartment4Rent","x":40,"y":40,"distance":14.14213            │
 │    5623730951}                                                                  │
 ╰─────────────────────────────────────────────────────────────────────────────────╯
 ╭─────────────────────────────────────────────────────────────────────────────────╮
 │ ✔  book_stay (hotelBookerServer MCP Server) {"booking":{"guest_name":"Alex","h… │
 │                                                                                 │
 │    {"message":"Booking confirmed for Alex at Apartment4Rent for 3               │
 │    night(s). Booking ID: 2895c9fb-7b4e-457e-9cc2-2745d63233dc. Thank            │
 │    you!","booking_id":"2895c9fb-7b4e-457e-9cc2-2745d63233dc"}                   │
 ╰─────────────────────────────────────────────────────────────────────────────────╯
✦ OK. I've found the nearest hotel to you and booked a 3-night stay for Alex.

  Hotel: Apartment4Rent
  Booking ID: 2895c9fb-7b4e-457e-9cc2-2745d63233dc

╭─────────────────────────────────────────╮
│  > show me all existing hotel bookings  │
╰─────────────────────────────────────────╯

 ╭───────────────────────────────────────────────────────────────────────╮
 │ ✔  list_bookings (hotelBookerServer MCP Server) {}                    │
 │                                                                       │
 │    {"bookings":[{"id":"2895c9fb-7b4e-457e-9cc2-2745d63233dc","guest_  │
 │    name":"Alex","hotel_name":"Apartment4Rent","num_nights":3}]}       │
 ╰───────────────────────────────────────────────────────────────────────╯
✦ OK. Here is the list of all existing hotel bookings:

  Booking ID: 2895c9fb-7b4e-457e-9cc2-2745d63233dc
  Guest Name: Alex
  Hotel Name: Apartment4Rent
  Number of Nights: 3
```

usage (for basic curl, instead of Gemini CLI):
```
# create a booking
curl -X POST "http://127.0.0.1:8080/book_stay"      -H "Content-Type: application/json"      -d '{"guest_name": "Alex", "hotel_name": "Youth Hostel", "num_nights": 5}'

# list bookings
curl -X GET "http://127.0.0.1:8080/list_bookings"
```