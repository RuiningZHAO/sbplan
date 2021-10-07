"""
Ephemeris
-------

:Author: Ruining ZHAO (rnzhao@nao.cas.cn)
"""
import os
from astropy import config as _config

class Conf(_config.ConfigNamespace):
    """
    Configuration parameters for `sbplan.ephemeris`.
    """
    lib_dir = _config.ConfigItem(
        os.path.join(os.path.dirname(__file__), "lib"), "Path to the directory of library.", cfgtype="string")

#     query_url = _config.ConfigItem(
#         "https://ssd-api.jpl.nasa.gov/sbdb_query.api", "JPL Small-Body Database Search Engine URL.", cfgtype="string")
    params = _config.ConfigItem(
        ["RA", "DEC", "AZ", "EL", "delta", "r", "alpha", "elong", "lunar_elong", "Tmag"], "Parameters that can be returned.", cfgtype="list")

#     timeout = _config.ConfigItem(
#         60, "Time limit for connecting to JPL server.", cfgtype="integer")

conf = Conf()

from .core import CometEphemerides, CometEphemeridesClass

__all__ = ["CometEphemerides", "CometEphemeridesClass", "conf"]