"""
Catalog
-------

:Author: Ruining ZHAO (rnzhao@nao.cas.cn)
"""
import os
from astropy import config as _config

class Conf(_config.ConfigNamespace):
    """
    Configuration parameters for `sbplan.catalog`.
    """
    query_url = _config.ConfigItem(
        "https://ssd-api.jpl.nasa.gov/sbdb_query.api", "JPL Small-Body Database Search Engine URL.", cfgtype="string")

    timeout = _config.ConfigItem(
        60, "Time limit for connecting to JPL server.", cfgtype="integer")

    catalog_dir = _config.ConfigItem(
        os.path.join(os.path.dirname(__file__), "lib"), "Path to the directory where the catalogs are stored.", cfgtype="string")

    catalog_type = _config.ConfigItem(
        ["all", "obs"], "Pre-defined types of catalog", cfgtype="list")

conf = Conf()

from .core import CometCatalog, CometCatalogClass

__all__ = ["CometCatalog", "CometCatalogClass", "conf"]