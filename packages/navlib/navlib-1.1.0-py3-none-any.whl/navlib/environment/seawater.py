"""
This module provides functions to calculate various seawater properties.

Functions:
    ctd2svel: Calculate sound velocity from conductivity, temperature, and depth.
    depth2pressure: Calculate pressure from depth.
    ctp2salinity: Calculate absolute salinity from conductivity, temperature, and pressure.
    ctd2salinity: Calculate absolute salinity from conductivity, temperature, and depth.
    ctp2pden: Calculate potential density from conductivity, temperature, and pressure.
    ctd2oxygen_saturation: Calculate oxygen saturation from conductivity, temperature, and depth.

Authors: Sebastián Rodríguez-Martínez and Giancarlo Troni
Contact: srodriguez@mbari.org
"""

from typing import List, Union

import gsw
import numpy as np


def ctd2svel(
    conductivity: Union[float, np.ndarray, List[float]],
    temperature: Union[float, np.ndarray, List[float]],
    depth: Union[float, np.ndarray, List[float]],
    latitude: Union[float, np.ndarray, List[float]] = None,
    longitude: Union[float, np.ndarray, List[float]] = None,
) -> Union[float, np.ndarray]:
    """
    Calculates sound velocity in m/s from conductivity, temperature, and depth.

    Args:
        conductivity (Union[float, np.ndarray, List[float]]): Conductivity in S/m.
        temperature (Union[float, np.ndarray, List[float]]): Temperature in degrees Celsius (ITS-90).
        depth (Union[float, np.ndarray, List[float]]): Depth in meters. Positive is upward.
        latitude (Union[float, np.ndarray, List[float]], optional): Latitude in degrees. Defaults to None.
        longitude (Union[float, np.ndarray, List[float]], optional): Longitude in degrees. Defaults to None.
    Returns:
        sound_velocity (Union[float, np.ndarray]): Sound velocity in m/s.

    Raises:
        TypeError: If the inputs are not of the correct type.
        ValueError: If the inputs are not of the correct shape or range.
    """
    # Convert to numpy arrays
    if isinstance(conductivity, list):
        conductivity = np.array(conductivity)
    if isinstance(temperature, list):
        temperature = np.array(temperature)
    if isinstance(depth, list):
        depth = np.array(depth)
    if isinstance(latitude, list):
        latitude = np.array(latitude)
    if isinstance(longitude, list):
        longitude = np.array(longitude)

    # Check inputs type
    if not isinstance(conductivity, (np.ndarray, float)):
        raise TypeError("Conductivity must be a float or an array.")
    if not isinstance(temperature, (np.ndarray, float)):
        raise TypeError("Temperature must be a float or an array.")
    if not isinstance(depth, (np.ndarray, float)):
        raise TypeError("Depth must be a float or an array.")
    if latitude is not None and not isinstance(latitude, (np.ndarray, float)):
        raise TypeError("Latitude must be a float or an array.")
    if longitude is not None and not isinstance(longitude, (np.ndarray, float)):
        raise TypeError("Longitude must be a float or an array.")

    # Check shape of inputs if they are numpy arrays
    if isinstance(conductivity, np.ndarray):
        conductivity = conductivity.squeeze()
        if conductivity.ndim > 1:
            raise ValueError("Conductivity must be a 1D array.")
    if isinstance(temperature, np.ndarray):
        temperature = temperature.squeeze()
        if temperature.ndim > 1:
            raise ValueError("Temperature must be a 1D array.")
    if isinstance(depth, np.ndarray):
        depth = depth.squeeze()
        if depth.ndim > 1:
            raise ValueError("Depth must be a 1D array.")
    if latitude is not None and isinstance(latitude, np.ndarray):
        latitude = latitude.squeeze()
        if latitude.ndim > 1:
            raise ValueError("Latitude must be a 1D array.")
    if longitude is not None and isinstance(longitude, np.ndarray):
        longitude = longitude.squeeze()
        if longitude.ndim > 1:
            raise ValueError("Longitude must be a 1D array.")

    # If latitude is not provided, set it to 0
    if latitude is None:
        latitude = 0 if isinstance(depth, float) else np.zeros_like(depth)
    elif isinstance(latitude, float) and isinstance(depth, np.ndarray):
        latitude = np.full_like(depth, latitude)

    # If longitude is not provided, set it to 0
    if longitude is None:
        longitude = 0 if isinstance(depth, float) else np.zeros_like(depth)
    elif isinstance(longitude, float) and isinstance(depth, np.ndarray):
        longitude = np.full_like(depth, longitude)

    # Check that the inputs are of the same shape
    if isinstance(conductivity, np.ndarray):
        if (
            conductivity.shape != temperature.shape
            or conductivity.shape != depth.shape
            or conductivity.shape != latitude.shape
            or conductivity.shape != longitude.shape
        ):
            raise ValueError(
                "Conductivity, temperature, depth, latitude, and longitude must have the same shape."
            )

    # Check that the depth is negative
    if isinstance(depth, np.ndarray):
        if np.any(depth > 0):
            raise ValueError("Depth must be negative.")
    else:
        if depth > 0:
            raise ValueError("Depth must be negative.")

    # Check that the latitude is between -90 and 90
    if isinstance(latitude, np.ndarray):
        if np.any(latitude < -90) or np.any(latitude > 90):
            raise ValueError("Latitude must be between -90 and 90 degrees.")
    else:
        if latitude < -90 or latitude > 90:
            raise ValueError("Latitude must be between -90 and 90 degrees.")

    # Check that the longitude is between -360 and 360
    if isinstance(longitude, np.ndarray):
        if np.any(longitude < -360) or np.any(longitude > 360):
            raise ValueError("Longitude must be between -360 and 360 degrees.")
    else:
        if longitude < -360 or longitude > 360:
            raise ValueError("Longitude must be between -360 and 360 degrees.")

    # Calculate sound velocity
    pressure = gsw.p_from_z(depth, latitude)
    practical_salinity = gsw.SP_from_C(conductivity, temperature, pressure)
    absolute_salinity = gsw.SA_from_SP(
        practical_salinity, pressure, longitude, latitude
    )
    conservative_temperature = gsw.CT_from_t(absolute_salinity, temperature, pressure)
    sound_speed = gsw.sound_speed(absolute_salinity, conservative_temperature, pressure)
    return sound_speed


