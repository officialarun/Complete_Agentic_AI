from mcp.server.fastmcp import FastMCP

mcp=FastMCP("Weather")

@mcp.tool()
async def get_weather(location:str)->str:
    """Returns the weather of a location."""
    return "Precipitation: 0% | Humidity: 38% | Wind: 11 km/h"

if __name__ =="__main__":
    mcp.run(transport="streamable-http")