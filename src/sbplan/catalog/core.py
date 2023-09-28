"""
"""

import os, json

# AstroPy
from astropy.table import Table

# astroquery
from astroquery.query import BaseQuery

from . import conf

__all__ = ["CometCatalog", "CometCatalogClass"]


class CometCatalogClass(BaseQuery):

    QUERY_URL = conf.query_url
    TIMEOUT = conf.timeout
    CATALOG_DIR = conf.catalog_dir
    CATALOG_TYPE = conf.catalog_type


    def __init__(self):
        """
        Initialize a comet catalog class.
        """
        super(CometCatalogClass, self).__init__()


    def get(self, cat_type=CATALOG_TYPE, update=False, verbose=False):
        """
        """
        
        self._check_cat_type_dtype(cat_type)

        if isinstance(cat_type, list):

            catalog = list()
            for cat_type_item in cat_type:

                catalog_path = os.path.join(self.CATALOG_DIR, f"comet_catalog_{cat_type_item}.csv")
                if (not os.path.exists(catalog_path)) | update:
                    self._update(cat_type=cat_type_item, verbose=verbose)

                catalog.append(self._get(cat_type=cat_type_item))

        else:
            
            catalog_path = os.path.join(self.CATALOG_DIR, f"comet_catalog_{cat_type}.csv")
            if (not os.path.exists(catalog_path)) | update:
                self._update(cat_type=cat_type, verbose=verbose)

            catalog = self._get(cat_type=cat_type)

        return catalog


    def _get(self, cat_type):
        """
        """
            
        catalog_path = os.path.join(self.CATALOG_DIR, f"comet_catalog_{cat_type}.csv")
        catalog = Table.read(catalog_path)

#         # Custom defined filters
#         if cat_type == "obs":
#             mask = (catalog["prefix"].data != "D") &\
#                    (~catalog["M1"].data.mask) &\
#                    (~catalog["K1"].data.mask)
#             catalog = catalog[mask]

        return catalog


    def update(self, cat_type=CATALOG_TYPE, verbose=False):
        """
        """

        self._check_cat_type_dtype(cat_type)

        if isinstance(cat_type, list):
            catalog = list()
            for cat_type_item in cat_type:
                self._update(cat_type=cat_type_item, verbose=verbose)

        else:
            self._update(cat_type=cat_type, verbose=verbose)

        return None


    def _update(self, cat_type, verbose):
        """
        """

        # Download
        payload = self._args_to_payload(cat_type)
        response = self._request(method="GET",
                                 url=self.QUERY_URL,
                                 data=payload,
                                 timeout=self.TIMEOUT,
                                 cache=False)
        # Decode
        catalog_dict = response.json()
        # Check version
        if verbose: print(f"{catalog_dict['signature']['source']} (version {catalog_dict['signature']['version']})")
        # Save
        catalog_path = os.path.join(self.CATALOG_DIR, f"comet_catalog_{cat_type}.csv")
        Table(names=catalog_dict["fields"], 
              rows=catalog_dict["data"]).write(catalog_path, overwrite=True)

        return None


    def _check_cat_type_dtype(self, cat_type):
        """
        """

        if not isinstance(cat_type, (str, list)):
            raise TypeError(f"A `str` or a `list` from {self.CATALOG_TYPE} is required.")
        elif isinstance(cat_type, str):
            if cat_type not in self.CATALOG_TYPE:
                raise ValueError(f"A `str` or a `list` from {self.CATALOG_TYPE} is required.")
            else:
                cat_type = [cat_type]
        elif isinstance(cat_type, list):
            for cat_type_item in cat_type:
                if cat_type_item not in self.CATALOG_TYPE:
                    raise ValueError(f"A `str` or a `list` from {self.CATALOG_TYPE} is required.")

        return cat_type


    def _args_to_payload(self, cat_type):
        """
        """

#         # Get all fields
#         response = self._request(method="GET",
#                                  url=self.QUERY_URL,
#                                  data={"info": "field"},
#                                  timeout=self.TIMEOUT,
#                                  cache=False)
#         fields_dict = response.json()
#         fields = ""
#         for field_type in ["object", "orbit", "phys_par"]:
#             for field in fields_dict["info"]["field"][field_type]["list"]:
#                 fields += field["name"] + ","

        payload = {
            "fields": "pdes,tp,q,e,w,om,i,M1,K1,orbit_id", #fields[:-1],
            "full-prec": 1,
            "sb-kind": "c",
        }
        
        if cat_type != "all":
            payload["sb-cdata"] = {
                "AND": ["prefix|NE|D", "M1|DF", "K1|DF"]
            }
            payload["sb-cdata"] = json.dumps(payload["sb-cdata"])

        return payload


# the default tool for users to interact with is an instance of the Class
CometCatalog = CometCatalogClass()