def depth2pressure(
    depth: Union[float, np.ndarray, List[float]],
    latitude: Union[float, np.ndarray, List[float]] = None,
) -> Union[float, np.ndarray]:
    """
    Calculates pressure in dbars from depth in meters.

    Args:
        depth (Union[float, np.ndarray, List[float]]): Depth in meters.
        latitude (Union[float, np.ndarray, List[float]], optional): Latitude in degrees. Defaults to None.

    Returns:
        pressure (Union[float, np.ndarray]): Pressure in dbars.

    Raises:
        ValueError: If the latitude is not between -90 and 90 degrees.
    """
    # Convert to numpy arrays
    if isinstance(depth, list):
        depth = np.array(depth)
    if isinstance(latitude, list):
        latitude = np.array(latitude)

    # Check inputs type
    if not isinstance(depth, (np.ndarray, float)):
        raise TypeError("Depth must be a float or an array.")
    if latitude is not None and not isinstance(latitude, (np.ndarray, float)):
        raise TypeError("Latitude must be a float or an array.")

    # Check shape of inputs if they are numpy arrays
    if isinstance(depth, np.ndarray):
        depth = depth.squeeze()
        if depth.ndim > 1:
            raise ValueError("Depth must be a 1D array.")
    if latitude is not None and isinstance(latitude, np.ndarray):
        latitude = latitude.squeeze()
        if latitude.ndim > 1:
            raise ValueError("Latitude must be a 1D array.")

    # If latitude is not provided, set it to 0
    if latitude is None:
        latitude = 0 if isinstance(depth, float) else np.zeros_like(depth)
    elif isinstance(latitude, float) and isinstance(depth, np.ndarray):
        latitude = np.full_like(depth, latitude)

    # Check that the inputs are of the same shape
    if isinstance(depth, np.ndarray):
        if depth.shape != latitude.shape:
            raise ValueError("Depth and latitude must have the same shape.")

    # Check that the depth is negative
    if isinstance(depth, np.ndarray):
        if np.any(depth > 0):
            raise ValueError("Depth must be negative.")
    else:
        if depth > 0:
            raise ValueError("Depth must be negative.")

    # Check that the latitude is beetwen -90 and 90
    if isinstance(latitude, np.ndarray):
        if np.any(latitude < -90) or np.any(latitude > 90):
            raise ValueError("Latitude must be between -90 and 90 degrees.")
    else:
        if latitude < -90 or latitude > 90:
            raise ValueError("Latitude must be between -90 and 90 degrees.")

    return gsw.p_from_z(depth, latitude)


