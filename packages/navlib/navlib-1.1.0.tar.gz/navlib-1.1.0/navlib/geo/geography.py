"""
This module provides functions for working with geographic coordinates.

Functions:
    latlon_to_zone_number: Determines the UTM zone number for a given latitude and longitude.
    latlon_to_zone_letter: Determines the UTM zone letter for a given latitude.
    ll2utm: Converts latitude and longitude to UTM coordinates.
    utm2ll: Converts UTM coordinates to latitude and longitude.
    deg2m_lat: Converts latitude from degrees to meters.
    deg2m_lon: Converts longitude from degrees to meters.
    ll2xy: Converts latitude and longitude to xy mercator coordinates from an origin.
    xy2ll: Converts xy mercator coordinates to latitude and longitude from an origin.

Authors: Sebastián Rodríguez-Martínez and Giancarlo Troni
Contact: srodriguez@mbari.org
"""

from typing import Tuple, Union

import numpy as np
import pyproj

from navlib.math import mean


def latlon_to_zone_number(latitude: float, longitude: float) -> int:
    """
    Determines the UTM zone number for a given latitude and longitude.

    Args:
        latitude (float): Latitude in degrees.
        longitude (float): Longitude in degrees.

    Returns:
        utm_zone (int): UTM zone number.

    Raises:
        ValueError: If the latitude and longitude are not within the valid range.

    Examples:
        >>> latlon_to_zone_number(37.7749, -122.4194)
        10
    """
    # Check if the latitude and longitude are within the valid range.
    if not (-80.0 <= latitude <= 84.0) or not (-180.0 <= longitude <= 180.0):
        raise ValueError("Latitude and longitude must be within the valid range.")

    if 56.0 <= latitude < 64.0 and 3.0 <= longitude < 12.0:
        return 32
    if 72.0 <= latitude < 84.0 and 0.0 <= longitude < 42.0:
        return 31
    return int((longitude + 180) / 6) + 1


def latlon_to_zone_letter(latitude: float) -> str:
    """
    Determines the UTM zone letter for a given latitude.

    Args:
        latitude (float): Latitude in degrees.

    Returns:
        utm_zone (str): UTM zone letter.

    Raises:
        ValueError: If the latitude is not within the valid range.

    Examples:
        >>> latlon_to_zone_letter(37.7749)
        'T'
    """
    # Check if the latitude is within the valid range.
    if not (-80.0 <= latitude <= 84.0):
        raise ValueError("Latitude must be within the valid range.")

    if 84 >= latitude >= 72:
        return "X"
    if 72 > latitude >= 64:
        return "W"
    if 64 > latitude >= 56:
        return "V"
    if 56 > latitude >= 48:
        return "U"
    if 48 > latitude >= 40:
        return "T"
    if 40 > latitude >= 32:
        return "S"
    if 32 > latitude >= 24:
        return "R"
    if 24 > latitude >= 16:
        return "Q"
    if 16 > latitude >= 8:
        return "P"
    if 8 > latitude >= 0:
        return "N"
    if 0 > latitude >= -8:
        return "M"
    if -8 > latitude >= -16:
        return "L"
    if -16 > latitude >= -24:
        return "K"
    if -24 > latitude >= -32:
        return "J"
    if -32 > latitude >= -40:
        return "H"
    if -40 > latitude >= -48:
        return "G"
    if -48 > latitude >= -56:
        return "F"
    if -56 > latitude >= -64:
        return "E"
    if -64 > latitude >= -72:
        return "D"
    if -72 > latitude >= -80:
        return "C"
    return "Z"


