import re

# NumPy
import numpy as np
# AstroPy
import astropy.units as u
from astropy.time import Time, TimeDelta
from astropy.coordinates import EarthLocation
# Astroquery
from astroquery.mpc import MPC


def totalMagnitude(Delta, r_h, M1, K1):
    """
    m1 = M1 + 5 * log10(Delta) + K1 * log10(r_h)
    """

    m1 = M1 + 5 * np.log10(Delta) + K1 * np.log10(r_h)

    return m1


def timeTag(epoch):
    """
    """

    if re.search("^\d+[ydhms]$", epoch["step"]):
        if epoch["step"][-1] == "y":
            dt = TimeDelta(int(epoch["step"][:-1]) * u.Unit("yr"))
        elif epoch["step"][-1] == "d":
            dt = TimeDelta(int(epoch["step"][:-1]) * u.Unit("d"))
        elif epoch["step"][-1] == "h":
            dt = TimeDelta(int(epoch["step"][:-1]) * u.Unit("h"))
        elif epoch["step"][-1] == "m":
            dt = TimeDelta(int(epoch["step"][:-1]) * u.Unit("min"))
        else:
            dt = TimeDelta(int(epoch["step"][:-1]) * u.Unit("s"))
    
    time_tag = Time(epoch["start"]) + np.arange(int((Time(epoch["stop"]) - Time(epoch["start"])) / dt + 1)) * dt

    return time_tag


def siteLocation(IAU_code):
    """
    """

    # Get MPC coordinates
    longitude, rho_cos_phi, rho_sin_phi, name = MPC.get_observatory_location(IAU_code)

    # Convert to longitude, latitude, and radius (in [cm]) refer to geocenter
    lon = longitude.value / 180 * np.pi
    lat = np.arctan(rho_sin_phi / rho_cos_phi)
    r = np.sqrt(rho_sin_phi**2 + rho_cos_phi**2) * 6378137 * 100

    # Convert to Cartesian coordinates in [cm]
    x, y, z = r * np.cos(lat) * np.cos(lon), r * np.cos(lat) * np.sin(lon), r * np.sin(lat)

    site_location = EarthLocation.from_geocentric(x, y, z, unit=u.Unit("cm"))

    return site_location