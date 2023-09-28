"""
Catalog
-------

:Author: Ruining ZHAO (rnzhao@nao.cas.cn)
"""
import os

# AstroPy
import astropy.config as _config

from .core import CometCatalog, CometCatalogClass

__all__ = ['CometCatalog', 'CometCatalogClass', 'conf']


class Conf(_config.ConfigNamespace):
    """
    Configuration parameters for `sbplan.catalog`.
    """

    query_url = _config.ConfigItem(
        'https://ssd-api.jpl.nasa.gov/sbdb_query.api', cfgtype='string', 
        description=(
            'JPL Small-Body Database Search Engine URL.'
        )
    )

    timeout = _config.ConfigItem(
        60, cfgtype='integer', 
        description=(
            'Time limit for connecting to JPL server.'
        )
    )

    catalog_dir = _config.ConfigItem(
        os.path.join(os.path.dirname(__file__), 'lib'), cfgtype='string', 
        description=(
            'Path to the directory where the catalogs are stored.'
        )
    )

    catalog_type = _config.ConfigItem(
        ['all', 'obs'], cfgtype='list', 
        description=(
            'Pre-defined types of catalog.'
        )
    )

conf = Conf()

del _config