def ll2utm(
    latitude: Union[int, float, np.ndarray, list],
    longitude: Union[int, float, np.ndarray, list],
) -> Tuple[Union[float, np.ndarray], int, str]:
    """
    Converts latitude and longitude to UTM coordinates.

    In this case we will use ENU (not following NED): x-axis is pointing EAST
    y-axis is pointing NORTH and z-axis is pointing UP.

    Args:
        latitude (Union[int, float, np.ndarray, list]): Latitude in degrees.
        longitude (Union[int, float, np.ndarray, list]): Longitude in degrees.

    Returns:
        easting (Union[float, np.ndarray]): UTM easting in meters.
        northing (Union[float, np.ndarray]): UTM northing in meters.
        zone_number (int): UTM zone number.
        hemisphere (str): Hemisphere ('north' or 'south').

    Raises:
        ValueError: If the latitude and longitude are not within the valid range.

    Examples:
        >>> ll2utm(37.7749, -122.4194)
        (551730.0, 4163834.0, 10, 'north')
        >>> ll2utm([37.7749, 37.7749], [-122.4194, -122.4194])
        (array([551730., 551730.]), array([4163834., 4163834.]), 10, 'north')
    """
    # Convert to array if its a list
    if isinstance(latitude, list):
        latitude = np.array(latitude)
    if isinstance(longitude, list):
        longitude = np.array(longitude)

    # Check input type
    if not isinstance(latitude, (float, np.ndarray, int)):
        raise TypeError("Latitude must be an integer, a float or a numpy array.")
    if not isinstance(longitude, (float, np.ndarray, int)):
        raise TypeError("Longitude must be an integer, a float or a numpy array.")
    if type(latitude) is not type(longitude):
        raise TypeError("Latitude and Longitude types do not match")

    # Check data validity
    if isinstance(latitude, np.ndarray) and isinstance(longitude, np.ndarray):
        if latitude.shape != longitude.shape:
            raise ValueError("Latitude and longitude must have the same shape.")

    # Check if the latitude and longitude are within the valid range.
    if isinstance(latitude, np.ndarray) and isinstance(longitude, np.ndarray):
        if not (np.all((-80.0 <= latitude) & (latitude <= 84.0))):
            raise ValueError("Latitude must be within the valid range.")
        if not (np.all((-180.0 <= longitude) & (longitude <= 180.0))):
            raise ValueError("Longitude must be within the valid range.")
    else:
        if not (-80.0 <= latitude <= 84.0) or not (-180.0 <= longitude <= 180.0):
            raise ValueError("Latitude and longitude must be within the valid range.")

    if isinstance(latitude, np.ndarray):
        zone_number = latlon_to_zone_number(mean(latitude), mean(longitude))
        hemisphere = "north" if mean(latitude) > 0 else "south"
    else:
        zone_number = latlon_to_zone_number(latitude, longitude)
        hemisphere = "north" if latitude > 0 else "south"

    if hemisphere == "north":
        utm_proj = pyproj.Proj(
            proj="utm", zone=f"{zone_number}", ellps="WGS84", datum="WGS84", units="m"
        )
    else:
        utm_proj = pyproj.Proj(
            proj="utm",
            zone=f"{zone_number}",
            ellps="WGS84",
            datum="WGS84",
            units="m",
            south=True,
        )

    # utm_x and utm_y hold the UTM coordinates corresponding to the given latitude and longitude, i.e., easting and
    # northing, respectively.
    easting, northing = utm_proj(longitude, latitude)

    return easting, northing, zone_number, hemisphere


def utm2ll(
    northing: Union[int, float, np.ndarray, list],
    easting: Union[int, float, np.ndarray, list],
    zone_str: str,
) -> Tuple[Union[float, np.ndarray], Union[float, np.ndarray]]:
    """
    Converts the UTMx (easting) and UTMy (northing) and UTM zone coordinates to
    the latitude and longitude mercator projection.

    Args:
        northing (Union[int, float, np.ndarray, list]): Northing in meters.
        easting (Union[int, float, np.ndarray, list]): Easting in meters.
        zone_str (str): UTM zone. Example: '10N'.

    Returns:
        latitude (Union[float, np.ndarray]): Latitude in degrees.
        longitude (Union[float, np.ndarray]): Longitude in degrees.

    Raises:
        ValueError: If the UTM zone is not valid.

    Examples:
        >>> utm2ll(4163834.0, 551730.0, '10N')
        (37.7749, -122.4194)
    """
    # Convert lists to numpy arrays
    if isinstance(northing, list):
        northing = np.array(northing)
    if isinstance(easting, list):
        easting = np.array(easting)

    # Check input type
    if not isinstance(northing, (float, np.ndarray, int)):
        raise TypeError("Northing must be an integer, float or a numpy array.")
    if not isinstance(easting, (float, np.ndarray, int)):
        raise TypeError("Easting must be an integer, float or a numpy array.")
    if type(northing) is not type(easting):
        raise TypeError("Northing and Easting types do not match")
    if not isinstance(zone_str, str):
        raise TypeError("Zone must be a string.")

    # Check data validity
    if isinstance(northing, np.ndarray):
        if northing.shape != easting.shape:
            raise ValueError("Northing and easting must have the same shape.")

    # Check if the zone is a valid UTM zone.
    if not zone_str[0].isdigit() or not zone_str[-1].isalpha():
        raise ValueError("Invalid UTM zone.")

    zone_number = zone_str[:-1]

    if int(zone_number) > 60 or int(zone_number) < 1:
        raise ValueError("Invalid UTM zone.")

    if zone_str[-1].upper() == "N":
        ll_proj = pyproj.Proj(
            proj="utm",
            zone=zone_number,
            ellps="WGS84",
            datum="WGS84",
            units="m",
            no_defs=True,
        )
    elif zone_str[-1].upper() == "S":
        ll_proj = pyproj.Proj(
            proj="utm",
            zone=zone_number,
            ellps="WGS84",
            datum="WGS84",
            units="m",
            south=True,
            no_defs=True,
        )
    else:
        raise ValueError("Invalid UTM zone.")

    longitude, latitude = ll_proj(easting, northing, inverse=True)

    return latitude, longitude