def ctp2salinity(
    conductivity: Union[float, np.ndarray, List[float]],
    temperature: Union[float, np.ndarray, List[float]],
    pressure: Union[float, np.ndarray, List[float]],
    latitude: Union[float, np.ndarray, List[float]] = None,
    longitude: Union[float, np.ndarray, List[float]] = None,
) -> Union[float, np.ndarray]:
    """
     Calculates absolute salinity in g/kg from conductivity, temperature, and pressure.

     Args:
        conductivity (Union[float, np.ndarray, List[float]]): Conductivity in S/m.
        temperature (Union[float, np.ndarray, List[float]]): Temperature in degrees Celsius (ITS-90).
        pressure (Union[float, np.ndarray, List[float]]): Pressure in dbars.
        latitude (Union[float, np.ndarray, List[float]], optional): Latitude in degrees. Defaults to None.
        longitude (Union[float, np.ndarray, List[float]], optional): Longitude in degrees. Defaults to None.

    Returns:
        absolute_salinity (Union[float, np.ndarray]): Absolute salinity in g/kg.

    Raises:
        TypeError: If the inputs are not of the correct type.
        ValueError: If the inputs are not of the correct shape or range.
    """
    # Convert to numpy arrays
    if isinstance(conductivity, list):
        conductivity = np.array(conductivity)
    if isinstance(temperature, list):
        temperature = np.array(temperature)
    if isinstance(pressure, list):
        pressure = np.array(pressure)
    if isinstance(latitude, list):
        latitude = np.array(latitude)
    if isinstance(longitude, list):
        longitude = np.array(longitude)

    # Check inputs type
    if not isinstance(conductivity, (np.ndarray, float)):
        raise TypeError("Conductivity must be a float or an array.")
    if not isinstance(temperature, (np.ndarray, float)):
        raise TypeError("Temperature must be a float or an array.")
    if not isinstance(pressure, (np.ndarray, float)):
        raise TypeError("Pressure must be a float or an array.")
    if latitude is not None and not isinstance(latitude, (np.ndarray, float)):
        raise TypeError("Latitude must be a float or an array.")
    if longitude is not None and not isinstance(longitude, (np.ndarray, float)):
        raise TypeError("Longitude must be a float or an array.")

    # Check shape of inputs if they are numpy arrays
    if isinstance(conductivity, np.ndarray):
        conductivity = conductivity.squeeze()
        if conductivity.ndim > 1:
            raise ValueError("Conductivity must be a 1D array.")
    if isinstance(temperature, np.ndarray):
        temperature = temperature.squeeze()
        if temperature.ndim > 1:
            raise ValueError("Temperature must be a 1D array.")
    if isinstance(pressure, np.ndarray):
        pressure = pressure.squeeze()
        if pressure.ndim > 1:
            raise ValueError("Pressure must be a 1D array.")
    if latitude is not None and isinstance(latitude, np.ndarray):
        latitude = latitude.squeeze()
        if latitude.ndim > 1:
            raise ValueError("Latitude must be a 1D array.")
    if longitude is not None and isinstance(longitude, np.ndarray):
        longitude = longitude.squeeze()
        if longitude.ndim > 1:
            raise ValueError("Longitude must be a 1D array.")

    # If latitude is not provided, set it to 0
    if latitude is None:
        latitude = 0 if isinstance(pressure, float) else np.zeros_like(pressure)
    elif isinstance(latitude, float) and isinstance(pressure, np.ndarray):
        latitude = np.full_like(pressure, latitude)

    # If longitude is not provided, set it to 0
    if longitude is None:
        longitude = 0 if isinstance(pressure, float) else np.zeros_like(pressure)
    elif isinstance(longitude, float) and isinstance(pressure, np.ndarray):
        longitude = np.full_like(pressure, longitude)

    # Check that the inputs are of the same shape
    if isinstance(conductivity, np.ndarray):
        if (
            conductivity.shape != temperature.shape
            or conductivity.shape != pressure.shape
            or conductivity.shape != latitude.shape
            or conductivity.shape != longitude.shape
        ):
            raise ValueError(
                "Conductivity, temperature, pressure, latitude, and longitude must have the same shape."
            )

    # Check that the latitude is beetwen -90 and 90
    if isinstance(latitude, np.ndarray):
        if np.any(latitude < -90) or np.any(latitude > 90):
            raise ValueError("Latitude must be between -90 and 90 degrees.")
    else:
        if latitude < -90 or latitude > 90:
            raise ValueError("Latitude must be between -90 and 90 degrees.")

    # Check that the longitude is beetwen -360 and 360
    if isinstance(longitude, np.ndarray):
        if np.any(longitude < -360) or np.any(longitude > 360):
            raise ValueError("Longitude must be between -360 and 360 degrees.")
    else:
        if longitude < -360 or longitude > 360:
            raise ValueError("Longitude must be between -360 and 360 degrees.")
    practical_salinity = gsw.SP_from_C(conductivity, temperature, pressure)
    absolute_salinity = gsw.SA_from_SP(
        practical_salinity, pressure, longitude, latitude
    )
    return absolute_salinity


