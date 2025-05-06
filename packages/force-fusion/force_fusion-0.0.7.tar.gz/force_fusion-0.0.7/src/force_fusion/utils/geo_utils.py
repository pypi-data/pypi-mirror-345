"""
Geographic coordinate and map tile utilities.
"""

import math


def geo_to_tile(lat, lon, zoom):
    """
    Convert geographic coordinates to tile coordinates.

    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
        zoom: Zoom level (0-19)

    Returns:
        tuple: (x, y) tile coordinates
    """
    # Convert to radians
    lat_rad = math.radians(lat)

    # Calculate tile coordinates
    n = 2.0**zoom
    x = ((lon + 180.0) / 360.0) * n
    y = (
        (1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi)
        / 2.0
        * n
    )

    return x, y


def tile_to_geo(tile_x, tile_y, zoom):
    """
    Convert tile coordinates to geographic coordinates.

    Args:
        tile_x: Tile x coordinate
        tile_y: Tile y coordinate
        zoom: Zoom level (0-19)

    Returns:
        tuple: (lat, lon) geographic coordinates in degrees
    """
    n = 2.0**zoom
    lon = tile_x / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * tile_y / n)))
    lat = math.degrees(lat_rad)

    return lat, lon


def get_visible_tiles(center_lat, center_lon, zoom, width, height):
    """
    Calculate the tiles that are visible within the specified viewport.
    Ensures complete coverage for both rectangular and circular viewports.

    Args:
        center_lat: Latitude of the center in degrees
        center_lon: Longitude of the center in degrees
        zoom: Zoom level (0-19)
        width: Viewport width in pixels
        height: Viewport height in pixels

    Returns:
        list: List of tuples (zoom, tile_x, tile_y, screen_x, screen_y)
    """
    # Calculate center tile
    center_tile_x, center_tile_y = geo_to_tile(center_lat, center_lon, zoom)

    # Size of a single tile in pixels
    from force_fusion import config

    tile_size = config.TILE_SIZE

    # Calculate the number of tiles needed to cover the viewport
    # Use ceiling to ensure we get complete coverage, plus add 1 to ensure overlap
    half_width_tiles = math.ceil(width / (2 * tile_size)) + 1
    half_height_tiles = math.ceil(height / (2 * tile_size)) + 1

    # Ensure we get enough tiles to cover diagonal corners in a circular view
    diagonal_tiles = math.ceil(math.sqrt(half_width_tiles**2 + half_height_tiles**2))

    # Use the larger value to ensure full coverage for circular views
    max_tiles = max(half_width_tiles, half_height_tiles, diagonal_tiles)

    # Calculate the range of tiles to fetch
    min_tile_x = math.floor(center_tile_x - max_tiles)
    max_tile_x = math.ceil(center_tile_x + max_tiles)
    min_tile_y = math.floor(center_tile_y - max_tiles)
    max_tile_y = math.ceil(center_tile_y + max_tiles)

    # Calculate the pixel position of the center tile
    center_pixel_x = width / 2
    center_pixel_y = height / 2

    # Get all tiles in the visible range
    tiles = []
    for tile_y in range(min_tile_y, max_tile_y + 1):
        for tile_x in range(min_tile_x, max_tile_x + 1):
            # Calculate the pixel position of the top-left corner of this tile
            pixel_x = center_pixel_x + (tile_x - center_tile_x) * tile_size
            pixel_y = center_pixel_y + (tile_y - center_tile_y) * tile_size

            # Check if this tile is at least partially visible
            # For circular views, we include all tiles in the calculated range
            if (
                pixel_x + tile_size >= 0
                and pixel_x <= width
                and pixel_y + tile_size >= 0
                and pixel_y <= height
            ):
                tiles.append((zoom, tile_x, tile_y, pixel_x, pixel_y))

    return tiles


def tile_to_quadkey(tile_x, tile_y, zoom):
    """
    Convert tile coordinates to a quadkey (used by Bing Maps).

    Args:
        tile_x: Tile x coordinate
        tile_y: Tile y coordinate
        zoom: Zoom level (0-19)

    Returns:
        str: Quadkey string
    """
    quadkey = ""
    for i in range(zoom, 0, -1):
        digit = 0
        mask = 1 << (i - 1)
        if (tile_x & mask) != 0:
            digit += 1
        if (tile_y & mask) != 0:
            digit += 2
        quadkey += str(digit)
    return quadkey


def geo_to_screen(lat, lon, center_lat, center_lon, zoom, width, height):
    """
    Convert geographic coordinates to screen coordinates.

    Args:
        lat: Latitude in degrees to convert
        lon: Longitude in degrees to convert
        center_lat: Latitude of the center in degrees
        center_lon: Longitude of the center in degrees
        zoom: Zoom level (0-19)
        width: Viewport width in pixels
        height: Viewport height in pixels

    Returns:
        tuple: (x, y) screen coordinates in pixels
    """
    # Convert geographic coordinates to tile coordinates
    point_tile_x, point_tile_y = geo_to_tile(lat, lon, zoom)
    center_tile_x, center_tile_y = geo_to_tile(center_lat, center_lon, zoom)

    # Size of a single tile in pixels
    from force_fusion import config

    tile_size = config.TILE_SIZE

    # Calculate screen coordinates
    screen_x = width / 2 + (point_tile_x - center_tile_x) * tile_size
    screen_y = height / 2 + (point_tile_y - center_tile_y) * tile_size

    return screen_x, screen_y
