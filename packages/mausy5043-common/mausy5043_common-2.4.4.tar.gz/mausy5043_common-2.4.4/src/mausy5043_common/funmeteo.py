#!/usr/bin/env python3

# mausy5043-common
# Copyright (C) 2025  Maurice (mausy5043) Hendrix
# AGPL-3.0-or-later  - see LICENSE

"""Provide various meteorological conversions."""

import numpy as np


def moisture(temperature: float, relative_humidity: float, pressure: float) -> np.ndarray:
    """Calculate moisture content of air given T, RH and P.

    Args:
        temperature: in degC
        relative_humidity: in %
        pressure: in mbara or hPa

    Returns:
        np.array: moisture content in kg/m3
    """
    kelvin: float = temperature + 273.15
    pascal: float = pressure * 100
    rho: float = (287.04 * kelvin) / pascal

    es: float = 611.2 * np.exp(17.67 * (kelvin - 273.15) / (kelvin - 29.65))
    rvs: float = 0.622 * es / (pascal - es)
    rv: float = relative_humidity / 100.0 * rvs
    qv: float = rv / (1 + rv)
    moistair: float = qv * rho * 1000  # g water per m3 air
    return np.array([moistair])


def wet_bulb_temperature(temperature: float, relative_humidity: float) -> float:
    """Calculate the wet bulb temperature of the air given T and RH.

    Args:
        temperature: in degC
        relative_humidity: in %

    Returns:
        Wet bulb temperature in degC
    """
    wbt: float = (
        temperature * np.arctan(0.151977 * np.sqrt(relative_humidity + 8.313659))
        + np.arctan(temperature + relative_humidity)
        - np.arctan(relative_humidity - 1.676331)
        + 0.00391838 * np.power(relative_humidity, 1.5) * np.arctan(0.023101 * relative_humidity)
        - 4.686035
    )
    return wbt
