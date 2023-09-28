"""
Ephemerides
-------

:Author: Ruining ZHAO (rnzhao@nao.cas.cn)
"""

import os

# AstroPy
from astropy.config as _config

from .core import CometEphemerides, CometEphemeridesClass

__all__ = ['CometEphemerides', 'CometEphemeridesClass', 'conf']


class Conf(_config.ConfigNamespace):
    """
    Configuration parameters for `sbplan.ephemerides`.
    """

    lib_dir = _config.ConfigItem(
        os.path.join(os.path.dirname(__file__), 'lib'), cfgtype='string', 
        description=(
            'Path to the directory of library.'
        )
    )

    # query_url = _config.ConfigItem(
    #     'https://ssd-api.jpl.nasa.gov/sbdb_query.api', cfgtype='string', 
    #     description=(
    #         'JPL Small-Body Database Search Engine URL.'
    #     )
    # )

    params = _config.ConfigItem(
        ['RA', 'DEC', 'AZ', 'EL', 'delta', 'r', 'alpha', 'elong', 'lunar_elong', 'Tmag'], 
        cfgtype='list', 
        description=(
            'Parameters that can be returned.'
        )
    )

    # timeout = _config.ConfigItem(
    #     60, cfgtype='integer', 
    #     descroption=(
    #         'Time limit for connecting to JPL server.'
    #     )
    # )


conf = Conf()

del _config