def deg2m_lat(
    latitude: Union[int, float, np.ndarray, list]
) -> Union[float, np.ndarray]:
    """
    Converts latitude from degrees to meters.

    Args:
        latitude (Union[int, float, np.ndarray, list]): Latitude in degrees.

    Returns:
        latitude (Union[float, np.ndarray]): Latitude in meters.

    Examples:
        >>> deg2m_lat(1)
        1.1057e+05
    """
    # Convert lists to numpy arrays
    if isinstance(latitude, list):
        latitude = np.array(latitude)

    # Check input type
    if not isinstance(latitude, (float, np.ndarray, int)):
        raise TypeError("Latitude must be an integer, float or a numpy array.")

    # Convert to radians
    latrad = np.deg2rad(latitude)
    dy = (
        111132.09
        - 566.05 * np.cos(2.0 * latrad)
        + 1.20 * np.cos(4.0 * latrad)
        - 0.002 * np.cos(6.0 * latrad)
    )
    return dy


def deg2m_lon(
    longitude: Union[int, float, np.ndarray, list]
) -> Union[float, np.ndarray]:
    """
    Converts longitude from degrees to meters.

    Args:
        longitude (Union[int, float, np.ndarray, list]): Latitude in degrees.

    Returns:
        latitude (Union[float, np.ndarray]): Longitude in meters.

    Examples:
        >>> deg2m_lon(1)
        1.1113e+05
    """
    # Convert lists to numpy arrays
    if isinstance(longitude, list):
        longitude = np.array(longitude)

    # Check input type
    if not isinstance(longitude, (float, np.ndarray, int)):
        raise TypeError("Longitude must be an integer, float or a numpy array.")

    # Convert to radians
    latrad = np.deg2rad(longitude)
    dx = (
        111415.13 * np.cos(latrad)
        - 94.55 * np.cos(3.0 * latrad)
        + 0.12 * np.cos(5.0 * latrad)
    )
    return dx


def ll2xy(
    latitude: Union[int, float, np.ndarray, list],
    longitude: Union[int, float, np.ndarray, list],
    origin_latitude: float = 0.0,
    origin_longitude: float = 0.0,
) -> Tuple[Union[float, np.ndarray], Union[float, np.ndarray]]:
    """
    Converts latitude and longitude to xy mercator coordinates from an origin.

    In this case we will use ENU (not following NED): x-axis is pointing EAST
    y-axis is pointing NORTH and z-axis is pointing UP.

    Args:
        latitude (Union[int, float, np.ndarray, list]): Latitude in degrees.
        longitude (Union[int, float, np.ndarray, list]): Longitude in degrees.
        origin_latitude (float): Origin latitude in degrees.
        origin_longitude (float): Origin longitude in degrees.

    Returns:
        x (Union[float, np.ndarray]): x coordinate in meters.
        y (Union[float, np.ndarray]): y coordinate in meters.

    Examples:
        >>> ll2xy(37.7749, -122.4194)
        (551730.0, 4163834.0)
    """
    # Convert lists to numpy arrays
    if isinstance(latitude, list):
        latitude = np.array(latitude)
    if isinstance(longitude, list):
        longitude = np.array(longitude)

    # Check input type
    if not isinstance(latitude, (float, np.ndarray, int)):
        raise TypeError("Latitude must be an integer, float or a numpy array.")
    if not isinstance(longitude, (float, np.ndarray, int)):
        raise TypeError("Longitude must be an integer, float or a numpy array.")
    if type(latitude) is not type(longitude):
        raise TypeError("Latitude and Longitude types do not match")
    if not isinstance(origin_latitude, (float, int)):
        raise TypeError("Origin latitude must be an integer or a float.")
    if not isinstance(origin_longitude, (float, int)):
        raise TypeError("Origin longitude must be an integer or a float.")

    # Check data validity
    if isinstance(latitude, np.ndarray):
        if latitude.shape != longitude.shape:
            raise ValueError("Latitude and longitude must have the same shape.")

    x = (longitude - origin_longitude) * deg2m_lon(origin_latitude)
    y = (latitude - origin_latitude) * deg2m_lat(origin_latitude)
    return x, y