def ctd2salinity(
    conductivity: Union[float, np.ndarray, List[float]],
    temperature: Union[float, np.ndarray, List[float]],
    depth: Union[float, np.ndarray, List[float]],
    latitude: Union[float, np.ndarray, List[float]] = None,
    longitude: Union[float, np.ndarray, List[float]] = None,
) -> Union[float, np.ndarray]:
    """
    Calculates absolute salinity in g/kg from conductivity, temperature, and depth.

    Args:
        conductivity (Union[float, np.ndarray, List[float]]): Conductivity in S/m.
        temperature (Union[float, np.ndarray, List[float]]): Temperature in degrees Celsius (ITS-90).
        depth (Union[float, np.ndarray, List[float]]): Depth in meters. Positive is upward.
        latitude (Union[float, np.ndarray, List[float]], optional): Latitude in degrees. Defaults to None.
        longitude (Union[float, np.ndarray, List[float]], optional): Longitude in degrees. Defaults to None.
    Returns:
        absolute_salinity (Union[float, np.ndarray]): Absolute salinity in g/kg.

    Raises:
        TypeError: If the inputs are not of the correct type.
        ValueError: If the inputs are not of the correct shape or range.
    """
    # Convert to numpy arrays
    if isinstance(conductivity, list):
        conductivity = np.array(conductivity)
    if isinstance(temperature, list):
        temperature = np.array(temperature)
    if isinstance(depth, list):
        depth = np.array(depth)
    if isinstance(latitude, list):
        latitude = np.array(latitude)
    if isinstance(longitude, list):
        longitude = np.array(longitude)

    # Check inputs type
    if not isinstance(conductivity, (np.ndarray, float)):
        raise TypeError("Conductivity must be a float or an array.")
    if not isinstance(temperature, (np.ndarray, float)):
        raise TypeError("Temperature must be a float or an array.")
    if not isinstance(depth, (np.ndarray, float)):
        raise TypeError("Depth must be a float or an array.")
    if latitude is not None and not isinstance(latitude, (np.ndarray, float)):
        raise TypeError("Latitude must be a float or an array.")
    if longitude is not None and not isinstance(longitude, (np.ndarray, float)):
        raise TypeError("Longitude must be a float or an array.")

    # Check shape of inputs if they are numpy arrays
    if isinstance(conductivity, np.ndarray):
        conductivity = conductivity.squeeze()
        if conductivity.ndim > 1:
            raise ValueError("Conductivity must be a 1D array.")
    if isinstance(temperature, np.ndarray):
        temperature = temperature.squeeze()
        if temperature.ndim > 1:
            raise ValueError("Temperature must be a 1D array.")
    if isinstance(depth, np.ndarray):
        depth = depth.squeeze()
        if depth.ndim > 1:
            raise ValueError("Depth must be a 1D array.")
    if latitude is not None and isinstance(latitude, np.ndarray):
        latitude = latitude.squeeze()
        if latitude.ndim > 1:
            raise ValueError("Latitude must be a 1D array.")
    if longitude is not None and isinstance(longitude, np.ndarray):
        longitude = longitude.squeeze()
        if longitude.ndim > 1:
            raise ValueError("Longitude must be a 1D array.")

    # If latitude is not provided, set it to 0
    if latitude is None:
        latitude = 0 if isinstance(depth, float) else np.zeros_like(depth)
    elif isinstance(latitude, float) and isinstance(depth, np.ndarray):
        latitude = np.full_like(depth, latitude)

    # If longitude is not provided, set it to 0
    if longitude is None:
        longitude = 0 if isinstance(depth, float) else np.zeros_like(depth)
    elif isinstance(longitude, float) and isinstance(depth, np.ndarray):
        longitude = np.full_like(depth, longitude)

    # Check that the inputs are of the same shape
    if isinstance(conductivity, np.ndarray):
        if (
            conductivity.shape != temperature.shape
            or conductivity.shape != depth.shape
            or conductivity.shape != latitude.shape
            or conductivity.shape != longitude.shape
        ):
            raise ValueError(
                "Conductivity, temperature, depth, latitude, and longitude must have the same shape."
            )

    # Check that the depth is negative
    if isinstance(depth, np.ndarray):
        if np.any(depth > 0):
            raise ValueError("Depth must be negative.")
    else:
        if depth > 0:
            raise ValueError("Depth must be negative.")

    # Check that the latitude is beetwen -90 and 90
    if isinstance(latitude, np.ndarray):
        if np.any(latitude < -90) or np.any(latitude > 90):
            raise ValueError("Latitude must be between -90 and 90 degrees.")
    else:
        if latitude < -90 or latitude > 90:
            raise ValueError("Latitude must be between -90 and 90 degrees.")

    # Check that the longitude is beetwen -360 and 360
    if isinstance(longitude, np.ndarray):
        if np.any(longitude < -360) or np.any(longitude > 360):
            raise ValueError("Longitude must be between -360 and 360 degrees.")
    else:
        if longitude < -360 or longitude > 360:
            raise ValueError("Longitude must be between -360 and 360 degrees.")

    # Calculate sound velocity
    pressure = gsw.p_from_z(depth, latitude)
    practical_salinity = gsw.SP_from_C(conductivity, temperature, pressure)
    absolute_salinity = gsw.SA_from_SP(
        practical_salinity, pressure, longitude, latitude
    )
    return absolute_salinity


