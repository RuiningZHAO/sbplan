"""
"""

# NumPy
import numpy as np
# AstroPy
import astropy.units as u
from astropy.time import Time
from astropy.table import Table
from astropy.coordinates import EarthLocation
# skyfield
from skyfield.api import Loader, wgs84
from skyfield.data import mpc
from skyfield.constants import GM_SUN_Pitjeva_2005_km3_s2 as GM_SUN

from . import conf
from .utils import totalMagnitude

__all__ = ["CometEphemerides", "CometEphemeridesClass"]


class CometEphemeridesClass(object):


    LIB_DIR = conf.lib_dir
    PARAMS = conf.params


    def __init__(self, time_tag=None, location=None):
        """
        Initialize a comet ephemerides class.

        Parameters
        ----------
        time_tag : astropy.time.core.Time
            Time tag.

        location : astropy.coordinates.earth.EarthLocation
            Site location.
        """

        super(CometEphemeridesClass, self).__init__()

        self.time_tag = self._check_time_tag_dtype(time_tag)
        self.location = self._check_location_dtype(location)

        if (self.time_tag is not None) & (self.location is not None):
            # - Loader
            self.load = Loader(self.LIB_DIR)
            # - Settings
            # 1. Time
            self.ts = self.load.timescale()
            self.t = self.ts.from_astropy(time_tag)
            # 2. Ephemerides (sun, earth, moon)
            DE421 = self.load("de421.bsp")
            self.sun, self.earth, self.moon = DE421["sun"], DE421["earth"], DE421["moon"]
            # 3. Site location
            lon, lat, height = self.location.geodetic
            self.observer = (
                self.earth + wgs84.latlon(
                    latitude_degrees=lat.to(u.degree).value, 
                    longitude_degrees=lon.to(u.degree).value, 
                    elevation_m=height.to(u.m).value
                )
            )


    def __call__(self, *args, **kwargs):
        """ 
        Initialize a fresh copy of self
        """

        return self.__class__(*args, **kwargs)


    def get(self, catalog, params):
        """
        Calculate ephemerides.

        Parameters
        ----------
        catalog : astropy.table.table.Table
            Comet catalog.
        params : list
            List of parameters.

        Returns
        -------
        ephemerides : dict
            Ephemerides.
        """
        
        self.catalog = self._check_catalog_dtype(catalog)
        self.params = self._check_params_dtype(params)
        
        # - Observation
        # 1. Sun
        if ("r"     in self.params) or\
           ("alpha" in self.params) or\
           ("elong" in self.params) or\
           ("Tmag"  in self.params):
            s = self.observer.at(self.t).observe(self.sun).apparent()
            if ("r"     in self.params) or\
               ("alpha" in self.params) or\
               ("Tmag"  in self.params):
                _, _, earth_to_sun  = s.altaz(); earth_to_sun  = earth_to_sun.au
        # 2. Moon
        if "lunar_elong" in self.params:
            m = self.observer.at(self.t).observe(self.moon).apparent()
