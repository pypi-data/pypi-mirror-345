"""
Geographic coordinate and map tile utilities.
"""

import math


def geo_to_tile(lat, lon, zoom):
    """Convert geographic coordinates to tile coordinates.

    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
        zoom: Zoom level (1-19)

    Returns:
        Tuple of (tile_x, tile_y)
    """
    lat_rad = math.radians(lat)
    n = 2.0**zoom
    tile_x = (lon + 180.0) / 360.0 * n
    tile_y = (
        (1.0 - math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi)
        / 2.0
        * n
    )
    return tile_x, tile_y


def tile_to_geo(tile_x, tile_y, zoom):
    """Convert tile coordinates to geographic coordinates.

    Args:
        tile_x: Tile X coordinate
        tile_y: Tile Y coordinate
        zoom: Zoom level (1-19)

    Returns:
        Tuple of (lat, lon) in degrees
    """
    n = 2.0**zoom
    lon_deg = tile_x / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * tile_y / n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg


def get_visible_tiles(center_lat, center_lon, zoom, width, height):
    """Calculate which tiles are visible in the current view.

    Args:
        center_lat: Center latitude in degrees
        center_lon: Center longitude in degrees
        zoom: Zoom level (1-19)
        width: Viewport width in pixels
        height: Viewport height in pixels

    Returns:
        List of (zoom, tile_x, tile_y, screen_x, screen_y) tuples
    """
    # Calculate the center tile
    center_tile_x, center_tile_y = geo_to_tile(center_lat, center_lon, zoom)

    # Calculate how many tiles we need to cover the view
    tiles_x = math.ceil(width / 256) + 1
    tiles_y = math.ceil(height / 256) + 1

    # Calculate the top-left tile
    start_tile_x = math.floor(center_tile_x - tiles_x / 2)
    start_tile_y = math.floor(center_tile_y - tiles_y / 2)

    # Calculate the screen position of the top-left tile
    start_screen_x = width / 2 - (center_tile_x - start_tile_x) * 256
    start_screen_y = height / 2 - (center_tile_y - start_tile_y) * 256

    # Generate list of visible tiles
    visible_tiles = []
    for y in range(tiles_y):
        for x in range(tiles_x):
            tile_x = start_tile_x + x
            tile_y = start_tile_y + y

            # Skip invalid tile coordinates
            if tile_x < 0 or tile_y < 0 or tile_x >= 2**zoom or tile_y >= 2**zoom:
                continue

            screen_x = start_screen_x + x * 256
            screen_y = start_screen_y + y * 256

            visible_tiles.append((zoom, tile_x, tile_y, screen_x, screen_y))

    return visible_tiles


def geo_to_screen(lat, lon, center_lat, center_lon, zoom, width, height):
    """Convert geographic coordinates to screen coordinates.

    Args:
        lat: Point latitude in degrees
        lon: Point longitude in degrees
        center_lat: Center latitude in degrees
        center_lon: Center longitude in degrees
        zoom: Zoom level (1-19)
        width: Viewport width in pixels
        height: Viewport height in pixels

    Returns:
        Tuple of (screen_x, screen_y) in pixels
    """
    # Calculate tile coordinates for the center of the screen
    center_tile_x, center_tile_y = geo_to_tile(center_lat, center_lon, zoom)

    # Calculate the screen position for the center tile
    center_screen_x = width / 2
    center_screen_y = height / 2

    # Calculate tile coordinates for the given lat/lon
    tile_x, tile_y = geo_to_tile(lat, lon, zoom)

    # Calculate the screen position for the given lat/lon
    screen_x = center_screen_x + (tile_x - center_tile_x) * 256
    screen_y = center_screen_y + (tile_y - center_tile_y) * 256

    return screen_x, screen_y


def tile_to_quadkey(x, y, zoom):
    """Convert tile coordinates to a quadkey used by Bing Maps.

    Args:
        x: Tile X coordinate
        y: Tile Y coordinate
        zoom: Zoom level (1-19)

    Returns:
        Quadkey string
    """
    quadkey = ""
    for i in range(zoom, 0, -1):
        digit = 0
        mask = 1 << (i - 1)
        if (x & mask) != 0:
            digit += 1
        if (y & mask) != 0:
            digit += 2
        quadkey += str(digit)
    return quadkey