def xy2ll(
    x: Union[int, float, np.ndarray, list],
    y: Union[int, float, np.ndarray, list],
    origin_latitude: float = 0.0,
    origin_longitude: float = 0.0,
) -> Tuple[Union[float, np.ndarray], Union[float, np.ndarray]]:
    """
    Converts xy mercator coordinates to latitude and longitude from an origin.

    Args:
        x (Union[int, float, np.ndarray, list]): x coordinate in meters.
        y (Union[int, float, np.ndarray, list]): y coordinate in meters.
        origin_latitude (float): Origin latitude in degrees.
        origin_longitude (float): Origin longitude in degrees.

    Returns:
        latitude (Union[float, np.ndarray]): Latitude in degrees.
        longitude (Union[float, np.ndarray]): Longitude in degrees.

    Examples:
        >>> xy2ll(551730.0, 4163834.0)
        (37.7749, -122.4194)
    """
    # Convert lists to numpy arrays
    if isinstance(x, list):
        x = np.array(x)
    if isinstance(y, list):
        y = np.array(y)

    # Check input type
    if not isinstance(x, (float, np.ndarray, int)):
        raise TypeError("x must be an integer, float or a numpy array.")
    if not isinstance(y, (float, np.ndarray, int)):
        raise TypeError("y must be an integer, float or a numpy array.")
    if type(x) is not type(y):
        raise TypeError("x and y types do not match")
    if not isinstance(origin_latitude, (float, int)):
        raise TypeError("Origin latitude must be an integer or a float.")
    if not isinstance(origin_longitude, (float, int)):
        raise TypeError("Origin longitude must be an integer or a float.")

    # Check data validity
    if isinstance(x, np.ndarray):
        if x.shape != y.shape:
            raise ValueError("x and y must have the same shape.")

    latitude = y / deg2m_lat(origin_latitude) + origin_latitude
    longitude = x / deg2m_lon(origin_longitude) + origin_longitude
    return latitude, longitude


def dms_to_decimal(degrees: int, minutes: int, seconds: float, direction: str) -> float:
    """
    Convert DMS (degrees, minutes, seconds) to decimal degrees.

    Args:
        degrees (int): Degrees
        minutes (int): Minutes
        seconds (float): Seconds
        direction (str): Direction ('N', 'S', 'E', 'W')

    Returns:
        decimal (float): Decimal degrees

    Raises:
        ValueError: If the inputs are not of the correct dimensions.

    Examples:
        >>> dms_to_decimal(37, 46, 29.52, 'N')
        37.77486666666667
    """
    # Check data types validity
    if not isinstance(degrees, int):
        raise TypeError("Degrees must be an integer.")
    if not isinstance(minutes, int):
        raise TypeError("Minutes must be an integer.")
    if not isinstance(seconds, (int, float)):
        raise TypeError("Seconds must be a float or an integer.")

    # Check data validity
    if direction in ["N", "S"] and (degrees < 0 or degrees > 90):
        raise ValueError("Degrees must be between 0 and 90 for directions 'N' or 'S'.")
    if direction in ["E", "W"] and (degrees < 0 or degrees > 180):
        raise ValueError("Degrees must be between 0 and 180 for directions 'E' or 'W'.")
    if minutes < 0 or minutes >= 60:
        raise ValueError("Minutes must be between 0 and 59.")
    if seconds < 0 or seconds >= 60:
        raise ValueError("Seconds must be between 0 and 59.")
    if direction not in ["N", "S", "E", "W"]:
        raise ValueError("Direction must be 'N', 'S', 'E', or 'W'.")

    decimal = degrees + minutes / 60 + seconds / 3600
    if direction in ["S", "W"]:
        decimal = -decimal
    return decimal
