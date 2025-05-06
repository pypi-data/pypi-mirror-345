import numpy as np
from typing import Union, Iterable
import pandas as pd


def swrad2par(
        swrad: Union[pd.Series, int, float]) -> Union[pd.Series, int, float]:
    """
    Convert radiation from [kW m^-2] to [kJ m^-2 day^-1].

    Parameters
    ----------
    swrad : int, float, or pandas.Series
        Radiation in [kW m^-2].

    Returns
    -------
    par : int, float, or pandas.Series
        Radiation in [kJ m^-2 day^-1].
    """
    return swrad * 0.45 * 3600 * 24


def get_tmin_func(tmin: Union[float, int, Iterable], tmin_min: float,
                  tmin_max: float) -> np.ndarray:
    """
    Get the TMNIN restriction function.

    Parameters
    ----------
    tmin : float, int, or iterable
        The minimum temperature.
    tmin_min : float
        The minimum temperature threshold.
    tmin_max : float
        The maximum temperature threshold.

    Returns
    -------
    np.ndarray
        The TMNIN restriction function.
    """
    tmin = np.asarray(tmin)

    return np.clip((tmin - tmin_min) / (tmin_max - tmin_min), 0, 1)


def get_vpd_func(vpd: Union[float, int, Iterable], vpd_min: float,
                 vpd_max: float) -> np.ndarray:
    """
    Get the VPD restriction function.

    Parameters
    ----------
    vpd : float, int, or iterable
        The vapor pressure deficit.
    vpd_min : float
        The minimum vapor pressure deficit threshold.
    vpd_max : float
        The maximum vapor pressure deficit threshold.

    Returns
    -------
    np.ndarray
        The VPD restriction function.
    """

    vpd = np.asarray(vpd)

    return 1 - np.clip((vpd - vpd_min) / (vpd_max - vpd_min), 0, 1)


def calc_gpp(par, fapar, tmin, vpd, eps_max, tmin_min, tmin_max, vpd_min,
             vpd_max):
    """
    Models the GPP, given some data and parameters

            Parameters:
                    par (np.array): (data) par, as calculated using swrad2par
                    fapar (np.array): (data) fapar, gfrom the modis data
                    tmin (np.array): (data) minimum temperature of the day measured by fluxnet
                    vpd (np.array): (data) mean vpd of the day measured by fluxnet
                    eps_max (float): (parameter) Maximum light use efficiency under ideal conditions
                    tmin_min (float): (parameter) Lower end of the min temperature ramp.
                                        If the min temperature is lower than this value,
                                        photosynthesis will cease due to temperature stress
                    tmin_max (float): (parameter) Upper end of the min temperature ramp.
                                        If the min temperature is higher than this value, the temperature
                                        is not limiting photosynthesis
                    vpd_min (float): (parameter) Lower end of the vpd ramp.
                                        If the vpd is lower than this value, the vpd is not limiting photosynthesis
                    vpd_max (float): (parameter) Upper end of the vdp ramp.
                                        If the vpd is higher than this value, photosynthesis will cease due to
                                        water stress
            Returns:
                    gpp (np.array): Modeled GPP for the given conditions
    """
    f_tmin = get_tmin_func(tmin, tmin_min, tmin_max)
    f_vpd = get_vpd_func(vpd, vpd_min, vpd_max)

    gpp = par * fapar * eps_max * f_tmin * f_vpd
    return gpp