def ctp2pden(
    conductivity: Union[float, np.ndarray, List[float]],
    temperature: Union[float, np.ndarray, List[float]],
    pressure: Union[float, np.ndarray, List[float]],
    latitude: Union[float, np.ndarray, List[float]] = None,
    longitude: Union[float, np.ndarray, List[float]] = None,
    pressure_reference: Union[float, np.ndarray, List[float]] = None,
) -> Union[float, np.ndarray]:
    """
    Calculates potential density (kg/m^3) relative to a reference pressure
    (default 0 dbar) from conductivity, temperature, and pressure using the gsw library.

    Args:
        conductivity (Union[float, np.ndarray, List[float]]): Conductivity in S/m.
        temperature (Union[float, np.ndarray, List[float]]): Temperature in degrees Celsius (ITS-90).
        pressure (Union[float, np.ndarray, List[float]]): Pressure in dbars.
        latitude (Union[float, np.ndarray, List[float]], optional): Latitude in degrees. Defaults to None.
        longitude (Union[float, np.ndarray, List[float]], optional): Longitude in degrees. Defaults to None.
        pressure_reference (Union[float, np.ndarray, List[float]], optional): Reference pressure in dbars. Defaults to None.

    Returns:
        potential_density (Union[float, np.ndarray]): Potential density in kg/m^3.

    Raises:
        TypeError: If the inputs are not of the correct type.
        ValueError: If the inputs are not of the correct shape or range.
    """
    # Convert to numpy arrays
    if isinstance(conductivity, list):
        conductivity = np.array(conductivity)
    if isinstance(temperature, list):
        temperature = np.array(temperature)
    if isinstance(pressure, list):
        pressure = np.array(pressure)
    if isinstance(latitude, list):
        latitude = np.array(latitude)
    if isinstance(longitude, list):
        longitude = np.array(longitude)
    if isinstance(pressure_reference, list):
        pressure_reference = np.array(pressure_reference)

    # Check inputs type
    if not isinstance(conductivity, (np.ndarray, float)):
        raise TypeError("Conductivity must be a float or an array.")
    if not isinstance(temperature, (np.ndarray, float)):
        raise TypeError("Temperature must be a float or an array.")
    if not isinstance(pressure, (np.ndarray, float)):
        raise TypeError("Pressure must be a float or an array.")
    if latitude is not None and not isinstance(latitude, (np.ndarray, float)):
        raise TypeError("Latitude must be a float or an array.")
    if longitude is not None and not isinstance(longitude, (np.ndarray, float)):
        raise TypeError("Longitude must be a float or an array.")
    if pressure_reference is not None and not isinstance(
        pressure_reference, (np.ndarray, float)
    ):
        raise TypeError("Pressure reference must be a float or an array.")

    # Check shape of inputs if they are numpy arrays
    if isinstance(conductivity, np.ndarray):
        conductivity = conductivity.squeeze()
        if conductivity.ndim > 1:
            raise ValueError("Conductivity must be a 1D array.")
    if isinstance(temperature, np.ndarray):
        temperature = temperature.squeeze()
        if temperature.ndim > 1:
            raise ValueError("Temperature must be a 1D array.")
    if isinstance(pressure, np.ndarray):
        pressure = pressure.squeeze()
        if pressure.ndim > 1:
            raise ValueError("Pressure must be a 1D array.")
    if latitude is not None and isinstance(latitude, np.ndarray):
        latitude = latitude.squeeze()
        if latitude.ndim > 1:
            raise ValueError("Latitude must be a 1D array.")
    if longitude is not None and isinstance(longitude, np.ndarray):
        longitude = longitude.squeeze()
        if longitude.ndim > 1:
            raise ValueError("Longitude must be a 1D array.")
    if pressure_reference is not None and isinstance(pressure_reference, np.ndarray):
        pressure_reference = pressure_reference.squeeze()
        if pressure_reference.ndim > 1:
            raise ValueError("Pressure reference must be a 1D array.")

    # If latitude is not provided, set it to 0
    if latitude is None:
        latitude = 0 if isinstance(pressure, float) else np.zeros_like(pressure)
    elif isinstance(latitude, float) and isinstance(pressure, np.ndarray):
        latitude = np.full_like(pressure, latitude)

    # If longitude is not provided, set it to 0
    if longitude is None:
        longitude = 0 if isinstance(pressure, float) else np.zeros_like(pressure)
    elif isinstance(longitude, float) and isinstance(pressure, np.ndarray):
        longitude = np.full_like(pressure, longitude)

    # If pressure reference is not provided, set it to 0
    if pressure_reference is None:
        pressure_reference = (
            0 if isinstance(pressure, float) else np.zeros_like(pressure)
        )
    elif isinstance(pressure_reference, float) and isinstance(pressure, np.ndarray):
        pressure_reference = np.full_like(pressure, pressure_reference)

    # Check that the inputs are of the same shape
    if isinstance(conductivity, np.ndarray):
        if (
            conductivity.shape != temperature.shape
            or conductivity.shape != pressure.shape
            or conductivity.shape != latitude.shape
            or conductivity.shape != longitude.shape
            or conductivity.shape != pressure_reference.shape
        ):
            raise ValueError(
                "Conductivity, temperature, pressure, latitude, longitude and reference pressure must have the same shape."
            )

    # Check that the latitude is beetwen -90 and 90
    if isinstance(latitude, np.ndarray):
        if np.any(latitude < -90) or np.any(latitude > 90):
            raise ValueError("Latitude must be between -90 and 90 degrees.")
    else:
        if latitude < -90 or latitude > 90:
            raise ValueError("Latitude must be between -90 and 90 degrees.")

    # Check that the longitude is beetwen -360 and 360
    if isinstance(longitude, np.ndarray):
        if np.any(longitude < -360) or np.any(longitude > 360):
            raise ValueError("Longitude must be between -360 and 360 degrees.")
    else:
        if longitude < -360 or longitude > 360:
            raise ValueError("Longitude must be between -360 and 360 degrees.")

    # Compute potential density using the exact potential density function
    practical_salinity = gsw.SP_from_C(conductivity, temperature, pressure)
    absolute_salinity = gsw.SA_from_SP(
        practical_salinity, pressure, longitude, latitude
    )
    pden = gsw.pot_rho_t_exact(
        absolute_salinity, temperature, pressure, pressure_reference
    )
    return pden


