import re
# NumPy
import numpy as np
# AstroPy
from astropy.time import Time
from astropy.table import Table, vstack

def toSkyfieldFormat(catalog, database):
    """
    """

    if not isinstance(catalog, Table):
        raise ValueError("<class `astropy.table.table.Table`> is required for `catalog`.")

    if database == "jpl":

        # Add perihelion year, perihelion month, and perihelion day
        # !!! Note the conversion from TDB to TT !!!
        perihelion_time = Time(catalog["tp"].data, scale="tdb", format="jd").tt.ymdhms
        catalog["perihelion_year"]  = np.array([time[0] for time in perihelion_time])
        catalog["perihelion_month"] = np.array([time[1] for time in perihelion_time])
        catalog["perihelion_day"]   = np.array([((time[5] / 60 + time[4]) / 60 + time[3]) / 24 + time[2] for time in perihelion_time])

        # Delete perihelion time
        del catalog["tp"]

        # Rename columns
        catalog.rename_columns(["pdes", 
                                "q", 
                                "e", 
                                "w", 
                                "om", 
                                "i", 
                                "M1", 
                                "K1", 
                                "orbit_id"], 
                               ["designation", 
                                "perihelion_distance_au", 
                                "eccentricity", 
                                "argument_of_perihelion_degrees", 
                                "longitude_of_ascending_node_degrees", 
                                "inclination_degrees", 
                                "magnitude_g", 
                                "magnitude_k", 
                                "reference"])

        # Reorder columns
        catalog = catalog["designation",
                          "perihelion_year", 
                          "perihelion_month", 
                          "perihelion_day", 
                          "perihelion_distance_au", 
                          "eccentricity", 
                          "argument_of_perihelion_degrees", 
                          "longitude_of_ascending_node_degrees", 
                          "inclination_degrees", 
                          "magnitude_g", 
                          "magnitude_k", 
                          "reference"]

    elif database == "mpc":

        # - Columns
        # 1. designation -> primary designation (defined by JPL)
        pdes_list = list()
        for designation in catalog["designation"].data:
            if re.search("^\d+[PI]", designation.split("/")[0]):
                pdes_list.append(designation.split("/")[0])
            else:
                pdes_list.append(designation.split("/")[1].split(" (")[0])
        catalog["designation"] = pdes_list
        # 2. K1 = 2.5 * k (defined by JPL)
        catalog["magnitude_k"] *= 2.5

        # - Remove duplicate (keep only the most recent orbit for each comet)
        catalog.sort("designation")
        catalog = catalog.group_by(["designation"])
        catalog = catalog[catalog.groups.indices[1:] - 1]

        # - Sort
        # 1. Split into numbered, unnumbered, and interstellar catalogs
        idx_list_numbered = list()
        idx_list_unnumbered = list()
        idx_list_interstellar = list()
        for i, pdes in enumerate(catalog["designation"].data):
            if re.search("^\d+P", pdes):
                idx_list_numbered.append(i)
            elif re.search("^\d+I", pdes):
                idx_list_interstellar.append(i)
            else:
                idx_list_unnumbered.append(i)
        catalog_numbered = catalog[idx_list_numbered]
        catalog_unnumbered = catalog[idx_list_unnumbered]
        catalog_interstellar = catalog[idx_list_interstellar]
        # 2. Sort numbered and interstellar catalogs (unnumbered catalog is already sorted)
        pdes_list = list()
        for pdes in catalog_numbered["designation"].data:
            number = re.search("^\d+", pdes).group()
            pdes_list.append(pdes.replace(number, f"{int(number):08d}"))
            idx_list_sorted = sorted(range(len(pdes_list)), key=pdes_list.__getitem__)
        catalog_numbered = catalog_numbered[idx_list_sorted]
        pdes_list = list()
        for pdes in catalog_interstellar["designation"].data:
            number = re.search("^\d+", pdes).group()
            pdes_list.append(pdes.replace(number, f"{int(number):08d}"))
        idx_list_sorted = sorted(range(len(pdes_list)), key=pdes_list.__getitem__)
        catalog_interstellar = catalog_interstellar[idx_list_sorted]
        # 3. Concatenate
        catalog = vstack([catalog_numbered, catalog_unnumbered, catalog_interstellar])

    else:
        raise ValueError("One of the two databases, `mpc` and `jpl`, is required.")

    return catalog