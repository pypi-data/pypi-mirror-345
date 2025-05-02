# Ola Maps MCP Server

## Features

* `get_geocode`
    - Provides probable geographic coordinates and detailed location information, including a formatted address, for the given address as input.

* `reverse_geocode`
    - Converts geographic coordinates back into readable addresses or place names.

* `get_elevation`
    - Retrieves elevation data for a single location.

* `get_placeDetails`
    - Provides Place Details of a particular Place/POI whose Ola place_id necessarily needs to be given as an input.

* `nearbysearch`
    - Provides nearby places of a particular category/type based on the given location.

* `textsearch`
    - Provides a list of places based on textual search without the need for actual location coordinates.

* `get_directions`
    - Provides a routable path between two places.

* `distancematrix`
    - Calculates travel distance between multiple origins and destinations.

## Configuring mcp-ola-maps Server

### Steps to Configure:

1. Open the Claude Desktop Configuration File
    - On macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
    - On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

2. Add the Following Configuration:
```json
{
  "mcpServers": {
    "mcp-ola-maps": {
      "command": "uvx",
      "args": ["ola-maps-mcp-server"],
      "env": {
        "OLA_MAPS_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

3. Locate the command entry for `uvx` and replace it with the absolute path to the `uvx` executable. This ensures that the correct version of `uvx` is used when starting the server. On macOS, you can find this path using: `which uvx`.

4. Restart Claude Desktop to apply the changes.