#             if "lunar_illum" in self.params:
#                 _, _, earth_to_moon = m.altaz(); earth_to_moon = earth_to_moon.au
#                 SOM = s.separation_from(m); SOM = SOM.degrees
#                 i = np.arctan2(earth_to_sun * np.sin(SOM / 180.0 * np.pi), 
#                                earth_to_moon - earth_to_sun * np.cos(SOM / 180.0 * np.pi))
#                 k = (1 + np.cos(i)) / 2.0

        self.ephemerides = dict()
        catalog = self.catalog.to_pandas().set_index("designation", drop=False)
        for pdes in catalog["designation"].to_numpy():
            # 3. Comet (loop over catalog)
            row = catalog.loc[pdes]
            comet = self.sun + mpc.comet_orbit(row, self.ts, GM_SUN)
            c = self.observer.at(self.t).observe(comet).apparent()

            # - Parameters
            table = dict()
            # 1. RA [deg], DEC [deg], and geocentric distance [au]
            if ("RA"    in self.params) or\
               ("DEC"   in self.params) or\
               ("delta" in self.params) or\
               ("r"     in self.params) or\
               ("alpha" in self.params) or\
               ("Tmag"  in self.params):
                RA, DEC, Delta = c.radec()
                RA, DEC, Delta = RA._degrees, DEC.degrees, Delta.au
                if "RA"    in self.params: table["RA"]    = RA    * u.Unit("deg")
                if "DEC"   in self.params: table["DEC"]   = DEC   * u.Unit("deg")
                if "delta" in self.params: table["delta"] = Delta * u.Unit("au" )
            
            # 2. EL [deg] and AZ [deg]
            if ("AZ" in self.params) or\
               ("EL" in self.params):
                EL, AZ, _ = c.altaz(); EL, AZ = EL.degrees, AZ.degrees
                if "EL" in self.params: table["EL"] = EL * u.Unit("deg")
                if "AZ" in self.params: table["AZ"] = AZ * u.Unit("deg")

            # 3. Lunar elongation [deg]
            if "lunar_elong" in self.params:
                MOT = m.separation_from(c); MOT = MOT.degrees
                table["lunar_elong"] = MOT * u.Unit("deg")

            # 4. Solar elongation [deg]
            if ("r"     in self.params) or\
               ("alpha" in self.params) or\
               ("elong" in self.params) or\
               ("Tmag"  in self.params):
                SOT = s.separation_from(c); SOT = SOT.degrees
                if "elong" in self.params: table["elong"] = SOT * u.Unit("deg")

            # 5. Heliocentric distance [au]
            if ("r"    in self.params) or\
               ("Tmag" in self.params):
                r_h = np.sqrt(
                    Delta**2 + earth_to_sun**2 - 2.0 * Delta * earth_to_sun 
                    * np.cos(SOT * np.pi / 180.0)
                )
                if "r" in self.params:
                    table["r"] = r_h * u.Unit("au")

            # 6. Phase angle [deg]
            if "alpha" in self.params:
                alpha = 180.0 / np.pi * np.arctan2(
                    earth_to_sun * np.sin(SOT / 180.0 * np.pi), 
                    Delta - earth_to_sun * np.cos(SOT / 180.0 * np.pi)
                )
                table["alpha"] = alpha * u.Unit("deg")

            # 7. Magnitude [mag]
            if "Tmag" in self.params:
                m1 = totalMagnitude(
                    Delta=Delta, r_h=r_h, M1=row["magnitude_g"], K1=row["magnitude_k"])
                table["Tmag"] = m1 * u.Unit("mag")

            self.ephemerides[pdes] = Table(table)

        return self.time_tag, self.ephemerides


    def _check_time_tag_dtype(self, time_tag):
        """
        """

        if time_tag is not None:
            if not isinstance(time_tag, Time):
                raise ValueError("`astropy.time.core.Time` is required for `time_tag`.")
        
        return time_tag


    def _check_location_dtype(self, location):
        """
        """

        if location is not None:
            if not isinstance(location, EarthLocation):
                raise ValueError(
                    "`astropy.coordinates.earth.EarthLocation` is required for `location`.")
    
        return location


    def _check_catalog_dtype(self, catalog):
        """
        """
        if not isinstance(catalog, Table):
            raise ValueError("`astropy.table.table.Table` is required for `catalog`.")

        return catalog


    def _check_params_dtype(self, params):
        """
        """

        if not isinstance(params, (str, list)):
            raise TypeError(f"A `str` or a `list` from {self.PARAMS} is required.")
        elif isinstance(params, str):
            if params not in self.PARAMS:
                raise ValueError(f"A `str` or a `list` from {self.PARAMS} is required.")
            else:
                params = [params]
        elif isinstance(params, list):
            for param in params:
                if param not in self.PARAMS:
                    raise ValueError(
                        f"A `str` or a `list` from {self.PARAMS} is required.")
        
        return params


# the default tool for users to interact with is an instance of the Class
CometEphemerides = CometEphemeridesClass()