def ctd2oxygen_saturation(
    conductivity: Union[float, np.ndarray, List[float]],
    temperature: Union[float, np.ndarray, List[float]],
    depth: Union[float, np.ndarray, List[float]],
    latitude: Union[float, np.ndarray, List[float]] = None,
    longitude: Union[float, np.ndarray, List[float]] = None,
) -> Union[float, np.ndarray]:
    """
    Calculates the oxygen saturation value (ml/l) from salinity and temperature.

    Calculates the oxygen concentration expected at equilibrium with air at an
    Absolute Pressure of 101325 Pa (sea pressure of 0 dbar) including saturated
    water vapor. This function uses the solubility coefficients derived from the
    data of Benson and Krause (1984), as fitted by Garcia and Gordon (1992, 1993).

    Args:
        conductivity (Union[float, np.ndarray, List[float]]): Conductivity in S/m.
        temperature (Union[float, np.ndarray, List[float]]): Temperature in degrees Celsius (ITS-90).
        depth (Union[float, np.ndarray, List[float]]): Depth in meters. Positive is upward.
        latitude (Union[float, np.ndarray, List[float]], optional): Latitude in degrees. Defaults to None.
        longitude (Union[float, np.ndarray, List[float]], optional): Longitude in degrees. Defaults to None.

    Returns:
        solubility (Union[float, np.ndarray]): Solubility of oxygen in micro-moles per kg

    Raises:
        TypeError: If the inputs are not of the correct type.
        ValueError: If the inputs are not of the correct shape or range.
    """
    # Convert to numpy arrays
    if isinstance(conductivity, list):
        conductivity = np.array(conductivity)
    if isinstance(temperature, list):
        temperature = np.array(temperature)
    if isinstance(depth, list):
        depth = np.array(depth)
    if isinstance(latitude, list):
        latitude = np.array(latitude)
    if isinstance(longitude, list):
        longitude = np.array(longitude)

    # Check inputs type
    if not isinstance(conductivity, (np.ndarray, float)):
        raise TypeError("Conductivity must be a float or an array.")
    if not isinstance(temperature, (np.ndarray, float)):
        raise TypeError("Temperature must be a float or an array.")
    if not isinstance(depth, (np.ndarray, float)):
        raise TypeError("Depth must be a float or an array.")
    if latitude is not None and not isinstance(latitude, (np.ndarray, float)):
        raise TypeError("Latitude must be a float or an array.")
    if longitude is not None and not isinstance(longitude, (np.ndarray, float)):
        raise TypeError("Longitude must be a float or an array.")

    # Check shape of inputs if they are numpy arrays
    if isinstance(conductivity, np.ndarray):
        conductivity = conductivity.squeeze()
        if conductivity.ndim > 1:
            raise ValueError("Conductivity must be a 1D array.")
    if isinstance(temperature, np.ndarray):
        temperature = temperature.squeeze()
        if temperature.ndim > 1:
            raise ValueError("Temperature must be a 1D array.")
    if isinstance(depth, np.ndarray):
        depth = depth.squeeze()
        if depth.ndim > 1:
            raise ValueError("Depth must be a 1D array.")
    if latitude is not None and isinstance(latitude, np.ndarray):
        latitude = latitude.squeeze()
        if latitude.ndim > 1:
            raise ValueError("Latitude must be a 1D array.")
    if longitude is not None and isinstance(longitude, np.ndarray):
        longitude = longitude.squeeze()
        if longitude.ndim > 1:
            raise ValueError("Longitude must be a 1D array.")

    # If latitude is not provided, set it to 0
    if latitude is None:
        latitude = 0 if isinstance(depth, float) else np.zeros_like(depth)
    elif isinstance(latitude, float) and isinstance(depth, np.ndarray):
        latitude = np.full_like(depth, latitude)

    # If longitude is not provided, set it to 0
    if longitude is None:
        longitude = 0 if isinstance(depth, float) else np.zeros_like(depth)
    elif isinstance(longitude, float) and isinstance(depth, np.ndarray):
        longitude = np.full_like(depth, longitude)

    # Check that the inputs are of the same shape
    if isinstance(conductivity, np.ndarray):
        if (
            conductivity.shape != temperature.shape
            or conductivity.shape != depth.shape
            or conductivity.shape != latitude.shape
            or conductivity.shape != longitude.shape
        ):
            raise ValueError(
                "Conductivity, temperature, depth, latitude, and longitude must have the same shape."
            )

    # Check that the depth is negative
    if isinstance(depth, np.ndarray):
        if np.any(depth > 0):
            raise ValueError("Depth must be negative.")
    else:
        if depth > 0:
            raise ValueError("Depth must be negative.")

    # Check that the latitude is between -90 and 90
    if isinstance(latitude, np.ndarray):
        if np.any(latitude < -90) or np.any(latitude > 90):
            raise ValueError("Latitude must be between -90 and 90 degrees.")
    else:
        if latitude < -90 or latitude > 90:
            raise ValueError("Latitude must be between -90 and 90 degrees.")

    # Check that the longitude is between -360 and 360
    if isinstance(longitude, np.ndarray):
        if np.any(longitude < -360) or np.any(longitude > 360):
            raise ValueError("Longitude must be between -360 and 360 degrees.")
    else:
        if longitude < -360 or longitude > 360:
            raise ValueError("Longitude must be between -360 and 360 degrees.")

    # Calculate sound velocity
    pressure = gsw.p_from_z(depth, latitude)
    practical_salinity = gsw.SP_from_C(conductivity, temperature, pressure)
    absolute_salinity = gsw.SA_from_SP(
        practical_salinity, pressure, longitude, latitude
    )
    conservative_temperature = gsw.CT_from_t(absolute_salinity, temperature, pressure)
    o2sol = gsw.O2sol(
        absolute_salinity, conservative_temperature, pressure, longitude, latitude
    )
    return o2sol
